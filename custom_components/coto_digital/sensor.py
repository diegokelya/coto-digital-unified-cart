"""Sensor platform for Coto Digital."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Coto Digital sensors from a config entry."""
    
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    
    # Crear coordinador de actualización
    async def async_update_data():
        """Fetch data from API."""
        return await hass.async_add_executor_job(api.obtener_estadisticas)
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Crear sensores
    sensors = [
        CotoDigitalProductCountSensor(coordinator, entry),
        CotoDigitalUnitCountSensor(coordinator, entry),
        CotoDigitalTotalPriceSensor(coordinator, entry),
    ]
    
    async_add_entities(sensors)


class CotoDigitalProductCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor que muestra cantidad de productos diferentes en el carrito."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Coto Digital Productos"
        self._attr_unique_id = f"{entry.entry_id}_productos_count"
        self._attr_icon = "mdi:cart"
        self._attr_native_unit_of_measurement = "productos"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("productos_count", 0)


class CotoDigitalUnitCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor que muestra cantidad total de unidades en el carrito."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Coto Digital Unidades"
        self._attr_unique_id = f"{entry.entry_id}_unidades_count"
        self._attr_icon = "mdi:package-variant"
        self._attr_native_unit_of_measurement = "unidades"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("total_unidades", 0)


class CotoDigitalTotalPriceSensor(CoordinatorEntity, SensorEntity):
    """Sensor que muestra el total en pesos del carrito."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Coto Digital Total"
        self._attr_unique_id = f"{entry.entry_id}_total_precio"
        self._attr_icon = "mdi:currency-usd"
        self._attr_native_unit_of_measurement = "ARS"
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("total_precio", 0.0)
    
    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "productos": self.coordinator.data.get("productos_count", 0),
            "unidades": self.coordinator.data.get("total_unidades", 0),
        }
