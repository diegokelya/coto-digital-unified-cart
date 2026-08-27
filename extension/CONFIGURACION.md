# Configuración de la Extensión Chrome

La extensión necesita conocer la URL de tu dashboard de Coto Digital.

## Configuración Requerida

### 1. Editar manifest.json

Abrir `extension/manifest.json` y actualizar la línea de `matches`:

```json
{
  "content_scripts": [
    {
      "matches": [
        "http://YOUR_HA_IP:8766/*",
        "http://homeassistant.local:8766/*"
      ],
      ...
    }
  ]
}
```

Reemplazar `YOUR_HA_IP` con:
- La IP de tu Home Assistant (ej: `192.168.1.100`)
- O usar `homeassistant.local` si tienes mDNS configurado
- O `localhost` si está en la misma máquina

### 2. Editar scripts/sync_coto_dashboard.mjs

```javascript
const DASHBOARD_CONFIG = {
    url: 'http://YOUR_HA_IP:8766/',
    // Cambiar por tu IP o hostname
}
```

### 3. Editar scripts/verify_coto_dashboard.mjs

```javascript
interactive: iframe?.url === 'http://YOUR_HA_IP:8766/',
// Cambiar por tu IP o hostname
```

## Ejemplos de Configuración

### Usando IP Local
```json
"matches": ["http://192.168.1.50:8766/*"]
```

### Usando mDNS (Recomendado)
```json
"matches": ["http://homeassistant.local:8766/*"]
```

### Usando Localhost (mismo equipo)
```json
"matches": ["http://localhost:8766/*"]
```

### Múltiples URLs (Recomendado)
```json
"matches": [
  "http://homeassistant.local:8766/*",
  "http://localhost:8766/*",
  "http://192.168.1.50:8766/*"
]
```

## Encontrar tu IP de Home Assistant

### Opción 1: Desde la UI
1. Configuración → Sistema → Red
2. Buscar "IPv4"

### Opción 2: Desde terminal
```bash
# En el servidor de HA
hostname -I

# O
ip addr show | grep inet
```

### Opción 3: Desde router
1. Acceder al router (usualmente 192.168.1.1)
2. Buscar dispositivos conectados
3. Encontrar "Home Assistant" o "homeassistant"

## Troubleshooting

### La extensión no se activa

1. Verificar que la URL en `manifest.json` coincida exactamente
2. Recargar la extensión: `chrome://extensions/` → Clic en ↻
3. Verificar que el dashboard esté corriendo:
   ```bash
   curl http://YOUR_HA_IP:8766/api/carrito
   ```

### CORS errors

Si ves errores de CORS en la consola, asegúrate de que `coto_dashboard_web.py` tenga:

```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
```

## Seguridad

⚠️ **No hacer público el repositorio con tu IP local configurada**

Si vas a hacer fork o compartir:
1. Usar variables de entorno
2. Usar placeholders genéricos
3. Documentar en README cómo configurar

## Alternativa: Variable de Entorno

Editar `extension/dashboard.js`:

```javascript
const DASHBOARD_URL = process.env.COTO_DASHBOARD_URL || 'http://homeassistant.local:8766';
```

O crear archivo `extension/config.js` (ignorado en .gitignore):

```javascript
// config.js
export const DASHBOARD_URL = 'http://192.168.1.50:8766';
```

Y importar en otros archivos:
```javascript
import { DASHBOARD_URL } from './config.js';
```
