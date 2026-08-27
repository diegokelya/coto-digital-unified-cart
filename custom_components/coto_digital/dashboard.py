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
        # Obtener el dashboard storage
        lovelace_config = hass.data.get("lovelace")
        
        if lovelace_config is None:
            _LOGGER.warning("Lovelace config not available, skipping dashboard creation")
            return False
        
        # URL del dashboard
        dashboard_url = "coto-digital"
        
        # Verificar si ya existe
        dashboards = await hass.async_add_executor_job(
            _get_dashboards, hass
        )
        
        if dashboard_url in dashboards:
            _LOGGER.info("Dashboard 'coto-digital' already exists, skipping creation")
            return True
        
        # Crear el dashboard
        await hass.async_add_executor_job(
            _create_dashboard_storage, hass, dashboard_url
        )
        
        _LOGGER.info("Successfully created Coto Digital dashboard at /lovelace/coto-digital")
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to create dashboard: %s", err)
        return False


def _get_dashboards(hass: HomeAssistant) -> dict:
    """Get existing dashboards."""
    try:
        from homeassistant.components.lovelace import dashboard
        return dashboard.LovelaceConfig.async_get_dashboards(hass)
    except Exception:
        return {}


def _create_dashboard_storage(hass: HomeAssistant, url: str) -> None:
    """Create dashboard in storage."""
    try:
        from homeassistant.components.lovelace import dashboard
        from homeassistant.helpers import storage
        
        # Crear configuración del dashboard
        config = {
            "mode": "storage",
            "require_admin": DASHBOARD_CONFIG["require_admin"],
            "show_in_sidebar": DASHBOARD_CONFIG["show_in_sidebar"],
            "icon": DASHBOARD_CONFIG["icon"],
            "title": DASHBOARD_CONFIG["title"],
            "url_path": url,
        }
        
        # Guardar en storage
        store = storage.Store(hass, 1, f"lovelace.{url}")
        
        # Crear vista
        lovelace_data = {
            "views": [DASHBOARD_VIEW],
        }
        
        # Guardar dashboard
        hass.loop.create_task(store.async_save(lovelace_data))
        
        # Registrar dashboard en frontend
        if "lovelace" in hass.data:
            lovelace_config = hass.data["lovelace"]
            if hasattr(lovelace_config, "_dashboards"):
                lovelace_config._dashboards[url] = dashboard.LovelaceDashboard(
                    hass=hass,
                    url_path=url,
                    **config
                )
        
        _LOGGER.info("Dashboard storage created successfully")
        
    except Exception as err:
        _LOGGER.error("Error creating dashboard storage: %s", err)


async def async_remove_dashboard(hass: HomeAssistant) -> bool:
    """Remove Lovelace dashboard."""
    try:
        from homeassistant.helpers import storage
        
        url = "coto-digital"
        store = storage.Store(hass, 1, f"lovelace.{url}")
        
        # Eliminar del storage
        await store.async_remove()
        
        # Eliminar del registro
        if "lovelace" in hass.data:
            lovelace_config = hass.data["lovelace"]
            if hasattr(lovelace_config, "_dashboards") and url in lovelace_config._dashboards:
                del lovelace_config._dashboards[url]
        
        _LOGGER.info("Successfully removed Coto Digital dashboard")
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to remove dashboard: %s", err)
        return False
