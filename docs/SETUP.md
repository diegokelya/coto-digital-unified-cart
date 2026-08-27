# Configuración del Sistema

## Variables de entorno requeridas

Crear archivo `.env` en la raíz del proyecto o exportar en `.bashrc`:

```bash
export TELEGRAM_BOT_TOKEN="tu_bot_token_aquí"
export TELEGRAM_CHAT_ID="406287065"
```

### Obtener token de Telegram Bot

1. Abrir Telegram y buscar `@BotFather`
2. Enviar `/newbot`
3. Seguir instrucciones para crear el bot
4. Copiar el token que BotFather proporciona
5. Para obtener tu `CHAT_ID`:
   - Enviar un mensaje a tu bot
   - Visitar: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Buscar el campo `"chat":{"id":...}`

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/diegokelya/coto-digital-unified-cart.git
cd coto-digital-unified-cart
```

### 2. Instalar dependencias

```bash
pip3 install -r requirements.txt
```

### 3. Configurar base de datos

```bash
# Crear directorio de datos si no existe
mkdir -p ~/.hermes/data

# Inicializar base de datos (se crea automáticamente al ejecutar)
sqlite3 ~/.hermes/data/coto_carrito.db "
CREATE TABLE IF NOT EXISTS carrito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id TEXT UNIQUE,
    nombre TEXT,
    precio REAL,
    imagen_url TEXT,
    cantidad INTEGER DEFAULT 1,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS historial_busquedas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    resultados_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

### 4. Configurar servicios systemd

```bash
# Crear directorio de servicios de usuario
mkdir -p ~/.config/systemd/user

# Copiar servicios
cp systemd/coto-telegram-bot.service ~/.config/systemd/user/
cp systemd/coto-dashboard-web.service ~/.config/systemd/user/

# Editar servicios para reemplazar rutas si es necesario
# Cambiar %h/.hermes/scripts por la ruta a src/ del proyecto

# Recargar systemd
systemctl --user daemon-reload

# Habilitar servicios
systemctl --user enable coto-telegram-bot.service
systemctl --user enable coto-dashboard-web.service

# Iniciar servicios
systemctl --user start coto-telegram-bot.service
systemctl --user start coto-dashboard-web.service
```

### 5. Verificar servicios

```bash
# Ver estado
systemctl --user status coto-telegram-bot.service
systemctl --user status coto-dashboard-web.service

# Ver logs en tiempo real
journalctl --user -u coto-telegram-bot -f
journalctl --user -u coto-dashboard-web -f

# Verificar que el dashboard responde
curl http://localhost:8766/api/carrito
```

### 6. Instalar extensión Chrome

1. Abrir Chrome
2. Navegar a `chrome://extensions/`
3. Activar "Modo de desarrollador" (esquina superior derecha)
4. Clic en "Cargar extensión sin empaquetar"
5. Seleccionar carpeta `extension/` del proyecto
6. La extensión aparecerá en la barra de herramientas

### 7. Configurar extensión Chrome

1. Navegar a `https://www.cotodigital3.com.ar`
2. Abrir DevTools (F12) → Console
3. Verificar que no hay errores de CORS
4. Buscar productos en Coto Digital
5. Clic en ícono de extensión → "Importar al Dashboard"
6. Verificar en `http://localhost:8766/` que los productos aparecen

## Configuración avanzada

### Cambiar puerto del dashboard

Editar `src/coto_dashboard_web.py` línea final:

```python
app.run(host='0.0.0.0', port=8766, debug=False)
# Cambiar 8766 por el puerto deseado
```

Actualizar también:
- `extension/dashboard.js`: variable `DASHBOARD_URL`
- `scripts/sync_coto_dashboard.mjs`: variable `DASHBOARD_URL`

### Ejecutar en producción con Gunicorn

```bash
pip3 install gunicorn

gunicorn -w 4 -b 0.0.0.0:8766 coto_dashboard_web:app
```

Actualizar `coto-dashboard-web.service`:

```ini
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:8766 coto_dashboard_web:app
```

### Configurar firewall para acceso remoto

```bash
# UFW
sudo ufw allow 8766/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8766 -j ACCEPT
```

### Habilitar HTTPS con certificado autofirmado

```bash
# Generar certificado
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Actualizar coto_dashboard_web.py
app.run(host='0.0.0.0', port=8766, 
        ssl_context=('cert.pem', 'key.pem'))
```

## Solución de problemas

### Dashboard no inicia

```bash
# Verificar que puerto no esté ocupado
lsof -i :8766

# Matar proceso si es necesario
kill $(lsof -t -i :8766)

# Verificar logs
journalctl --user -u coto-dashboard-web -n 100
```

### Bot no responde

```bash
# Verificar token
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Debe responder con información del bot
# Si falla, el token es inválido

# Reiniciar servicio
systemctl --user restart coto-telegram-bot
```

### Extensión no comunica con dashboard

1. Verificar CORS en `coto_dashboard_web.py`:
   ```python
   @app.after_request
   def after_request(response):
       response.headers.add('Access-Control-Allow-Origin', '*')
       return response
   ```

2. Verificar URL en `extension/dashboard.js` coincida con IP del servidor

3. Abrir DevTools → Console y buscar errores de red

### Base de datos corrupta

```bash
# Backup
cp ~/.hermes/data/coto_carrito.db ~/.hermes/data/coto_carrito.db.backup

# Verificar integridad
sqlite3 ~/.hermes/data/coto_carrito.db "PRAGMA integrity_check;"

# Recrear si es necesario
rm ~/.hermes/data/coto_carrito.db
# Ejecutar paso 3 de instalación nuevamente
```

## Monitoreo

### Logs

```bash
# Dashboard web
tail -f ~/.hermes/data/coto_dashboard.log

# Bot Telegram
tail -f ~/.hermes/data/coto_telegram.log

# Systemd (todos los servicios)
journalctl --user -f
```

### Métricas

```bash
# Productos en carrito
sqlite3 ~/.hermes/data/coto_carrito.db "SELECT COUNT(*) FROM carrito;"

# Total de búsquedas
sqlite3 ~/.hermes/data/coto_carrito.db "SELECT COUNT(*) FROM historial_busquedas;"

# Búsquedas más frecuentes
sqlite3 ~/.hermes/data/coto_carrito.db "
SELECT query, COUNT(*) as count 
FROM historial_busquedas 
GROUP BY query 
ORDER BY count DESC 
LIMIT 10;
"
```

## Actualización

```bash
cd coto-digital-unified-cart
git pull origin main

# Reinstalar dependencias si cambiaron
pip3 install -r requirements.txt

# Reiniciar servicios
systemctl --user restart coto-telegram-bot
systemctl --user restart coto-dashboard-web

# Recargar extensión Chrome
# chrome://extensions/ → Clic en icono de recarga
```

## Contribuir

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

MIT - Ver archivo `LICENSE`
