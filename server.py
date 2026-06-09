from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import threading
import time

# 💡 IMPORTANTE: Asegúrate de que estos nombres coincidan con tus archivos de funciones
from tracker import check_new_chapters
from bot import notify_new_chapters

app = Flask(__name__)
CORS(app)  # permite requests desde la extensión

NU_COOKIES_FILE = "nu_cookies.json"
NOVELS_FILE = "novels.json"

def load_novels():
    if os.path.exists(NOVELS_FILE):
        with open(NOVELS_FILE, "r") as f:
            return json.load(f)
    return {"novels": []}

def save_novels(data):
    with open(NOVELS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─── RUTA HOME PARA QUE RENDER SEPA QUE EL SERVIDOR ESTÁ VIVO ───
@app.route("/")
def home():
    return "¡Bot Tracker funcionando en la nube de forma gratuita! 🤖"

# ─── ENDPOINT PARA AGREGAR NOVELAS (CON TU LÓGICA DE COOKIES) ───
@app.route("/add", methods=["POST"])
def add_novel():
    body = request.get_json()
    title = body.get("title", "").strip()
    source = body.get("source", "").strip()
    novel_id = body.get("id", "").strip()
    cookies = body.get("cookies", "")

    # Si vienen cookies de NovelUpdates, las guardamos
    if source == "novelupdates" and cookies:
        with open(NU_COOKIES_FILE, "w") as f:
            json.dump({"cookies": cookies}, f)
        print(f"  🍪 Cookies de NU guardadas con éxito")

    if not title or not novel_id:
        return jsonify({"success": False, "message": "Título o ID faltante"})

    data = load_novels()

    for n in data["novels"]:
        n_id = n.get("id") or n.get("mangadex_id") or n.get("slug", "")
        if n_id == novel_id or n["title"].lower() == title.lower():
            return jsonify({"success": False, "message": "Ya está en tu lista"})

    data["novels"].append({
        "title": title,
        "source": source,
        "id": novel_id
    })
    save_novels(data)
    return jsonify({"success": True, "message": f"'{title}' agregado 🎉"})

@app.route("/list", methods=["GET"])
def list_novels():
    data = load_novels()
    return jsonify(data)

def bot_loop():
    print("🤖 Bucle del Bot iniciado en segundo plano...", flush=True)
    time.sleep(10) # Cortesía al servidor
    
    while True:
        try:
            print("\n🔍 Chequeando capítulos nuevos desde la nube...", flush=True)
            data = load_novels()
            
            # 1. Tu tracker busca si hay novedades
            new_chapters = check_new_chapters(data["novels"])
            
            # 2. Le pasamos la lista DIRECTAMENTE a tu función original del bot
            notify_new_chapters(new_chapters)
                
        except Exception as e:
            print(f"❌ Error en el bucle del bot: {e}", flush=True)
        
        print("🤖 Esperando 2 horas para el siguiente chequeo...", flush=True)
        time.sleep(7200)

# Lanzamos el bot en un hilo secundario (Background Thread) para que no bloquee a Flask
bot_thread = threading.Thread(target=bot_loop, daemon=True)
bot_thread.start()

# ─── CONFIGURACIÓN DE ARRANQUE PARA RENDER ───
if __name__ == "__main__":
    # Render inyecta dinámicamente el puerto en la variable de entorno PORT. 
    # Dejamos 5001 como plan de respaldo por si lo corres en tu Mac.
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False) # Debug en False es vital para evitar que el hilo se ejecute dos veces