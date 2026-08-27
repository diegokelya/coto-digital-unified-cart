"""Dashboard creation for Coto Digital integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.components import frontend

_LOGGER = logging.getLogger(__name__)

DASHBOARD_CONFIG = {
    "title": "Coto Digital",
    "icon": "mdi:cart",
    "show_in_sidebar": True,
    "require_admin": False,
}

DASHBOARD_VIEW = {
    "title": "Coto Digital",
    "path": "coto-digital",
    "icon": "mdi:cart",
    "badges": [],
    "cards": [
        # Header con estadísticas
        {
            "type": "vertical-stack",
            "cards": [
                {
                    "type": "markdown",
                    "content": "# 🛒 Coto Digital\n## Tu carrito de compras",
                },
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {
                            "type": "entity",
                            "entity": "sensor.coto_digital_productos",
                            "name": "Productos",
                            "icon": "mdi:cart-variant",
                        },
                        {
                            "type": "entity",
                            "entity": "sensor.coto_digital_unidades",
                            "name": "Unidades",
                            "icon": "mdi:package-variant",
                        },
                        {
                            "type": "entity",
                            "entity": "sensor.coto_digital_total",
                            "name": "Total",
                            "icon": "mdi:currency-usd",
                        },
                    ],
                },
            ],
        },
        # Botones de acción
        {
            "type": "entities",
            "title": "Acciones",
            "entities": [
                {
                    "entity": "button.sincronizar_coto_digital",
                    "name": "Sincronizar con Coto Digital",
                    "icon": "mdi:sync",
                },
                {
                    "entity": "button.vaciar_carrito_coto_digital",
                    "name": "Vaciar Carrito",
                    "icon": "mdi:delete-empty",
                },
            ],
        },
        # Servicio de búsqueda
        {
            "type": "entities",
            "title": "Buscar Productos",
            "entities": [
                {
                    "type": "custom:hui-element",
                    "card_type": "button",
                    "name": "Buscar Producto",
                    "icon": "mdi:magnify",
                    "tap_action": {
                        "action": "call-service",
                        "service": "script.coto_buscar_productos",
                    },
                },
            ],
        },
        # Gráfico de total
        {
            "type": "history-graph",
            "title": "Historial de Total",
            "entities": [
                {
                    "entity": "sensor.coto_digital_total",
                },
            ],
            "hours_to_show": 168,
        },
        # Servicios disponibles
        {
            "type": "markdown",
            "content": """
## Servicios Disponibles

### Buscar Producto
```yaml
service: coto_digital.buscar_producto
data:
  query: "leche"
```

### Agregar al Carrito
```yaml
service: coto_digital.agregar_al_carrito
data:
  producto_id: "prod_123"
  nombre: "Leche 1L"
  precio: 450.50
  cantidad: 2
```

### Eliminar del Carrito
```yaml
service: coto_digital.eliminar_del_carrito
data:
  producto_id: "prod_123"
```

### Vaciar Carrito
```yaml
service: coto_digital.vaciar_carrito
```
            """,
        },
    ],
}


async def async_create_dashboard(hass: HomeAssistant) -> bool:
    """Create Lovelace dashboard for Coto Digital."""
    try:
        _LOGGER.info("Starting Coto Digital dashboard creation")
        
        # Método simplificado - usar solo storage directo
        # No depender de lovelace.dashboard que puede no estar disponible
        
        url = "coto-digital"
        
        # Verificar si ya existe
        from homeassistant.helpers import storage
        store = storage.Store(hass, 1, f"lovelace.{url}")
        
        try:
            existing = await store.async_load()
            if existing:
                _LOGGER.info("Dashboard 'coto-digital' already exists, skipping creation")
                return True
        except Exception:
            # No existe, continuar con creación
            pass
        
        # Crear vista del dashboard
        lovelace_data = {
            "views": [DASHBOARD_VIEW],
        }
        
        # Guardar dashboard
        await store.async_save(lovelace_data)
        
        _LOGGER.info("Successfully created Coto Digital dashboard at /lovelace/coto-digital")
        _LOGGER.info("Dashboard will be available after Home Assistant restart")
        
        # Intentar registrar en lovelace_dashboards (opcional)
        try:
            await _register_dashboard(hass, url)
        except Exception as err:
            _LOGGER.warning("Could not register dashboard in sidebar (will still be accessible): %s", err)
        
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to create dashboard: %s", err, exc_info=True)
        return False


async def _register_dashboard(hass: HomeAssistant, url: str) -> None:
    """Register dashboard in lovelace_dashboards for sidebar visibility."""
    try:
        from homeassistant.helpers import storage
        
        store = storage.Store(hass, 1, "lovelace_dashboards")
        
        # Cargar dashboards existentes
        data = await store.async_load()
        
        if data is None:
            data = {"items": []}
        
        items = data.get("items", [])
        
        # Verificar si ya existe
        if any(item.get("url_path") == url for item in items):
            _LOGGER.debug("Dashboard already registered in sidebar")
            return
        
        # Agregar nuevo dashboard
        from datetime import datetime
        new_dashboard = {
            "id": f"coto_digital_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "url_path": url,
            "require_admin": False,
            "show_in_sidebar": True,
            "icon": "mdi:cart",
            "title": "Coto Digital",
        }
        
        items.append(new_dashboard)
        data["items"] = items
        
        await store.async_save(data)
        
        _LOGGER.info("Dashboard registered in sidebar")
        
    except Exception as err:
        _LOGGER.warning("Failed to register dashboard: %s", err)


async def async_remove_dashboard(hass: HomeAssistant) -> bool:
    """Remove Lovelace dashboard."""
    try:
        from homeassistant.helpers import storage
        
        url = "coto-digital"
        store = storage.Store(hass, 1, f"lovelace.{url}")
        
        # Eliminar del storage
        await store.async_remove()
        
        # Eliminar del registro de dashboards
        try:
            dashboards_store = storage.Store(hass, 1, "lovelace_dashboards")
            data = await dashboards_store.async_load()
            
            if data and "items" in data:
                items = data["items"]
                data["items"] = [item for item in items if item.get("url_path") != url]
                await dashboards_store.async_save(data)
        except Exception:
            pass  # No crítico si falla
        
        _LOGGER.info("Successfully removed Coto Digital dashboard")
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to remove dashboard: %s", err)
        return False
