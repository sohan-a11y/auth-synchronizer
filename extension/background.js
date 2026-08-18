chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "SYNC_SESSION") {
    handleSync(request.tab).then((res) => sendResponse({ success: res })).catch((err) => sendResponse({ success: false, error: err.toString() }));
    return true; // Keep message channel open for async response
  }
});

async function handleSync(tab) {
  const url = new URL(tab.url);
  const domain = url.hostname;

  // Extract cookies
  const cookies = await chrome.cookies.getAll({ domain: domain });

  // Inject script to extract localStorage and sessionStorage
  const [result] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const lStore = {};
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        lStore[k] = localStorage.getItem(k);
      }

      const sStore = {};
      for (let i = 0; i < sessionStorage.length; i++) {
        const k = sessionStorage.key(i);
        sStore[k] = sessionStorage.getItem(k);
      }

      return { localStorage: lStore, sessionStorage: sStore };
    }
  });

  const storageData = result.result;

  const authState = {
    domain: domain,
    url: tab.url,
    cookies: cookies,
    localStorage: storageData.localStorage,
    sessionStorage: storageData.sessionStorage,
    syncedAt: new Date().toISOString()
  };

  const response = await fetch("http://localhost:8000/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain: domain, state: authState })
  });

  return response.ok;
}
