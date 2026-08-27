const MAX_AGE_MS = 10 * 60 * 1000;
const WAIT_MS = 350;

function send(message) {
  chrome.runtime.sendMessage(message).catch(() => {});
}

function createOverlay(items) {
  const host = document.createElement('div');
  host.id = 'hermes-coto-loader';
  host.innerHTML = `
    <style>
      #hermes-coto-loader{position:fixed;top:20px;right:20px;z-index:2147483647;width:360px;background:#1f2937;color:#fff;border:2px solid #22c55e;border-radius:12px;padding:16px;font:14px Arial,sans-serif;box-shadow:0 8px 30px #0008}
      #hermes-coto-loader h3{margin:0 0 8px;color:#86efac}#hermes-coto-loader p{margin:8px 0}
      #hermes-coto-loader progress{width:100%}#hermes-coto-loader ul{max-height:260px;overflow:auto;padding-left:20px}
      #hermes-coto-loader li.ok{color:#86efac}#hermes-coto-loader li.error{color:#fca5a5}
      #hermes-coto-loader button{padding:8px 12px;border:0;border-radius:6px;background:#22c55e;color:#052e16;font-weight:bold;cursor:pointer}
    </style>
    <h3>Hermes → Coto Digital</h3><p class="status">Preparando carrito…</p>
    <progress value="0" max="${items.length}"></progress><ul></ul><div class="actions"></div>`;
  document.documentElement.appendChild(host);
  const list = host.querySelector('ul');
  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = `${item.name} × ${item.cantidad}`;
    list.appendChild(li);
  }
  return host;
}

async function cotoJson(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'include',
    ...options,
    headers: { accept: 'application/json, text/plain, */*', ...(options.headers || {}) },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function sessionToken() {
  const data = await cotoJson('/rest/model/atg/rest/SessionConfirmationActor/getSessionConfirmationNumber');
  const token = data?.sessionConfirmationNumber ?? data?._dynSessConf ?? data?.dynSessConf;
  if (token == null) throw new Error('Coto no entregó el token de sesión');
  return String(token);
}

async function addItem(item, token) {
  const path = `/rest/model/atg/actors/cCarritoActor/addOrRemoveItemToOrderV2?pushSite=CotoDigital&_dynSessConf=${encodeURIComponent(token)}`;
  const result = await cotoJson(path, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'cache-control': 'no-cache' },
    body: JSON.stringify({
      skuId: `sku${item.sku}`,
      quantity: Number(item.cantidad),
      prodId: `prod${item.sku}`,
      sucPickUp: null,
      cambiaSuc: 'true',
    }),
  });
  if (!result || String(result.codigoError) !== '0') {
    throw new Error(result?.mensajeError || 'Coto rechazó el producto');
  }
}

async function run(items) {
  const overlay = createOverlay(items);
  const status = overlay.querySelector('.status');
  const progress = overlay.querySelector('progress');
  const rows = [...overlay.querySelectorAll('li')];
  let ok = 0;
  let fail = 0;

  try {
    const token = await sessionToken();
    await chrome.runtime.sendMessage({ type: 'MARK_CONSUMED' });
    for (let index = 0; index < items.length; index++) {
      status.textContent = `Agregando ${index + 1} de ${items.length}: ${items[index].name}`;
      try {
        await addItem(items[index], token);
        rows[index].className = 'ok'; rows[index].textContent = `✓ ${rows[index].textContent}`; ok++;
      } catch (error) {
        rows[index].className = 'error'; rows[index].textContent = `✗ ${rows[index].textContent} — ${error.message}`; fail++;
      }
      progress.value = index + 1;
      send({ type: 'COTO_PROGRESS', done: index + 1, total: items.length, ok, fail });
      await new Promise((resolve) => setTimeout(resolve, WAIT_MS));
    }
    status.textContent = `Terminado: ${ok} agregados, ${fail} con error.`;
    const button = document.createElement('button');
    button.textContent = 'Recargar y ver carrito';
    button.onclick = () => location.href = '/carrito';
    overlay.querySelector('.actions').appendChild(button);
    send({ type: 'COTO_DONE', total: items.length, ok, fail });
  } catch (error) {
    status.textContent = `No se pudo iniciar la carga: ${error.message}`;
    send({ type: 'COTO_ERROR', error: error.message });
  }
}

(async () => {
  const pending = await chrome.runtime.sendMessage({ type: 'GET_PENDING' }).catch(() => null);
  if (!pending || pending.consumed || !Array.isArray(pending.items) || !pending.items.length) return;
  if (Date.now() - pending.createdAt > MAX_AGE_MS) return;
  run(pending.items);
})();
