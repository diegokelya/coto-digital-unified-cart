#!/usr/bin/env python3
"""
Servidor web local para gestionar el carrito de Coto Digital desde Home Assistant
Puerto: 8766
"""

import os
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
import html
import re
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Configuración
DB_PATH = os.path.expanduser("~/.hermes/data/coto_carrito.db")
USER_ID = os.getenv("COTO_TELEGRAM_CHAT_ID", "406287065")
PORT = 8766
COTO_API_URL = "https://www.cotodigital3.com.ar/sitios/cdigi/browse/search"
EXTENSION_ZIP = Path.home() / ".hermes" / "exports" / "hermes-coto-loader.zip"

# Caché de resultados de búsqueda (persistente en memoria del servidor)
search_cache = {}

# =============================================================================
# Base de datos
# =============================================================================

def get_db():
    """Obtener conexión a BD con timeout y WAL mode."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Migrar el esquema sin perder los productos existentes."""
    conn = get_db()
    columnas = {row[1] for row in conn.execute("PRAGMA table_info(carrito)")}
    if 'producto_imagen' not in columnas:
        conn.execute("ALTER TABLE carrito ADD COLUMN producto_imagen TEXT")
    conn.commit()
    conn.close()


def get_carrito():
    """Obtener productos del carrito."""
    conn = get_db()
    rows = conn.execute("""
        SELECT id, producto_nombre, producto_url, producto_imagen, precio, cantidad, added_at
        FROM carrito
        WHERE user_id = ?
        ORDER BY added_at DESC
    """, (USER_ID,)).fetchall()
    conn.close()
    
    productos = []
    for row in rows:
        productos.append({
            'id': row['id'],
            'nombre': row['producto_nombre'],
            'url': row['producto_url'],
            'imagen': row['producto_imagen'],
            'precio': row['precio'],
            'cantidad': row['cantidad'],
            'agregado': row['added_at']
        })
    
    return productos


def exportar_carrito_coto():
    """Separar productos automáticos de los que requieren carga manual."""
    cargables = []
    manuales = []
    for producto in get_carrito():
        match = re.search(r'prod(\d{8})', producto.get('url') or '')
        item = {
            'name': producto['nombre'],
            'cantidad': producto['cantidad'],
            'precio': producto['precio'],
            'url': producto.get('url'),
        }
        if match:
            item['sku'] = match.group(1)
            cargables.append(item)
        else:
            manuales.append(item)
    return {'items': cargables, 'manuales': manuales, 'total': len(cargables) + len(manuales)}


def generar_lista_texto():
    exportacion = exportar_carrito_coto()
    lineas = ['LISTA PARA COTO DIGITAL', '']
    for item in exportacion['items'] + exportacion['manuales']:
        lineas.append(f"{item['cantidad']} x {item['name']} — ${item['precio']:.2f}")
        if item.get('url'):
            lineas.append(item['url'])
        lineas.append('')
    lineas.append(f"Productos: {exportacion['total']}")
    return '\n'.join(lineas)


