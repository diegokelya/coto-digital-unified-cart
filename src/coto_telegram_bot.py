#!/usr/bin/env python3
"""
Bot persistente de Telegram para Coto Digital
Escucha comandos 24/7 mediante long polling
"""

import os
import sys
import json
import time
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import subprocess
from datetime import datetime

# Importar funciones del bot principal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuración
BOT_TOKEN = os.getenv("COTO_TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("COTO_TELEGRAM_CHAT_ID")
LOG_FILE = os.path.expanduser("~/.hermes/data/coto_bot.log")
STATE_FILE = os.path.expanduser("~/.hermes/data/coto_bot_state.json")
DB_PATH = os.path.expanduser("~/.hermes/data/coto_carrito.db")

if not BOT_TOKEN:
    print("❌ COTO_TELEGRAM_BOT_TOKEN no configurado")
    print("Configurá el token con:")
    print("  read -rsp 'Token: ' T && echo \"COTO_TELEGRAM_BOT_TOKEN=$T\" >> ~/.hermes/.env")
    sys.exit(1)

if not CHAT_ID:
    print("⚠️ COTO_TELEGRAM_CHAT_ID no configurado")
    print("El bot responderá a cualquier chat.")

# Logging
def log(mensaje):
    """Escribir mensaje en log y stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"
    
    print(linea, flush=True)
    
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a') as f:
            f.write(linea + '\n')
    except Exception as e:
        print(f"Error escribiendo log: {e}")

# Estado persistente
def cargar_estado():
    """Cargar último update_id procesado."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {'last_update_id': 0}
    except:
        return {'last_update_id': 0}

def guardar_estado(estado):
    """Guardar último update_id procesado."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(estado, f)
    except Exception as e:
        log(f"Error guardando estado: {e}")

# API de Telegram
def enviar_mensaje(chat_id, texto):
    """Enviar mensaje de Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        'chat_id': chat_id,
        'text': texto,
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
        log(f"Error enviando mensaje: {e}")
        return False

def obtener_actualizaciones(offset=0):
    """Obtener actualizaciones de Telegram (long polling)."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    data = {
        'offset': offset,
        'timeout': 30,  # Long polling de 30 segundos
        'allowed_updates': ['message']
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        resp = urllib.request.urlopen(req, timeout=35)
        result = json.loads(resp.read().decode())
        
        if result.get('ok'):
            return result.get('result', [])
        else:
            log(f"Error en getUpdates: {result}")
            return []
    except Exception as e:
        log(f"Error obteniendo actualizaciones: {e}")
        return []

# Procesamiento de comandos (importado del bot principal)
def procesar_comando_local(comando, user_id="default"):
    """Procesar comando usando el bot principal de Coto Digital."""
    try:
        # Ejecutar el bot principal como subproceso, pasando el user_id
        result = subprocess.run(
            ['python3', '/home/diego/.hermes/scripts/coto_digital_bot.py', comando, str(user_id)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            log(f"Error procesando comando: {result.stderr}")
            return "❌ Error procesando el comando"
    except Exception as e:
        log(f"Error ejecutando comando: {e}")
        return f"❌ Error: {e}"

# Loop principal
def main():
    """Loop principal del bot."""
    log("=== Bot de Coto Digital iniciado ===")
    log("Token de Telegram configurado")
    log(f"Chat ID autorizado: {CHAT_ID or 'Cualquiera'}")
    
    estado = cargar_estado()
    offset = estado['last_update_id'] + 1
    
    log(f"Comenzando desde update_id: {offset}")
    
    while True:
        try:
            updates = obtener_actualizaciones(offset)
            
            for update in updates:
                update_id = update['update_id']
                
                # Actualizar offset
                if update_id >= offset:
                    offset = update_id + 1
                    estado['last_update_id'] = update_id
                    guardar_estado(estado)
                
                # Procesar mensaje
                if 'message' in update:
                    msg = update['message']
                    chat = msg['chat']
                    chat_id = chat['id']
                    
                    # Filtrar por chat autorizado si está configurado
                    if CHAT_ID and str(chat_id) != str(CHAT_ID):
                        log(f"Mensaje de chat no autorizado: {chat_id}")
                        continue
                    
                    # Obtener texto del mensaje
                    texto = msg.get('text', '')
                    
                    if not texto:
                        continue
                    
                    # Log del comando
                    usuario = chat.get('first_name', 'Usuario')
                    log(f"Comando de {usuario} (chat {chat_id}): {texto}")
                    
                    # Procesar comando
                    respuesta = procesar_comando_local(texto, user_id=str(chat_id))
                    
                    # Enviar respuesta
                    if respuesta:
                        enviar_mensaje(chat_id, respuesta)
                        log(f"Respuesta enviada ({len(respuesta)} chars)")
        
        except KeyboardInterrupt:
            log("Bot detenido por el usuario")
            break
        except Exception as e:
            log(f"Error en loop principal: {e}")
            time.sleep(5)  # Esperar antes de reintentar

if __name__ == "__main__":
    main()
