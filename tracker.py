import requests
from bs4 import BeautifulSoup
import json
import os

SEEN_FILE = "seen_chapters.json"
MANGADEX_API = "https://api.mangadex.org"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=2)

# ─────────────────────────────────────────
# MANGADEX
# ─────────────────────────────────────────
def get_chapter_mangadex(manga_id, lang="en"):
    try:
        res = requests.get(
            f"{MANGADEX_API}/chapter",
            params={
                "manga": manga_id,
                "translatedLanguage[]": lang,
                "order[publishAt]": "desc",
                "limit": 1,
            },
            timeout=10
        )
        data = res.json()
        chapters = data.get("data", [])
        if not chapters:
            return None, None

        ch = chapters[0]["attributes"]
        chapter_num = ch.get("chapter") or "Oneshot"
        title = ch.get("title") or ""
        ch_id = chapters[0]["id"]
        display = f"Chapter {chapter_num}" + (f" — {title}" if title else "")
        url = f"https://mangadex.org/chapter/{ch_id}"
        return display, url

    except Exception as e:
        print(f"  Error MangaDex: {e}")
        return None, None

# ─────────────────────────────────────────
# NOVELUPDATES — via página de grupos de traducción
# ─────────────────────────────────────────
def get_chapter_novelupdates(slug):
    cookies_file = "nu_cookies.json"
    saved_cookies = ""
    
    if os.path.exists(cookies_file):
        with open(cookies_file, "r") as f:
            saved_cookies = json.load(f).get("cookies", "")
    else:
        print(f"  ⚠️  Sin cookies — agrega una novela desde la extensión estando logueada")
        return None, None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": saved_cookies,
            "Referer": "https://www.novelupdates.com/",
        }
        res = requests.get(
            f"https://www.novelupdates.com/series/{slug}/",
            headers=headers,
            timeout=15
        )
        
        print(f"  NU status: {res.status_code} | {len(res.text)} bytes")
        soup = BeautifulSoup(res.text, "html.parser")

        for selector in ["a.chp-release", "li.sp_li_chp a", "#myTable a"]:
            items = soup.select(selector)
            if items:
                first = items[0]
                return first.text.strip(), first.get("href", "")

        # Debug: muestra qué llegó si no encuentra capítulos
        title_tag = soup.select_one(".seriesnameheader")
        if title_tag:
            print(f"  Página OK — serie encontrada: {title_tag.text.strip()}")
            print(f"  Pero sin capítulos visibles (pueden requerir JS)")
        else:
            print(f"  ⚠️  Página no reconocida — posible bloqueo o redirección")

        return None, None

    except Exception as e:
        print(f"  Error NU: {e}")
        return None, None
    
def get_chapter_nu_fallback(slug):
    """
    Fallback: scrapea la página de la serie directamente
    con headers más agresivos.
    """
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        })

        # Primero visita la home para conseguir cookies
        session.get("https://www.novelupdates.com/", timeout=10)

        res = session.get(
            f"https://www.novelupdates.com/series/{slug}/",
            timeout=15
        )
        soup = BeautifulSoup(res.text, "html.parser")

        # Intenta varios selectores
        for selector in ["a.chp-release", "li.sp_li_chp a", "#myTable a"]:
            items = soup.select(selector)
            if items:
                first = items[0]
                return first.text.strip(), first.get("href", "")

        # Último recurso: busca cualquier link que parezca capítulo
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "chapter" in href.lower() or "ch-" in href.lower():
                return a.text.strip(), href

        print(f"  ⚠️  NovelUpdates sigue bloqueando para: {slug}")
        return None, None

    except Exception as e:
        print(f"  Error NU fallback: {e}")
        return None, None

# ─────────────────────────────────────────
# COMIX.TO — scraping básico
# ─────────────────────────────────────────
def get_chapter_comix(novel_id):
    # Reconstruye la URL si solo tiene el slug
    if novel_id.startswith("http"):
        url = novel_id
    else:
        url = f"https://comix.to/title/{novel_id}"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for selector in [".chapter-item a", ".chapters-list a", "ul.row-content-chapter li a"]:
            items = soup.select(selector)
            if items:
                return items[0].text.strip(), items[0].get("href", "")
        return None, None
    except Exception as e:
        print(f"  Error Comix: {e}")
        return None, None

# ─────────────────────────────────────────
# DISPATCHER PRINCIPAL
# ─────────────────────────────────────────
def get_latest_chapter(novel):
    """Enruta al scraper correcto según el campo 'source'."""
    source = novel.get("source", "mangadex")
    novel_id = novel.get("id") or novel.get("mangadex_id") or novel.get("slug", "")

    if source == "mangadex":
        return get_chapter_mangadex(novel_id)
    elif source == "novelupdates":
        return get_chapter_novelupdates(novel_id)
    elif source == "comix":
        return get_chapter_comix(novel_id)
    else:
        print(f"  ⚠️  Source desconocido: {source}")
        return None, None

# ─────────────────────────────────────────
# CHECK PRINCIPAL
# ─────────────────────────────────────────
def check_new_chapters(novels):
    seen = load_seen()
    new_chapters = []

    for novel in novels:
        title = novel["title"]
        source = novel.get("source", "mangadex")

        print(f"  [{source.upper()}] Chequeando: {title}...")
        chapter_name, chapter_url = get_latest_chapter(novel)

        if not chapter_name:
            print(f"  ⚠️  Sin datos para {title}")
            continue

        last_seen = seen.get(title)

        if last_seen != chapter_name:
            new_chapters.append({
                "title": title,
                "chapter": chapter_name,
                "url": chapter_url
            })
            seen[title] = chapter_name
            print(f"  ✨ NUEVO: {chapter_name}")
        else:
            print(f"  ✓ Sin novedad ({chapter_name})")

    save_seen(seen)
    return new_chapters