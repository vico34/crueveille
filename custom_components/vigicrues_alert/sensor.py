"""Sensors for Vigicrues Alert."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VigicruesAlertCoordinator, VigicruesAlertData, utc_iso
from .entity import VigicruesAlertEntity

CM_PER_HOUR = "cm/h"
M3_PER_SECOND = "m3/s"
KM = "km"


@dataclass(frozen=True, kw_only=True)
class VigicruesSensorDescription(SensorEntityDescription):
    """Sensor description."""

    value_fn: Callable[[VigicruesAlertData], Any]


SENSORS: tuple[VigicruesSensorDescription, ...] = (
    VigicruesSensorDescription(
        key="water_level",
        translation_key="water_level",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: data.water_level_m,
    ),
    VigicruesSensorDescription(
        key="flow",
        translation_key="flow",
        native_unit_of_measurement=M3_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.flow_m3_s,
    ),
    VigicruesSensorDescription(
        key="rise_rate",
        translation_key="rise_rate",
        native_unit_of_measurement=CM_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.rise_cm_h,
    ),
    VigicruesSensorDescription(
        key="forecast_height",
        translation_key="forecast_height",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: data.forecast_height_m,
    ),
    VigicruesSensorDescription(
        key="risk_level",
        translation_key="risk_level",
        value_fn=lambda data: data.risk_level,
    ),
    VigicruesSensorDescription(
        key="station_distance",
        translation_key="station_distance",
        native_unit_of_measurement=KM,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.station.distance_km,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: VigicruesAlertCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        VigicruesSensor(coordinator, description) for description in SENSORS
    )


class VigicruesSensor(VigicruesAlertEntity, SensorEntity):
    """Vigicrues computed sensor."""

    entity_description: VigicruesSensorDescription

    def __init__(
        self,
        coordinator: VigicruesAlertCoordinator,
        description: VigicruesSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{description.key}"
        )

    @property
    def native_value(self) -> Any:
        """Return sensor state."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        data = self.coordinator.data
        return {
            "station_code": data.station.code,
            "station_name": data.station.label,
            "station_latitude": data.station.latitude,
            "station_longitude": data.station.longitude,
            "height_observed_at": utc_iso(data.height_observed_at),
            "flow_observed_at": utc_iso(data.flow_observed_at),
            "alert_reason": data.alert_reason,
        }
