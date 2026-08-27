#!/usr/bin/env node
import { WebSocket } from 'ws';

const haUrl = process.env.HASS_URL || 'http://homeassistant.local:8123';
const token = process.env.HASS_TOKEN;
if (!token) throw new Error('HASS_TOKEN no configurado');

const ws = new WebSocket(haUrl.replace(/^http/, 'ws') + '/api/websocket');
let nextId = 1;
let listId;
let configId;
let timer = setTimeout(() => {
  console.error('Timeout verificando dashboard');
  process.exit(1);
}, 15000);

ws.on('message', raw => {
  const msg = JSON.parse(raw.toString());
  if (msg.type === 'auth_required') {
    ws.send(JSON.stringify({ type: 'auth', access_token: token }));
    return;
  }
  if (msg.type === 'auth_invalid') throw new Error('Autenticación HA inválida');
  if (msg.type === 'auth_ok') {
    listId = nextId++;
    ws.send(JSON.stringify({ id: listId, type: 'lovelace/dashboards/list' }));
    return;
  }
  if (msg.id === listId) {
    if (!msg.success) throw new Error(JSON.stringify(msg.error));
    const dashboard = msg.result.find(d => d.url_path === 'pedido-coto');
    if (!dashboard) throw new Error('Dashboard pedido-coto no encontrado');
    configId = nextId++;
    ws.send(JSON.stringify({ id: configId, type: 'lovelace/config', url_path: 'pedido-coto' }));
    return;
  }
  if (msg.id === configId) {
    if (!msg.success) throw new Error(JSON.stringify(msg.error));
    const views = msg.result.views || [];
    const cards = views.flatMap(v => v.cards || []);
    const iframe = cards.find(c => c.type === 'iframe');
    const expectedImage = process.env.EXPECTED_IMAGE_URL || null;
    const markdown = cards.filter(c => c.type === 'markdown').map(c => c.content || '').join('\n');
    const result = {
      dashboard: 'pedido-coto',
      views: views.length,
      cards: cards.length,
      iframe_url: iframe?.url || null,
      interactive: iframe?.url === 'http://192.168.68.118:8766/',
      expected_image_present: expectedImage ? markdown.includes(expectedImage) : null
    };
    console.log(JSON.stringify(result));
    clearTimeout(timer);
    ws.close();
    const verified = result.interactive && (!expectedImage || result.expected_image_present);
    process.exit(verified ? 0 : 1);
  }
});

ws.on('error', err => {
  console.error(err.message);
  process.exit(1);
});
