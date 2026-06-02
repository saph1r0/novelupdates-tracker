const SERVER = "https://novel-tracker-bot.onrender.com";

document.addEventListener("DOMContentLoaded", async () => {
  const content = document.getElementById("content");

  // Obtener tab activa
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Verificar si es un sitio soportado
  const supported = ["novelupdates.com/series", "mangadex.org/title", "comix.to"];
  const isSupported = supported.some(s => tab.url.includes(s));

  if (!isSupported) {
    content.innerHTML = `<div class="not-supported">Abre una página de<br>NovelUpdates, MangaDex o Comix.to</div>`;
    return;
  }

  // Ejecutar content script para obtener info
  let info;
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
        func: () => {
        const url = window.location.href;
        let data = { title: null, source: "unknown", id: null };

        if (url.includes("mangadex.org/title/")) {
            const match = url.match(/mangadex\.org\/title\/([a-f0-9-]{36})/);
            data.source = "mangadex";
            data.id = match ? match[1] : null;
            const el = document.querySelector("span.title") 
                    || document.querySelector("h1") 
                    || document.querySelector(".manga-title");
            data.title = el ? el.innerText.trim() : document.title.split("|")[0].trim();
        }
        else if (url.includes("novelupdates.com/series/")) {
            const match = url.match(/novelupdates\.com\/series\/([^/?#]+)/);
            data.source = "novelupdates";
            data.id = match ? match[1] : null;

            // Prueba selectores en orden, ignora textos de botones UI
            const candidates = [
            ".seriesnameheader",
            "h1.seriestitle",
            ".series-title",
            "h1"
            ];
            const blocked = ["insert", "edit link", "toolbar", "format"];
            
            for (const sel of candidates) {
            const el = document.querySelector(sel);
            if (!el) continue;
            const text = el.innerText.trim();
            const isUI = blocked.some(b => text.toLowerCase().includes(b));
            if (text.length > 3 && !isUI) {
                data.title = text;
                break;
            }
            }

            // Fallback: título de la pestaña limpio
            if (!data.title) {
            data.title = document.title
                .replace(/[-–|]\s*(Novel Updates|NovelUpdates).*$/i, "")
                .trim();
            }
        }
        else if (url.includes("comix.to")) {
            data.source = "comix";
            // Usa el slug de la URL como ID, no la URL entera
            const match = url.match(/comix\.to\/title\/([^/?#]+)/);
            data.id = match ? match[1] : url;
            const candidates = ["h1.series-name", ".comic-title", "h1"];
            for (const sel of candidates) {
            const el = document.querySelector(sel);
            if (el && el.innerText.trim().length > 2) {
                data.title = el.innerText.trim();
                break;
            }
            }
            if (!data.title) {
            data.title = document.title.split("|")[0].trim();
            }
        }
        return data;
        }
    });
    info = results[0].result;
  } catch (e) {
    content.innerHTML = `<div class="not-supported">Error leyendo la página</div>`;
    return;
  }

  const badgeClass = info.source === "mangadex" ? "mangadex" 
                   : info.source === "novelupdates" ? "novelupdates"
                   : info.source === "comix" ? "comix" : "unknown";

  content.innerHTML = `
    <div class="info-box">
      <span class="badge ${badgeClass}">${info.source.toUpperCase()}</span>
      <span>Título detectado:</span>
      <strong>${info.title || "No detectado"}</strong>
      <span style="margin-top:6px;display:block">ID:</span>
      <strong style="font-size:0.7rem;word-break:break-all">${info.id || "—"}</strong>
    </div>
    <button id="addBtn" ${!info.title || !info.id ? "disabled" : ""}>
      ➕ Agregar al tracker
    </button>
    <div id="status"></div>
  `;

  document.getElementById("addBtn")?.addEventListener("click", async () => {
    const btn = document.getElementById("addBtn");
    const status = document.getElementById("status");
    btn.disabled = true;
    btn.textContent = "Agregando...";

    try {
        // Obtener cookies de NovelUpdates desde el browser
      const nuCookies = await chrome.cookies.getAll({ domain: "novelupdates.com" });
      const cookieString = nuCookies.map(c => `${c.name}=${c.value}`).join("; ");
      const res = await fetch(`${SERVER}/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: info.title, source: info.source, id: info.id,cookies: cookieString })
      });
      const data = await res.json();

      if (data.success) {
        status.className = "success";
        status.textContent = `✅ ${data.message}`;
        btn.textContent = "✓ Agregado";
      } else {
        status.className = "error";
        status.textContent = `❌ ${data.message}`;
        btn.disabled = false;
        btn.textContent = "➕ Agregar al tracker";
      }
    } catch (e) {
      status.className = "error";
      status.textContent = "❌ Bot server no está corriendo";
      btn.disabled = false;
      btn.textContent = "➕ Agregar al tracker";
    }
  });
});