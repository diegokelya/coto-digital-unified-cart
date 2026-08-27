#!/usr/bin/env python3
"""
Bot de Telegram para hacer pedidos en Coto Digital
Permite buscar productos, ver precios y armar carrito
"""

import os
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
import re
from datetime import datetime

# Configuración
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "406287065")
DB_PATH = os.path.expanduser("~/.hermes/data/coto_carrito.db")

# URLs de Coto Digital
COTO_BASE_URL = "https://www.cotodigital3.com.ar"
COTO_SEARCH_URL = f"{COTO_BASE_URL}/sitios/cdigi/browse/search"

# Almacenamiento temporal de resultados de búsqueda por usuario
# Estructura: {user_id: {'query': str, 'resultados': [productos], 'timestamp': float}}
BUSQUEDAS_CACHE = {}


# =============================================================================
# Base de datos
# =============================================================================

def init_db():
    """Inicializar base de datos SQLite para el carrito."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Habilitar WAL mode para mejor concurrencia (múltiples procesos)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.commit()
    
    cursor = conn.cursor()
    
    # Tabla de productos en el carrito
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            producto_nombre TEXT NOT NULL,
            producto_url TEXT,
            producto_imagen TEXT,
            precio REAL,
            cantidad INTEGER DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columnas_carrito = {row[1] for row in cursor.execute("PRAGMA table_info(carrito)")}
    if 'producto_imagen' not in columnas_carrito:
        cursor.execute("ALTER TABLE carrito ADD COLUMN producto_imagen TEXT")
    
    # Tabla de búsquedas recientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS busquedas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            query TEXT NOT NULL,
            resultados INTEGER DEFAULT 0,
            searched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


# =============================================================================
# API de Coto Digital
# =============================================================================

def buscar_productos(query):
    """
    Buscar productos en Coto Digital usando la API JSON.
    Retorna lista de diccionarios con: nombre, precio, url, imagen, id
    """
    # Usar la API JSON que funciona
    url = f"https://www.cotodigital3.com.ar/sitios/cdigi/browse/search?Ntt={urllib.parse.quote(query)}&format=json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': COTO_BASE_URL
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))
        
        # Extraer productos recursivamente del JSON anidado
        productos = []
        productos_ids = set()  # Para evitar duplicados
        
        def extraer_productos_recursivo(obj):
            """Buscar productos recursivamente en la estructura JSON."""
            if isinstance(obj, dict):
                # Si encontramos 'records' con lista, procesar
                if 'records' in obj and isinstance(obj['records'], list):
                    for record in obj['records']:
                        # Los productos reales están en record.records[0].attributes
                        if 'records' in record and isinstance(record['records'], list):
                            for sub_record in record['records']:
                                if 'attributes' in sub_record:
                                    attrs = sub_record['attributes']
                                    
                                    # Extraer información del producto
                                    nombre = None
                                    precio = 0.0
                                    producto_id = None
                                    imagen = None
                                    
                                    # Nombre del producto
                                    if 'product.displayName' in attrs:
                                        nombre = attrs['product.displayName'][0] if isinstance(attrs['product.displayName'], list) else attrs['product.displayName']
                                    
                                    # ID del producto
                                    if 'product.repositoryId' in attrs:
                                        producto_id = attrs['product.repositoryId'][0] if isinstance(attrs['product.repositoryId'], list) else attrs['product.repositoryId']
                                    
                                    # Precio activo (el que se muestra)
                                    if 'sku.activePrice' in attrs:
                                        precio_str = attrs['sku.activePrice'][0] if isinstance(attrs['sku.activePrice'], list) else attrs['sku.activePrice']
                                        try:
                                            precio = float(precio_str)
                                        except:
                                            precio = 0.0

                                    if 'product.mediumImage.url' in attrs:
                                        valor_imagen = attrs['product.mediumImage.url']
                                        imagen = valor_imagen[0] if isinstance(valor_imagen, list) and valor_imagen else valor_imagen
                                    
                                    # Solo agregar si tiene nombre y no está duplicado
                                    if nombre and producto_id and producto_id not in productos_ids:
                                        productos_ids.add(producto_id)
                                        
                                        producto = {
                                            'nombre': nombre.strip(),
                                            'url': f"{COTO_BASE_URL}/sitios/cdigi/producto/{producto_id}",
                                            'precio': precio,
                                            'id': producto_id,
                                            'imagen': imagen
                                        }
                                        productos.append(producto)
                
                # Seguir buscando recursivamente
                for value in obj.values():
                    extraer_productos_recursivo(value)
            
            elif isinstance(obj, list):
                for item in obj:
                    extraer_productos_recursivo(item)
        
        # Iniciar búsqueda recursiva
        extraer_productos_recursivo(data)
        
        # Limitar a 10 resultados
        return productos[:10]
        
    except Exception as e:
        print(f"Error buscando productos: {e}")
        import traceback
        traceback.print_exc()
        return []


# =============================================================================
# Gestión del carrito
# =============================================================================

def agregar_al_carrito(user_id, producto_nombre, producto_url, precio, cantidad=1, producto_imagen=None):
    """Agregar un producto al carrito."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO carrito
            (user_id, producto_nombre, producto_url, producto_imagen, precio, cantidad)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, producto_nombre, producto_url, producto_imagen, precio, cantidad))
    
    conn.commit()
    conn.close()


