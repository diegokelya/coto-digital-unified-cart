# Coto Digital para Home Assistant

<p align="center">
  <img src="logo.png" alt="Coto Digital Logo" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS"></a>
  <a href="https://github.com/diegokelya/coto-digital-unified-cart/releases"><img src="https://img.shields.io/github/release/diegokelya/coto-digital-unified-cart.svg" alt="GitHub Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/diegokelya/coto-digital-unified-cart.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/country-AR-blue.svg" alt="Argentina">
</p>

Integración completa de Coto Digital para Home Assistant. Gestiona tu carrito de compras, busca productos y automatiza tus compras desde Home Assistant.

## Características

### Integración Home Assistant (HACS)

- 🏠 **Integración nativa**: Instalación vía HACS con config UI
- 📊 **Sensores en tiempo real**: Total en pesos, productos y unidades
- 🔘 **Botones**: Vaciar carrito y sincronizar con un clic
- 📡 **Servicios**: Buscar, agregar, eliminar productos vía automatizaciones
- 🗄️ **Base de datos local**: Persistencia SQLite integrada

### Componentes adicionales

- 🛒 **Dashboard web**: Interfaz web unificada (puerto 8766)
- 🤖 **Bot de Telegram**: Control remoto del carrito
- 🧩 **Extensión Chrome**: Importación automática desde Coto Digital
- 🔄 **Sincronización**: Scripts automáticos de actualización

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

### Método 1: HACS (Recomendado)

#### Requisitos previos

- Home Assistant 2023.1.0 o superior
- [HACS](https://hacs.xyz/) instalado

#### Pasos

1. **Agregar repositorio custom a HACS**:
   - Abrir HACS en Home Assistant
   - Clic en los tres puntos (⋮) → "Custom repositories"
   - URL: `https://github.com/diegokelya/coto-digital-unified-cart`
   - Categoría: `Integration`
   - Clic en "Add"

2. **Instalar la integración**:
   - En HACS, buscar "Coto Digital"
   - Clic en "Download"
   - Reiniciar Home Assistant

3. **Configurar la integración**:
   - Ir a Configuración → Dispositivos y servicios
   - Clic en "+ Agregar integración"
   - Buscar "Coto Digital"
   - Seguir el asistente de configuración

### Método 2: Instalación manual

1. Descargar la última versión desde [Releases](https://github.com/diegokelya/coto-digital-unified-cart/releases)
2. Descomprimir y copiar `custom_components/coto_digital` a tu directorio `custom_components/` de Home Assistant
3. Reiniciar Home Assistant
4. Agregar la integración desde la UI

### Método 3: Componentes standalone (Dashboard + Bot)

Para usar el dashboard web y bot de Telegram sin Home Assistant:

```bash
sudo apt install python3 python3-pip sqlite3
pip3 install flask requests
```

Ver [docs/SETUP.md](docs/SETUP.md) para configuración completa de componentes standalone.

## Uso en Home Assistant

### Sensores

La integración crea automáticamente estos sensores:

- `sensor.coto_digital_productos` - Cantidad de productos diferentes
- `sensor.coto_digital_unidades` - Total de unidades
- `sensor.coto_digital_total` - Total en pesos (ARS)

### Botones

- `button.vaciar_carrito_coto_digital` - Vacía el carrito
- `button.sincronizar_coto_digital` - Sincroniza con Coto Digital

### Servicios

#### Buscar productos

```yaml
service: coto_digital.buscar_producto
data:
  query: "leche"
```

#### Agregar al carrito

```yaml
service: coto_digital.agregar_al_carrito
data:
  producto_id: "prod_123456"
  nombre: "Leche La Serenísima 1L"
  precio: 450.50
  cantidad: 2
```

#### Eliminar del carrito

```yaml
service: coto_digital.eliminar_del_carrito
data:
  producto_id: "prod_123456"
```

#### Vaciar carrito

```yaml
service: coto_digital.vaciar_carrito
```

### Automatizaciones de ejemplo

#### Recordatorio de compras

```yaml
automation:
  - alias: "Recordar hacer compras"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.coto_digital_productos
        above: 0
    action:
      - service: notify.mobile_app_iphone_de_diego
        data:
          title: "Carrito Coto Digital"
          message: >
            Tienes {{ states('sensor.coto_digital_productos') }} productos 
            por un total de ${{ states('sensor.coto_digital_total') }}
```

#### Alerta de carrito grande

```yaml
automation:
  - alias: "Alerta carrito grande"
    trigger:
      - platform: numeric_state
        entity_id: sensor.coto_digital_total
        above: 50000
    action:
      - service: notify.mobile_app_iphone_de_diego
        data:
          message: "Tu carrito supera los $50.000"
```

#### Dashboard Lovelace

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Coto Digital
    entities:
      - entity: sensor.coto_digital_productos
        name: Productos
      - entity: sensor.coto_digital_unidades
        name: Unidades
      - entity: sensor.coto_digital_total
        name: Total
  - type: horizontal-stack
    cards:
      - type: button
        entity: button.sincronizar_coto_digital
        name: Sincronizar
        icon: mdi:sync
      - type: button
        entity: button.vaciar_carrito_coto_digital
        name: Vaciar
        icon: mdi:delete-empty
```

## Componentes standalone

### 1. Variables de entorno (solo para dashboard/bot)

```bash
export TELEGRAM_BOT_TOKEN="tu_token_aquí"
export TELEGRAM_CHAT_ID="406287065"
```

### 2. Servicios systemd (solo para dashboard/bot)

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
