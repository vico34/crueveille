"""Binary sensors for Vigicrues Alert."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ALERT_LEVEL, DEFAULT_ALERT_LEVEL, DOMAIN, RISK_ORDER
from .coordinator import VigicruesAlertCoordinator, utc_iso
from .entity import VigicruesAlertEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator: VigicruesAlertCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VigicruesFloodAlertBinarySensor(coordinator)])


class VigicruesFloodAlertBinarySensor(VigicruesAlertEntity, BinarySensorEntity):
    """Flood alert binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_translation_key = "flood_alert"

    def __init__(self, coordinator: VigicruesAlertCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_flood_alert"

    @property
    def is_on(self) -> bool:
        """Return true if local risk reached configured alert level."""
        alert_level = self.coordinator.config_entry.data.get(
            CONF_ALERT_LEVEL,
            DEFAULT_ALERT_LEVEL,
        )
        return RISK_ORDER[self.coordinator.data.risk_level] >= RISK_ORDER[alert_level]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        data = self.coordinator.data
        return {
            "risk_level": data.risk_level,
            "alert_reason": data.alert_reason,
            "station_code": data.station.code,
            "station_name": data.station.label,
            "height_observed_at": utc_iso(data.height_observed_at),
            "water_level_m": data.water_level_m,
            "rise_cm_h": data.rise_cm_h,
            "forecast_height_m": data.forecast_height_m,
        }
