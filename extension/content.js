function extractNovelInfo() {
  const url = window.location.href;
  let info = { title: null, source: null, id: null, url: url };

  // --- MangaDex ---
  if (url.includes("mangadex.org/title/")) {
    const match = url.match(/mangadex\.org\/title\/([a-f0-9-]{36})/);
    info.source = "mangadex";
    info.id = match ? match[1] : null;
    // Título desde el h1 de la página
    const h1 = document.querySelector("h1.title");
    info.title = h1 ? h1.innerText.trim() : document.title.split("|")[0].trim();
  }

  // --- NovelUpdates ---
  else if (url.includes("novelupdates.com/series/")) {
    const match = url.match(/novelupdates\.com\/series\/([^/]+)/);
    info.source = "novelupdates";
    info.id = match ? match[1] : null; // el slug
    const h1 = document.querySelector(".seriesnameheader");
    info.title = h1 ? h1.innerText.trim() : document.title.split("|")[0].trim();
  }

  // --- Comix.to ---
  else if (url.includes("comix.to")) {
    info.source = "comix";
    info.id = url;
    info.title = document.querySelector("h1")?.innerText.trim() 
                 || document.title.split("|")[0].trim();
  }

  return info;
}

// Escucha mensajes del popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getNovelInfo") {
    sendResponse(extractNovelInfo());
  }
});