def ver_carrito(user_id):
    """Ver todos los productos en el carrito."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, producto_nombre, precio, cantidad, added_at
        FROM carrito
        WHERE user_id = ?
        ORDER BY added_at DESC
    """, (user_id,))
    
    items = cursor.fetchall()
    conn.close()
    
    return items


def vaciar_carrito(user_id):
    """Vaciar el carrito del usuario."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM carrito WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()


def eliminar_item_carrito(item_id, user_id):
    """Eliminar un item específico del carrito."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM carrito
        WHERE id = ? AND user_id = ?
    """, (item_id, user_id))
    
    conn.commit()
    conn.close()


def sincronizar_dashboard():
    """Sincronizar dashboard de Home Assistant después de cambios en el carrito."""
    try:
        import subprocess
        result = subprocess.run(
            ['/home/diego/.hermes/scripts/sync_coto_dashboard.sh'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error sincronizando dashboard: {e}")
        return False


def agregar_producto_manual(user_id, nombre, precio, cantidad=1):
    """Agregar un producto manualmente al carrito (sin búsqueda previa)."""
    try:
        precio_float = float(precio)
    except ValueError:
        return False, "Precio inválido"
    
    if cantidad < 1:
        return False, "La cantidad debe ser mayor a 0"
    
    agregar_al_carrito(
        user_id,
        nombre,
        COTO_BASE_URL,  # producto_url (posicional)
        precio_float,
        cantidad
    )
    
    return True, f"Producto agregado: {nombre} - ${precio_float:.2f} × {cantidad}"


# =============================================================================
# Bot de Telegram
# =============================================================================

def enviar_mensaje_telegram(mensaje):
    """Enviar mensaje a Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return False


