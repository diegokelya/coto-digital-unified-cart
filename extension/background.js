const COTO_URL = 'https://www.coto.com.ar/';

chrome.runtime.onMessage.addListener((message, sender, respond) => {
  if (!message || typeof message.type !== 'string') return;

  if (message.type === 'EXPORT_COTO') {
    const pendingCart = {
      items: message.items,
      sourceTabId: sender.tab?.id ?? null,
      createdAt: Date.now(),
      consumed: false,
    };
    chrome.storage.session.set({ pendingCart })
      .then(() => chrome.tabs.create({ url: COTO_URL }))
      .then(() => respond({ ok: true }))
      .catch((error) => respond({ ok: false, error: String(error) }));
    return true;
  }

  if (message.type === 'GET_PENDING') {
    chrome.storage.session.get('pendingCart')
      .then(({ pendingCart }) => respond(pendingCart ?? null));
    return true;
  }

  if (message.type === 'MARK_CONSUMED') {
    chrome.storage.session.get('pendingCart').then(({ pendingCart }) => {
      if (pendingCart) chrome.storage.session.set({ pendingCart: { ...pendingCart, consumed: true } });
      respond({ ok: true });
    });
    return true;
  }

  if (message.type.startsWith('COTO_')) {
    chrome.storage.session.get('pendingCart').then(({ pendingCart }) => {
      if (pendingCart?.sourceTabId != null) {
        chrome.tabs.sendMessage(pendingCart.sourceTabId, message).catch(() => {});
      }
      if (message.type === 'COTO_DONE' && message.fail === 0) {
        chrome.storage.session.remove('pendingCart');
      }
    });
  }
});
