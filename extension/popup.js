document.getElementById("syncBtn").addEventListener("click", async () => {
  const statusDiv = document.getElementById("status");
  statusDiv.textContent = "Syncing...";
  
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    statusDiv.textContent = "No active tab.";
    return;
  }

  chrome.runtime.sendMessage({ action: "SYNC_SESSION", tab: tab }, (response) => {
    if (response && response.success) {
      statusDiv.textContent = "Session Synced Successfully!";
    } else {
      statusDiv.textContent = "Failed to sync session.";
    }
  });
});