def agregar_al_carrito(nombre, precio, cantidad=1, url=None, imagen=None):
    """Agregar producto al carrito."""
    conn = get_db()
    conn.execute("""
        INSERT INTO carrito
            (user_id, producto_nombre, producto_url, producto_imagen, precio, cantidad, added_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (USER_ID, nombre, url, imagen, precio, cantidad, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    # Sincronizar dashboard
    sincronizar_dashboard()


def eliminar_del_carrito(item_id):
    """Eliminar producto del carrito."""
    conn = get_db()
    conn.execute("DELETE FROM carrito WHERE id = ? AND user_id = ?", (item_id, USER_ID))
    conn.commit()
    conn.close()
    
    # Sincronizar dashboard
    sincronizar_dashboard()


def vaciar_carrito():
    """Vaciar carrito completo."""
    conn = get_db()
    conn.execute("DELETE FROM carrito WHERE user_id = ?", (USER_ID,))
    conn.commit()
    conn.close()
    
    # Sincronizar dashboard
    sincronizar_dashboard()


def sincronizar_dashboard():
    """Sincronizar dashboard de Home Assistant."""
    try:
        import subprocess
        subprocess.run(
            ['/home/diego/.hermes/scripts/sync_coto_dashboard.sh'],
            capture_output=True,
            timeout=30
        )
    except:
        pass


# =============================================================================
# API de Coto Digital
# =============================================================================

def buscar_productos_coto(query, limit=10):
    """Buscar productos en la API JSON de Coto Digital."""
    url = f"{COTO_API_URL}?Ntt={urllib.parse.quote(query)}&format=json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.cotodigital3.com.ar'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        productos = []
        productos_ids = set()

        def primero(value, default=None):
            if isinstance(value, list):
                return value[0] if value else default
            return value if value is not None else default

        def extraer_recursivo(obj):
            if len(productos) >= limit:
                return
            if isinstance(obj, dict):
                if 'records' in obj and isinstance(obj['records'], list):
                    for record in obj['records']:
                        if not isinstance(record, dict):
                            continue
                        for sub_record in (record.get('records') or []):
                            if not isinstance(sub_record, dict):
                                continue
                            attrs = sub_record.get('attributes')
                            if not isinstance(attrs, dict):
                                continue

                            producto_id = primero(attrs.get('product.repositoryId'))
                            nombre = primero(attrs.get('product.displayName'))
                            precio_raw = primero(attrs.get('sku.activePrice'), 0)
                            imagen = primero(attrs.get('product.mediumImage.url'))

                            if not producto_id or not nombre:
                                continue
                            producto_id = str(producto_id)
                            if producto_id in productos_ids:
                                continue
                            try:
                                precio = float(precio_raw or 0)
                            except (TypeError, ValueError):
                                precio = 0.0

                            productos_ids.add(producto_id)
                            productos.append({
                                'id': producto_id,
                                'nombre': str(nombre).strip(),
                                'precio': precio,
                                'url': f"https://www.cotodigital3.com.ar/sitios/cdigi/producto/{producto_id}",
                                'imagen': str(imagen).strip() if imagen else None
                            })
                            if len(productos) >= limit:
                                return

                for valor in obj.values():
                    extraer_recursivo(valor)
                    if len(productos) >= limit:
                        return
            elif isinstance(obj, list):
                for item in obj:
                    extraer_recursivo(item)
                    if len(productos) >= limit:
                        return

        extraer_recursivo(data)
        return productos[:limit]

    except Exception as e:
        print(f"Error buscando productos: {e}", flush=True)
        return []


# =============================================================================
# Servidor HTTP
# =============================================================================

class CotoDashboardHandler(BaseHTTPRequestHandler):
    """Handler para peticiones HTTP."""
    
    def log_message(self, format, *args):
        """Logging personalizado."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")
    
    def send_json(self, data, status=200):
        """Enviar respuesta JSON."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html(self, html_content):
        """Enviar respuesta HTML."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode())

    def send_bytes(self, content, content_type, filename=None):
        """Enviar archivos o texto descargable."""
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(content)
    
    def do_GET(self):
        """Manejar peticiones GET."""
        path = self.path.split('?')[0]
        
        # Página principal
        if path == '/' or path == '/index.html':
            self.send_html(get_html_interface())
        
        # API: Obtener carrito
        elif path == '/api/cart':
            productos = get_carrito()
            total = sum(p['precio'] * p['cantidad'] for p in productos)
            self.send_json({'productos': productos, 'total': total})

        elif path == '/api/export/coto':
            self.send_json(exportar_carrito_coto())

        elif path == '/api/export/lista.txt':
            self.send_bytes(generar_lista_texto().encode('utf-8'), 'text/plain; charset=utf-8', 'carrito-coto.txt')

        elif path == '/downloads/hermes-coto-loader.zip' and EXTENSION_ZIP.exists():
            self.send_bytes(EXTENSION_ZIP.read_bytes(), 'application/zip', EXTENSION_ZIP.name)
        
        # API: Buscar productos
        elif path == '/api/search':
            query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            query = query_params.get('q', [''])[0]
            
            if not query:
                self.send_json({'error': 'Query vacío'}, 400)
                return
            
            resultados = buscar_productos_coto(query)
            
            # Guardar en caché
            search_id = str(abs(hash(query + str(datetime.now()))))
            search_cache[search_id] = resultados
            
            self.send_json({'search_id': search_id, 'resultados': resultados})
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Manejar peticiones POST."""
        path = self.path
        
        # Leer body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except:
            self.send_json({'error': 'JSON inválido'}, 400)
            return
        
        # API: Agregar desde búsqueda
        if path == '/api/cart/add':
            search_id = data.get('search_id')
            index = data.get('index')
            cantidad = int(data.get('cantidad', 1))
            
            if not search_id or index is None:
                self.send_json({'error': 'Parámetros faltantes'}, 400)
                return
            
            # Validar cantidad
            if cantidad < 1 or cantidad > 99:
                self.send_json({'error': 'Cantidad inválida'}, 400)
                return
            
            # Obtener producto del caché
            resultados = search_cache.get(search_id, [])
            if index < 0 or index >= len(resultados):
                self.send_json({'error': 'Índice inválido'}, 400)
                return
            
            producto = resultados[index]
            agregar_al_carrito(
                nombre=producto['nombre'],
                precio=producto['precio'],
                cantidad=cantidad,
                url=producto.get('url'),
                imagen=producto.get('imagen')
            )
            
            self.send_json({'success': True})
        
        # API: Agregar manualmente
        elif path == '/api/cart/manual':
            nombre = data.get('nombre', '').strip()
            precio = data.get('precio')
            cantidad = int(data.get('cantidad', 1))
            
            # Validaciones
            if not nombre:
                self.send_json({'error': 'Nombre vacío'}, 400)
                return
            
            try:
                precio = float(precio)
                if precio < 0:
                    raise ValueError()
            except:
                self.send_json({'error': 'Precio inválido'}, 400)
                return
            
            if cantidad < 1 or cantidad > 99:
                self.send_json({'error': 'Cantidad inválida'}, 400)
                return
            
            agregar_al_carrito(nombre=nombre, precio=precio, cantidad=cantidad)
            self.send_json({'success': True})
        
        # API: Vaciar carrito
        elif path == '/api/cart/clear':
            vaciar_carrito()
            self.send_json({'success': True})
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_DELETE(self):
        """Manejar peticiones DELETE."""
        # API: Eliminar producto
        if self.path.startswith('/api/cart/'):
            try:
                item_id = int(self.path.split('/')[-1])
                eliminar_del_carrito(item_id)
                self.send_json({'success': True})
            except:
                self.send_json({'error': 'ID inválido'}, 400)
        else:
            self.send_response(404)
            self.end_headers()


def get_html_interface():
    """Generar interfaz HTML."""
    return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coto Digital - Carrito</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1, h2 { color: #4CAF50; margin-bottom: 15px; }
        .section { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        input, button {
            padding: 10px;
            border: 1px solid #444;
            border-radius: 4px;
            font-size: 14px;
        }
        input {
            background: #333;
            color: #e0e0e0;
            width: 100%;
            margin-bottom: 10px;
        }
        button {
            background: #4CAF50;
            color: white;
            cursor: pointer;
            border: none;
            font-weight: 600;
        }
        button:hover { background: #45a049; }
        button.danger { background: #f44336; }
        button.danger:hover { background: #da190b; }
        button.secondary, .button-link { background: #1976D2; }
        .button-link {
            color: white;
            text-decoration: none;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            display: inline-block;
        }
        .export-actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
        .export-status { margin-bottom: 12px; color: #90caf9; }
        .grid { display: grid; grid-template-columns: 1fr 100px 100px; gap: 10px; align-items: center; }
        .product-item {
            background: #333;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .product-info { flex: 1; }
        .product-content { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; }
        .product-image {
            width: 88px;
            height: 88px;
            object-fit: contain;
            background: white;
            border-radius: 8px;
            flex: 0 0 88px;
        }
        .product-image-placeholder {
            width: 88px;
            height: 88px;
            display: grid;
            place-items: center;
            background: #444;
            border-radius: 8px;
            color: #aaa;
            font-size: 28px;
            flex: 0 0 88px;
        }
        .product-name { font-weight: 600; margin-bottom: 5px; }
        .product-price { color: #4CAF50; font-size: 18px; }
        .total {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            text-align: right;
            padding: 20px;
            background: #333;
            border-radius: 4px;
        }
        .cart-table-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid #444; }
        .cart-table { width: 100%; border-collapse: collapse; min-width: 700px; }
        .cart-table th, .cart-table td { padding: 12px; border-bottom: 1px solid #444; text-align: left; vertical-align: middle; }
        .cart-table th { background: #333; color: #a5d6a7; white-space: nowrap; }
        .cart-table tbody tr:hover { background: #303030; }
        .cart-table td.number, .cart-table th.number { text-align: right; white-space: nowrap; }
        .cart-table td.action, .cart-table th.action { text-align: center; }
        .cart-table tfoot td { background: #333; color: #4CAF50; font-size: 20px; font-weight: 700; border-bottom: 0; }
        .cart-table .product-content { min-width: 280px; }
        .cart-table .product-image, .cart-table .product-image-placeholder { width: 64px; height: 64px; flex-basis: 64px; }
        .empty { text-align: center; color: #888; padding: 40px; }
        .search-result {
            background: #333;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .loading { text-align: center; color: #888; padding: 20px; }
    </style>
</head>
<body>
    <h1>🛒 Coto Digital</h1>
    
    <!-- Búsqueda -->
    <div class="section">
        <h2>Buscar Productos</h2>
        <div class="grid">
            <input type="text" id="searchQuery" placeholder="Ej: leche, coca cola, arroz..." />
            <input type="number" id="searchQty" value="1" min="1" max="99" />
            <button onclick="buscarProductos()">Buscar</button>
        </div>
        <div id="searchResults"></div>
    </div>
    
    <!-- Agregar manual -->
    <div class="section">
        <h2>Agregar Manualmente</h2>
        <input type="text" id="manualNombre" placeholder="Nombre del producto" />
        <div class="grid">
            <input type="number" id="manualPrecio" placeholder="Precio" step="0.01" min="0" />
            <input type="number" id="manualCantidad" value="1" min="1" max="99" />
            <button onclick="agregarManual()">Agregar</button>
        </div>
    </div>
    
    <!-- Carrito -->
    <div class="section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h2>Carrito</h2>
            <div class="export-actions">
                <button class="secondary" onclick="exportarACoto()">🚀 Cargar en Coto</button>
                <a class="button-link" href="/api/export/lista.txt">📄 Descargar lista</a>
                <button class="danger" onclick="vaciarCarrito()">Vaciar Carrito</button>
            </div>
        </div>
        <div id="exportStatus" class="export-status"></div>
        <div id="cartItems"></div>
    </div>
    
    <script>
        let currentSearchId = null;
        let currentSearchResults = [];
        const SEARCH_STORAGE_KEY = 'cotoSearchState';
        
        // Restaurar primero la búsqueda porque Lovelace puede recargar el iframe.
        restaurarBusqueda();
        cargarCarrito();
        
        async function buscarProductos() {
            const query = document.getElementById('searchQuery').value.trim();
            if (!query) return alert('Ingresá un producto');
            
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '<div class="loading">Buscando...</div>';
            
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                
                if (!data.resultados || data.resultados.length === 0) {
                    resultsDiv.innerHTML = '<div class="empty">No se encontraron productos</div>';
                    return;
                }
                
                currentSearchId = data.search_id;
                currentSearchResults = data.resultados;
                const cantidad = document.getElementById('searchQty').value;

                guardarBusqueda(query, cantidad, data.resultados);
                renderResultados(data.resultados, cantidad);
            } catch (err) {
                resultsDiv.innerHTML = `<div class="empty">Error: ${err.message}</div>`;
            }
        }

        function renderResultados(resultados, cantidad) {
            document.getElementById('searchResults').innerHTML = resultados.map((p, i) => `
                    <div class="search-result">
                        <div class="product-content">
                            ${productImage(p.imagen, p.nombre)}
                            <div class="product-info">
                                <div class="product-name">${escapeHtml(p.nombre)}</div>
                                <div class="product-price">$${p.precio.toFixed(2)}</div>
                            </div>
                        </div>
                        <button onclick="agregarDesdeBusqueda(${i}, ${cantidad})">Agregar</button>
                    </div>
                `).join('');
        }

        function guardarBusqueda(query, cantidad, resultados) {
            try {
                localStorage.setItem(SEARCH_STORAGE_KEY, JSON.stringify({
                    searchId: currentSearchId,
                    query,
                    cantidad,
                    resultados
                }));
            } catch (err) {
                console.warn('No se pudo guardar la búsqueda:', err);
            }
        }

        function restaurarBusqueda() {
            try {
                const raw = localStorage.getItem(SEARCH_STORAGE_KEY);
                if (!raw) return;
                const state = JSON.parse(raw);
                if (!state.searchId || !Array.isArray(state.resultados) || state.resultados.length === 0) return;

                currentSearchId = state.searchId;
                currentSearchResults = state.resultados;
                document.getElementById('searchQuery').value = state.query || '';
                document.getElementById('searchQty').value = state.cantidad || 1;
                renderResultados(state.resultados, state.cantidad || 1);
            } catch (err) {
                console.warn('No se pudo restaurar la búsqueda:', err);
            }
        }
        
        async function agregarDesdeBusqueda(index, cantidad) {
            try {
                const res = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ search_id: currentSearchId, index, cantidad })
                });
                
                if (res.ok) {
                    cargarCarrito();
                } else {
                    alert('Error agregando producto');
                }
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
        
        async function agregarManual() {
            const nombre = document.getElementById('manualNombre').value.trim();
            const precio = parseFloat(document.getElementById('manualPrecio').value);
            const cantidad = parseInt(document.getElementById('manualCantidad').value);
            
            if (!nombre) return alert('Ingresá el nombre');
            if (isNaN(precio) || precio < 0) return alert('Precio inválido');
            if (isNaN(cantidad) || cantidad < 1) return alert('Cantidad inválida');
            
            try {
                const res = await fetch('/api/cart/manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre, precio, cantidad })
                });
                
                if (res.ok) {
                    cargarCarrito();
                    document.getElementById('manualNombre').value = '';
                    document.getElementById('manualPrecio').value = '';
                    document.getElementById('manualCantidad').value = '1';
                } else {
                    alert('Error agregando producto');
                }
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
        
        async function cargarCarrito() {
            try {
                const res = await fetch('/api/cart');
                const data = await res.json();
                
                const itemsDiv = document.getElementById('cartItems');
                const productos = data.productos || [];
                const filas = productos.length ? productos.map(p => `
                    <tr>
                        <td>
                            <div class="product-content">
                                ${productImage(p.imagen, p.nombre)}
                                <div class="product-name">${escapeHtml(p.nombre)}</div>
                            </div>
                        </td>
                        <td class="number">${p.cantidad}</td>
                        <td class="number">$${p.precio.toFixed(2)}</td>
                        <td class="number">$${(p.cantidad * p.precio).toFixed(2)}</td>
                        <td class="action"><button class="danger" onclick="eliminarProducto(${p.id})">Eliminar</button></td>
                    </tr>
                `).join('') : '<tr><td colspan="5" class="empty">Carrito vacío</td></tr>';

                itemsDiv.innerHTML = `
                    <div class="cart-table-wrap">
                        <table class="cart-table">
                            <thead><tr>
                                <th>Producto</th>
                                <th class="number">Cantidad</th>
                                <th class="number">Unitario</th>
                                <th class="number">Subtotal</th>
                                <th class="action">Acción</th>
                            </tr></thead>
                            <tbody>${filas}</tbody>
                            <tfoot><tr>
                                <td colspan="3">Total</td>
                                <td class="number">$${Number(data.total || 0).toFixed(2)}</td>
                                <td></td>
                            </tr></tfoot>
                        </table>
                    </div>`;
            } catch (err) {
                console.error('Error cargando carrito:', err);
            }
        }
        
        async function eliminarProducto(id) {
            if (!confirm('¿Eliminar este producto?')) return;
            
            try {
                const res = await fetch(`/api/cart/${id}`, { method: 'DELETE' });
                if (res.ok) cargarCarrito();
            } catch (err) {
                alert('Error eliminando producto');
            }
        }
        
        async function vaciarCarrito() {
            if (!confirm('¿Vaciar el carrito completo?')) return;
            
            try {
                const res = await fetch('/api/cart/clear', { method: 'POST' });
                if (res.ok) cargarCarrito();
            } catch (err) {
                alert('Error vaciando carrito');
            }
        }
        
        async function exportarACoto() {
            const status = document.getElementById('exportStatus');
            try {
                const res = await fetch('/api/export/coto');
                const data = await res.json();
                if (!data.total) return alert('El carrito está vacío');
                if (!data.items.length) {
                    status.textContent = 'Los productos actuales son manuales. Descargá la lista para cargarlos en Coto.';
                    return;
                }
                if (!document.documentElement.dataset.hermesCotoExtension) {
                    status.innerHTML = 'Instalá una vez el <a href="/downloads/hermes-coto-loader.zip">Cargador de Coto</a> en Chrome. Mientras tanto podés descargar la lista.';
                    return;
                }
                status.textContent = `Preparando ${data.items.length} producto(s) para Coto...`;
                window.postMessage({
                    source: 'hermes-coto-dashboard',
                    type: 'EXPORT_COTO',
                    items: data.items
                }, '*');
                if (data.manuales.length) {
                    status.textContent += ` ${data.manuales.length} producto(s) manual(es) quedan en la lista descargable.`;
                }
            } catch (err) {
                status.textContent = 'No se pudo exportar: ' + err.message;
            }
        }

        window.addEventListener('message', (event) => {
            if (event.source !== window || !event.data || event.data.source !== 'hermes-coto-extension') return;
            const status = document.getElementById('exportStatus');
            if (event.data.type === 'COTO_QUEUED') status.textContent = 'Abriendo Coto Digital para cargar el carrito...';
            if (event.data.type === 'COTO_PROGRESS') status.textContent = `Coto: ${event.data.done}/${event.data.total} procesados`;
            if (event.data.type === 'COTO_DONE') status.textContent = `Listo: ${event.data.ok} agregados, ${event.data.fail} con error.`;
            if (event.data.type === 'COTO_ERROR') status.textContent = 'Error al cargar en Coto: ' + event.data.error;
        });
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function productImage(url, name) {
            if (!url || !url.startsWith('https://static.cotodigital3.com.ar/')) {
                return '<div class="product-image-placeholder">📦</div>';
            }
            const safeUrl = escapeHtml(url).replace(/"/g, '&quot;');
            const safeName = escapeHtml(name).replace(/"/g, '&quot;');
            return `<img class="product-image" src="${safeUrl}" alt="${safeName}" loading="lazy" />`;
        }
        
        // Auto-refresh cada 30 segundos
        setInterval(cargarCarrito, 30000);
    </script>
</body>
</html>'''


# =============================================================================
# Main
# =============================================================================

def main():
    """Iniciar servidor."""
    init_db()
    print(f"=== Servidor web de Coto Digital ===")
    print(f"Puerto: {PORT}")
    print(f"User ID: {USER_ID}")
    print(f"Base de datos: {DB_PATH}")
    print(f"URL: http://localhost:{PORT}")
    print(f"Presioná Ctrl+C para detener")
    print()
    
    server = HTTPServer(('0.0.0.0', PORT), CotoDashboardHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
        server.shutdown()


if __name__ == "__main__":
    main()