def procesar_comando(comando, user_id="default"):
    """Procesar comandos del bot."""
    partes = comando.strip().split(None, 1)
    cmd = partes[0].lower()
    args = partes[1] if len(partes) > 1 else ""
    
    if cmd == "/buscar":
        if not args:
            return "❌ Uso: /buscar <producto>\nEjemplo: /buscar coca cola"
        
        productos = buscar_productos(args)
        
        if not productos:
            return f"❌ No se encontraron productos para '{args}'"
        
        # Guardar búsqueda en caché por usuario
        BUSQUEDAS_CACHE[user_id] = {
            'query': args,
            'resultados': productos,
            'timestamp': datetime.now().timestamp()
        }
        
        # Guardar en BD
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO busquedas (user_id, query, resultados)
            VALUES (?, ?, ?)
        """, (user_id, args, len(productos)))
        conn.commit()
        conn.close()
        
        # Formatear resultados
        mensaje = f"🔍 *Resultados para '{args}'* ({len(productos)} productos)\n\n"
        
        for i, p in enumerate(productos, 1):
            mensaje += f"*{i}. {p['nombre']}*\n"
            mensaje += f"   💰 ${p['precio']:.2f}\n"
            mensaje += f"   🔗 [Ver producto]({p['url']})\n"
            mensaje += f"   `/agregar {i}` para añadir al carrito\n\n"
        
        return mensaje
    
    elif cmd == "/agregar":
        if not args:
            return "❌ Uso: /agregar <número>\nEjemplo: /agregar 1"
        
        try:
            indice = int(args) - 1  # Convertir a índice base-0
        except ValueError:
            return f"❌ '{args}' no es un número válido"
        
        # Verificar que hay búsqueda en caché
        if user_id not in BUSQUEDAS_CACHE:
            return "❌ Primero hacé una búsqueda con `/buscar <producto>`"
        
        resultados = BUSQUEDAS_CACHE[user_id]['resultados']
        
        # Verificar índice válido
        if indice < 0 or indice >= len(resultados):
            return f"❌ Número inválido. Tenés {len(resultados)} resultados disponibles."
        
        # Obtener producto seleccionado
        producto = resultados[indice]
        
        # Agregar al carrito
        agregar_al_carrito(
            user_id,
            producto['nombre'],
            producto['url'],
            producto['precio'],
            cantidad=1,
            producto_imagen=producto.get('imagen')
        )
        
        # Sincronizar dashboard
        sincronizar_dashboard()
        
        return f"✅ *Agregado al carrito*\n\n{producto['nombre']}\n💰 ${producto['precio']:.2f}\n\nUsá `/carrito` para ver tu carrito completo."
    
    elif cmd == "/carrito":
        items = ver_carrito(user_id)
        
        if not items:
            return "🛒 *Tu carrito está vacío*\n\nUsá `/buscar` para encontrar productos."
        
        mensaje = "🛒 *Tu carrito de compras*\n\n"
        total = 0.0
        
        for item_id, nombre, precio, cantidad, added_at in items:
            subtotal = precio * cantidad
            total += subtotal
            mensaje += f"*{nombre}*\n"
            mensaje += f"   Cantidad: {cantidad} × ${precio:.2f} = ${subtotal:.2f}\n"
            mensaje += f"   `/eliminar {item_id}` para quitar\n\n"
        
        mensaje += f"━━━━━━━━━━━━━━━━━━\n"
        mensaje += f"*TOTAL: ${total:.2f}*\n\n"
        mensaje += f"Comandos:\n"
        mensaje += f"• `/vaciar` — vaciar carrito\n"
        mensaje += f"• `/finalizar` — ir a Coto Digital para completar el pedido"
        
        return mensaje
    
    elif cmd == "/eliminar":
        if not args:
            return "❌ Uso: /eliminar <id>\nEjemplo: /eliminar 5\n\nUsá `/carrito` para ver los IDs."
        
        try:
            item_id = int(args)
        except ValueError:
            return f"❌ '{args}' no es un ID válido"
        
        eliminar_item_carrito(item_id, user_id)
        
        # Sincronizar dashboard
        sincronizar_dashboard()
        
        return f"✅ Producto eliminado del carrito"
    
    elif cmd == "/manual":
        # Formato: /manual Leche La Serenísima 1L | 2809
        # O: /manual Leche La Serenísima 1L | 2809 | 2 (con cantidad)
        if not args:
            return (
                "❌ Uso: `/manual <nombre> | <precio>` o `/manual <nombre> | <precio> | <cantidad>`\n\n"
                "**Ejemplos:**\n"
                "`/manual Leche La Serenísima 1L | 2809`\n"
                "`/manual Coca Cola 2.25L | 4845 | 2`"
            )
        
        # Parsear entrada
        partes = [p.strip() for p in args.split('|')]
        
        if len(partes) < 2:
            return "❌ Formato incorrecto. Usá: `/manual <nombre> | <precio>`"
        
        nombre = partes[0]
        precio_str = partes[1]
        cantidad = 1
        
        if len(partes) >= 3:
            try:
                cantidad = int(partes[2])
                if cantidad < 1:
                    return "❌ La cantidad debe ser mayor a 0"
            except ValueError:
                return f"❌ Cantidad inválida: '{partes[2]}'"
        
        # Normalizar precio (aceptar: 2809, 2809.50, 2.809, 2.809,50)
        # Primero eliminar puntos de miles, luego convertir coma decimal a punto
        precio_str = precio_str.replace('.', '')  # Eliminar separadores de miles
        precio_str = precio_str.replace(',', '.')  # Coma decimal → punto
        
        # Si tiene más de 2 decimales, es probable que sea un error
        # Ej: "2809.50" → "280950" → "2809.50" (correcto)
        # Ej: "2.809,50" → "2809.50" (correcto)
        try:
            precio_float = float(precio_str)
            # Si el precio resultante es > 1000000, probablemente hubo error
            if precio_float > 1000000:
                return "❌ Precio sospechoso (demasiado alto). Revisá el formato.\nEjemplo correcto: `2809` o `2809,50`"
        except ValueError:
            return f"❌ Precio inválido: '{partes[1]}'\nUsá formato: `2809` o `2809,50`"
        
        exito, mensaje = agregar_producto_manual(user_id, nombre, precio_str, cantidad)
        
        if exito:
            # Sincronizar dashboard
            sincronizar_dashboard()
            return f"✅ *Agregado al carrito*\n\n{mensaje}\n\nUsá `/carrito` para ver tu carrito completo."
        else:
            return f"❌ Error: {mensaje}"
    
    elif cmd == "/vaciar":
        vaciar_carrito(user_id)
        
        # Sincronizar dashboard
        sincronizar_dashboard()
        
        return "✅ Carrito vaciado"
    
    elif cmd == "/finalizar":
        items = ver_carrito(user_id)
        
        if not items:
            return "❌ Tu carrito está vacío\n\nUsá `/buscar` para encontrar productos."
        
        # Generar resumen del pedido
        mensaje = "📋 *RESUMEN DEL PEDIDO*\n\n"
        total = 0.0
        
        for item_id, nombre, precio, cantidad, added_at in items:
            subtotal = precio * cantidad
            total += subtotal
            mensaje += f"• {nombre}\n"
            mensaje += f"  {cantidad} × ${precio:.2f} = ${subtotal:.2f}\n\n"
        
        mensaje += f"━━━━━━━━━━━━━━━━━━\n"
        mensaje += f"*TOTAL: ${total:.2f}*\n"
        mensaje += f"━━━━━━━━━━━━━━━━━━\n\n"
        
        mensaje += f"⚠️ **IMPORTANTE:**\n"
        mensaje += f"El bot NO puede completar el pedido automáticamente.\n\n"
        mensaje += f"**Próximos pasos:**\n"
        mensaje += f"1. Abrí Coto Digital: {COTO_BASE_URL}\n"
        mensaje += f"2. Agregá estos productos manualmente\n"
        mensaje += f"3. Completá dirección y forma de pago\n"
        mensaje += f"4. Confirmá el pedido\n\n"
        mensaje += f"💡 **Tip:** Guardá este mensaje como referencia\n"
        mensaje += f"para no olvidar ningún producto."
        
        return mensaje
    
    elif cmd == "/ayuda" or cmd == "/start":
        mensaje = """
