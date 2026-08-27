const VERSION = chrome.runtime.getManifest().version;
document.documentElement.dataset.hermesCotoExtension = VERSION;

window.addEventListener('message', (event) => {
  if (event.source !== window || !event.data || event.data.source !== 'hermes-coto-dashboard') return;
  if (event.data.type !== 'EXPORT_COTO' || !Array.isArray(event.data.items)) return;

  const items = event.data.items
    .filter((item) => /^\d{8}$/.test(String(item.sku || '')))
    .map((item) => ({
      sku: String(item.sku),
      cantidad: Math.max(1, Math.min(99, Number(item.cantidad) || 1)),
      name: String(item.name || `SKU ${item.sku}`).slice(0, 200),
    }));

  chrome.runtime.sendMessage({ type: 'EXPORT_COTO', items })
    .then((result) => window.postMessage({
      source: 'hermes-coto-extension',
      type: result?.ok ? 'COTO_QUEUED' : 'COTO_ERROR',
      error: result?.error,
    }, '*'))
    .catch((error) => window.postMessage({
      source: 'hermes-coto-extension', type: 'COTO_ERROR', error: String(error),
    }, '*'));
});

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type?.startsWith('COTO_')) {
    window.postMessage({ source: 'hermes-coto-extension', ...message }, '*');
  }
});
