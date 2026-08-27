# Coto Digital - Sistema de Carrito Unificado

Sistema completo para gestionar compras en Coto Digital con interfaz web unificada y bot de Telegram.

## Características

- 🛒 **Carrito unificado**: Dashboard web con búsqueda y gestión de productos
- 🤖 **Bot de Telegram**: Control remoto del carrito y pedidos
- 🔍 **Búsqueda inteligente**: Búsqueda en tiempo real en catálogo Coto Digital
- 📊 **Dashboard persistente**: Interfaz web en `http://192.168.68.118:8766/`
- 🧩 **Extensión Chrome**: Importación automática de productos desde Coto Digital
- 🔄 **Sincronización automática**: SQLite como fuente única de verdad

## Arquitectura

### Componentes

1. **Backend Python** (`src/`)
   - `coto_digital_bot.py`: Lógica de búsqueda y gestión de productos
   - `coto_dashboard_web.py`: Servidor web Flask con API REST
   - `coto_telegram_bot.py`: Bot de Telegram para control remoto

2. **Frontend** (embebido en `coto_dashboard_web.py`)
   - Interfaz web moderna con búsqueda en tiempo real
   - Gestión visual del carrito con imágenes
   - Importación automática desde extensión Chrome

3. **Extensión Chrome** (`extension/`)
   - Captura productos desde Coto Digital
   - Comunicación con dashboard vía `postMessage`
   - Auto-importación al carrito unificado

4. **Sincronización** (`scripts/`)
   - `sync_coto_dashboard.mjs`: Sincronización bidireccional
   - Actualización automática de precios y disponibilidad

### Base de datos

SQLite: `~/.hermes/data/coto_carrito.db`

```sql
CREATE TABLE carrito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id TEXT UNIQUE,
    nombre TEXT,
    precio REAL,
    imagen_url TEXT,
    cantidad INTEGER DEFAULT 1,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE historial_busquedas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    resultados_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Instalación

### 1. Requisitos

```bash
sudo apt install python3 python3-pip sqlite3
pip3 install flask requests
```

### 2. Variables de entorno

```bash
export TELEGRAM_BOT_TOKEN="tu_token_aquí"
export TELEGRAM_CHAT_ID="406287065"
```

### 3. Servicios systemd

```bash
# Copiar servicios
cp systemd/*.service ~/.config/systemd/user/

# Habilitar e iniciar
systemctl --user daemon-reload
systemctl --user enable --now coto-telegram-bot.service
systemctl --user enable --now coto-dashboard-web.service

# Ver logs
journalctl --user -u coto-telegram-bot -f
journalctl --user -u coto-dashboard-web -f
```

### 4. Extensión Chrome

1. Abrir Chrome → `chrome://extensions/`
2. Activar "Modo de desarrollador"
3. "Cargar extensión sin empaquetar" → seleccionar carpeta `extension/`
4. La extensión se activará automáticamente en `cotodigital3.com.ar`

## Uso

### Dashboard Web

```bash
# Acceder al dashboard
http://192.168.68.118:8766/

# Buscar productos
# Agregar al carrito
# Importar desde extensión Chrome
# Sincronizar con Coto Digital
```

### Bot de Telegram

```
/buscar [producto] - Buscar productos
/carrito - Ver carrito actual
/agregar [id] - Agregar producto al carrito
/eliminar [id] - Quitar producto del carrito
/vaciar - Vaciar carrito completo
/sincronizar - Sincronizar con Coto Digital
```

### Extensión Chrome

1. Navegar a Coto Digital
2. Buscar productos
3. La extensión captura automáticamente productos visibles
4. Clic en ícono → "Importar al Dashboard"
5. Productos aparecen en `http://192.168.68.118:8766/`

## API REST

### Endpoints

```bash
# Obtener carrito
GET /api/carrito

# Buscar productos
GET /api/buscar?q=leche

# Agregar al carrito
POST /api/carrito
Content-Type: application/json
{"producto_id": "123", "nombre": "Leche", "precio": 450.0, "cantidad": 2}

# Eliminar del carrito
DELETE /api/carrito/<producto_id>

# Importar desde extensión
POST /api/importar
Content-Type: application/json
{"productos": [...]}

# Sincronizar con Coto Digital
POST /api/sincronizar
```

## Desarrollo

### Estructura del proyecto

```
coto-digital-unified-cart/
├── src/                      # Backend Python
│   ├── coto_digital_bot.py
│   ├── coto_dashboard_web.py
│   └── coto_telegram_bot.py
├── extension/                # Extensión Chrome
│   ├── manifest.json
│   ├── background.js
│   ├── coto.js
│   └── dashboard.js
├── scripts/                  # Sincronización
│   ├── sync_coto_dashboard.mjs
│   └── verify_coto_dashboard.mjs
├── systemd/                  # Servicios
│   └── coto-telegram-bot.service
├── docs/                     # Documentación
│   └── instrucciones_bot.md
└── README.md
```

### Testing

```bash
# Verificar dashboard
curl http://192.168.68.118:8766/api/carrito

# Test de búsqueda
python3 src/coto_digital_bot.py

# Verificar sincronización
node scripts/verify_coto_dashboard.mjs
```

## Seguridad

- ✅ No almacena credenciales de Coto Digital
- ✅ Tokens de Telegram en variables de entorno
- ✅ Base de datos SQLite local
- ✅ Comunicación HTTPS con Coto Digital
- ✅ Extensión Chrome con permisos mínimos

## Solución de problemas

### Dashboard no responde

```bash
systemctl --user restart coto-dashboard-web.service
journalctl --user -u coto-dashboard-web -n 50
```

### Bot de Telegram no responde

```bash
systemctl --user restart coto-telegram-bot.service
# Verificar token
echo $TELEGRAM_BOT_TOKEN
```

### Extensión no importa productos

1. Verificar que dashboard esté corriendo en `:8766`
2. Abrir DevTools → Console en Coto Digital
3. Buscar errores de CORS o comunicación
4. Recargar extensión en `chrome://extensions/`

## Roadmap

- [ ] Integración con Home Assistant para alertas
- [ ] Historial de precios y tendencias
- [ ] Notificaciones de ofertas
- [ ] Listas de compras predefinidas
- [ ] Exportar carrito a PDF/Excel
- [ ] Comparador de precios con otros supermercados

## Licencia

MIT

## Autor

Diego Kelyacoubian

## Soporte

Para reportar bugs o sugerir mejoras, abrir un issue en GitHub.
