"""The Coto Digital integration."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN,
    DB_NAME,
    SERVICE_BUSCAR,
    SERVICE_AGREGAR,
    SERVICE_ELIMINAR,
    SERVICE_VACIAR,
    SERVICE_SINCRONIZAR,
    ATTR_PRODUCTO_ID,
    ATTR_NOMBRE,
    ATTR_PRECIO,
    ATTR_IMAGEN_URL,
    ATTR_CANTIDAD,
)
from .coto_api import CotoDigitalAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

# Schemas para servicios
BUSCAR_SCHEMA = vol.Schema({
    vol.Required("query"): cv.string,
})

AGREGAR_SCHEMA = vol.Schema({
    vol.Required(ATTR_PRODUCTO_ID): cv.string,
    vol.Required(ATTR_NOMBRE): cv.string,
    vol.Required(ATTR_PRECIO): vol.Coerce(float),
    vol.Optional(ATTR_IMAGEN_URL): cv.string,
    vol.Optional(ATTR_CANTIDAD, default=1): vol.Coerce(int),
})

ELIMINAR_SCHEMA = vol.Schema({
    vol.Required(ATTR_PRODUCTO_ID): cv.string,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Coto Digital from a config entry."""
    
    # Crear directorio de datos si no existe
    data_dir = Path(hass.config.config_dir) / "custom_components" / DOMAIN / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = data_dir / DB_NAME
    
    # Inicializar API
    api = CotoDigitalAPI(str(db_path))
    
    # Guardar en hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "db_path": str(db_path),
    }
    
    # Cargar plataformas
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Registrar servicios
    async def handle_buscar(call: ServiceCall) -> None:
        """Handle buscar_producto service."""
        query = call.data.get("query")
        _LOGGER.info("Buscando productos: %s", query)
        
        resultados = await hass.async_add_executor_job(api.buscar_productos, query)
        
        # Disparar evento con resultados
        hass.bus.async_fire(
            f"{DOMAIN}_busqueda_completada",
            {
                "query": query,
                "count": len(resultados),
                "resultados": resultados[:10],  # Primeros 10
            },
        )
    
    async def handle_agregar(call: ServiceCall) -> None:
        """Handle agregar_al_carrito service."""
        producto = {
            "producto_id": call.data[ATTR_PRODUCTO_ID],
            "nombre": call.data[ATTR_NOMBRE],
            "precio": call.data[ATTR_PRECIO],
            "imagen_url": call.data.get(ATTR_IMAGEN_URL, ""),
            "cantidad": call.data.get(ATTR_CANTIDAD, 1),
        }
        
        _LOGGER.info("Agregando al carrito: %s", producto["nombre"])
        
        await hass.async_add_executor_job(api.agregar_al_carrito, producto)
        
        # Actualizar sensores
        hass.bus.async_fire(f"{DOMAIN}_carrito_actualizado")
    
    async def handle_eliminar(call: ServiceCall) -> None:
        """Handle eliminar_del_carrito service."""
        producto_id = call.data[ATTR_PRODUCTO_ID]
        
        _LOGGER.info("Eliminando del carrito: %s", producto_id)
        
        await hass.async_add_executor_job(api.eliminar_del_carrito, producto_id)
        
        # Actualizar sensores
        hass.bus.async_fire(f"{DOMAIN}_carrito_actualizado")
    
    async def handle_vaciar(call: ServiceCall) -> None:
        """Handle vaciar_carrito service."""
        _LOGGER.info("Vaciando carrito")
        
        await hass.async_add_executor_job(api.vaciar_carrito)
        
        # Actualizar sensores
        hass.bus.async_fire(f"{DOMAIN}_carrito_actualizado")
    
    async def handle_sincronizar(call: ServiceCall) -> None:
        """Handle sincronizar service."""
        _LOGGER.info("Sincronizando con Coto Digital")
        
        # Aquí iría la lógica de sincronización
        # Por ahora solo dispara evento
        hass.bus.async_fire(f"{DOMAIN}_sincronizacion_completada")
    
    # Registrar servicios
    hass.services.async_register(DOMAIN, SERVICE_BUSCAR, handle_buscar, schema=BUSCAR_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_AGREGAR, handle_agregar, schema=AGREGAR_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ELIMINAR, handle_eliminar, schema=ELIMINAR_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_VACIAR, handle_vaciar)
    hass.services.async_register(DOMAIN, SERVICE_SINCRONIZAR, handle_sincronizar)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Desregistrar servicios si no hay más entries
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_BUSCAR)
            hass.services.async_remove(DOMAIN, SERVICE_AGREGAR)
            hass.services.async_remove(DOMAIN, SERVICE_ELIMINAR)
            hass.services.async_remove(DOMAIN, SERVICE_VACIAR)
            hass.services.async_remove(DOMAIN, SERVICE_SINCRONIZAR)
    
    return unload_ok
