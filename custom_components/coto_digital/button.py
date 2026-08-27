"""Button platform for Coto Digital."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Coto Digital buttons from a config entry."""
    
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    
    buttons = [
        CotoDigitalVaciarCarritoButton(api, entry),
        CotoDigitalSincronizarButton(api, entry),
    ]
    
    async_add_entities(buttons)


class CotoDigitalVaciarCarritoButton(ButtonEntity):
    """Botón para vaciar el carrito."""

    def __init__(self, api, entry):
        """Initialize the button."""
        self._api = api
        self._attr_name = "Vaciar Carrito Coto Digital"
        self._attr_unique_id = f"{entry.entry_id}_vaciar_carrito"
        self._attr_icon = "mdi:delete-empty"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Vaciando carrito desde botón")
        await self.hass.async_add_executor_job(self._api.vaciar_carrito)
        self.hass.bus.async_fire(f"{DOMAIN}_carrito_actualizado")


class CotoDigitalSincronizarButton(ButtonEntity):
    """Botón para sincronizar con Coto Digital."""

    def __init__(self, api, entry):
        """Initialize the button."""
        self._api = api
        self._attr_name = "Sincronizar Coto Digital"
        self._attr_unique_id = f"{entry.entry_id}_sincronizar"
        self._attr_icon = "mdi:sync"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Sincronizando desde botón")
        # Aquí iría la lógica de sincronización
        self.hass.bus.async_fire(f"{DOMAIN}_sincronizacion_completada")
