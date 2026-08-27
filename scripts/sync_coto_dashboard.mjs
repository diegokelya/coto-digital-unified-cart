#!/usr/bin/env node
/**
 * Sincronizador de dashboard de Coto Digital en Home Assistant
 * Lee el carrito de SQLite y actualiza el dashboard vía WebSocket
 */

import { createRequire } from 'module';
import { WebSocket } from 'ws';

const require = createRequire(import.meta.url);
const Database = require('better-sqlite3');

// Configuración
const HA_URL = process.env.HASS_URL || 'http://homeassistant.local:8123';
const HA_TOKEN = process.env.HASS_TOKEN;
const DB_PATH = process.env.HOME + '/.hermes/data/coto_carrito.db';
const DASHBOARD_URL_PATH = 'pedido-coto';
const CHAT_ID = process.env.COTO_TELEGRAM_CHAT_ID || null;

if (!HA_TOKEN) {
  console.error('❌ HASS_TOKEN no configurado');
  process.exit(1);
}

if (!CHAT_ID) {
  console.warn('⚠️ COTO_TELEGRAM_CHAT_ID no configurado — mostrará productos de TODOS los usuarios');
}

// Leer carrito de SQLite
function leerCarrito() {
  try {
    const db = new Database(DB_PATH, { readonly: true });
    
    // Usar CHAT_ID si está configurado, sino 'default'
    const userId = CHAT_ID || 'default';
    
    const productos = db.prepare(`
      SELECT 
        id,
        producto_nombre,
        producto_url,
        producto_imagen,
        precio,
        cantidad,
        added_at
      FROM carrito
      WHERE user_id = ?
      ORDER BY added_at DESC
    `).all(userId);
    
    db.close();
    
    return productos;
  } catch (err) {
    console.error('Error leyendo BD:', err.message);
    return [];
  }
}

// Generar un único panel: búsqueda y carrito viven en la misma tabla interactiva.
function generarDashboard(productos) {
  return [{
    type: 'iframe',
    url: 'http://homeassistant.local:8766/',
    aspect_ratio: '150%'
  }];
}

// Actualizar dashboard en Home Assistant vía WebSocket
async function actualizarDashboard(cards) {
  return new Promise((resolve, reject) => {
    const wsUrl = HA_URL.replace('http', 'ws') + '/api/websocket';
    const ws = new WebSocket(wsUrl);
    
    let msgId = 1;
    let autenticado = false;
    
    ws.on('open', () => {
      console.log('Conectado a Home Assistant WebSocket');
    });
    
    ws.on('message', (data) => {
      const msg = JSON.parse(data.toString());
      
      // Autenticación
      if (msg.type === 'auth_required') {
        ws.send(JSON.stringify({
          type: 'auth',
          access_token: HA_TOKEN
        }));
        return;
      }
      
      if (msg.type === 'auth_ok') {
        autenticado = true;
        console.log('✓ Autenticado en HA');
        
        // Primero intentar obtener el dashboard existente
        ws.send(JSON.stringify({
          id: msgId++,
          type: 'lovelace/config',
          url_path: DASHBOARD_URL_PATH
        }));
        
        return;
      }
      
      // Respuesta de obtención de config
      if (msg.id === 1 && msg.type === 'result') {
        const dashboardConfig = {
          title: 'Pedido Coto Digital',
          icon: 'mdi:cart',
          views: [{
            title: 'Carrito',
            path: 'carrito',
            icon: 'mdi:cart',
            badges: [],
            cards: cards
          }]
        };
        
        if (msg.success) {
          // Dashboard existe, actualizar
          console.log('Dashboard existe, actualizando...');
          ws.send(JSON.stringify({
            id: msgId++,
            type: 'lovelace/config/save',
            url_path: DASHBOARD_URL_PATH,
            config: dashboardConfig
          }));
        } else {
          // Dashboard no existe, crear
          console.log('Dashboard no existe, creando...');
          ws.send(JSON.stringify({
            id: msgId++,
            type: 'lovelace/dashboards/create',
            url_path: DASHBOARD_URL_PATH,
            title: 'Pedido Coto Digital',
            icon: 'mdi:cart',
            require_admin: false,
            show_in_sidebar: true
          }));
        }
        
        return;
      }
      
      // Respuesta de creación de dashboard
      if (msg.id === 2 && msg.type === 'result' && !msg.success && msg.error?.code === 'already_exists') {
        // Si falla porque ya existe, intentar actualizar directamente
        console.log('Dashboard ya existe, intentando actualizar...');
        
        const dashboardConfig = {
          title: 'Pedido Coto Digital',
          icon: 'mdi:cart',
          views: [{
            title: 'Carrito',
            path: 'carrito',
            icon: 'mdi:cart',
            badges: [],
            cards: cards
          }]
        };
        
        ws.send(JSON.stringify({
          id: msgId++,
          type: 'lovelace/config/save',
          url_path: DASHBOARD_URL_PATH,
          config: dashboardConfig
        }));
        
        return;
      }
      
      // Respuesta de creación exitosa
      if (msg.id === 2 && msg.type === 'result' && msg.success) {
        // Dashboard creado, ahora guardar config
        console.log('Dashboard creado, guardando configuración...');
        
        const dashboardConfig = {
          title: 'Pedido Coto Digital',
          icon: 'mdi:cart',
          views: [{
            title: 'Carrito',
            path: 'carrito',
            icon: 'mdi:cart',
            badges: [],
            cards: cards
          }]
        };
        
        ws.send(JSON.stringify({
          id: msgId++,
          type: 'lovelace/config/save',
          url_path: DASHBOARD_URL_PATH,
          config: dashboardConfig
        }));
        
        return;
      }
      
      // Respuesta final de save
      if (msg.id >= 2 && msg.type === 'result') {
        if (msg.success) {
          console.log(`✓ Dashboard actualizado: http://homeassistant.local:8123/${DASHBOARD_URL_PATH}/carrito`);
          console.log(JSON.stringify({
            updated: true,
            cards: cards.length,
            unified_table: true,
            url: `http://homeassistant.local:8123/${DASHBOARD_URL_PATH}/carrito`
          }));
          ws.close();
          resolve();
        } else {
          console.error('Error actualizando dashboard:', msg.error);
          ws.close();
          reject(new Error(msg.error?.message || 'Error desconocido'));
        }
      }
    });
    
    ws.on('error', (err) => {
      console.error('Error WebSocket:', err.message);
      reject(err);
    });
    
    ws.on('close', () => {
      if (!autenticado) {
        reject(new Error('Conexión cerrada antes de autenticar'));
      }
    });
  });
}

// Main
(async () => {
  console.log('=== Sincronizando dashboard de Coto Digital ===');
  
  const productos = leerCarrito();
  console.log(`Productos en carrito: ${productos.length}`);
  
  const cards = generarDashboard(productos);
  console.log(`Tarjetas generadas: ${cards.length}`);
  
  await actualizarDashboard(cards);
  
  console.log('✓ Sincronización completada');
})();