🛒 *Bot de Coto Digital*

*Comandos disponibles:*

🔍 `/buscar <producto>` — buscar productos
   Ejemplo: `/buscar leche`

➕ `/agregar <número>` — agregar producto al carrito
   (después de hacer una búsqueda)

✏️ `/manual <nombre> | <precio> | <cantidad>` — agregar producto manualmente
   Ejemplos:
   `/manual Leche La Serenísima 1L | 2809`
   `/manual Coca Cola 2.25L | 4845 | 2`

🛒 `/carrito` — ver tu carrito

➖ `/eliminar <id>` — quitar producto del carrito

🗑️ `/vaciar` — vaciar el carrito completo

✅ `/finalizar` — generar resumen del pedido

❓ `/ayuda` — mostrar esta ayuda

⚠️ **NOTA:**
Este bot NO almacena contraseñas ni accede a tu sesión.
Todo funciona de forma manual y local.
"""
        return mensaje
    
    else:
        return f"❌ Comando desconocido: {cmd}\nUsá `/ayuda` para ver comandos disponibles"


# =============================================================================
# Main
# =============================================================================

def main():
    """Punto de entrada principal."""
    init_db()
    
    if len(sys.argv) < 2:
        print("Uso: coto_digital_bot.py '<comando>' [user_id]")
        print("Ejemplo: coto_digital_bot.py '/buscar coca cola'")
        print("         coto_digital_bot.py '/buscar coca cola' '12345'")
        sys.exit(1)
    
    comando = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    respuesta = procesar_comando(comando, user_id)
    
    print(respuesta)
    
    # Enviar a Telegram si está configurado (solo para modo default)
    if TELEGRAM_BOT_TOKEN and user_id == "default":
        enviar_mensaje_telegram(respuesta)


if __name__ == "__main__":
    main()
