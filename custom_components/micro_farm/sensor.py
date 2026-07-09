"""Sensors for Micro Farm."""

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
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DAILY_FEED_KG,
    CONF_DAILY_WATER_L,
    CONF_DRY_SOIL_PERCENT,
    CONF_LOW_BATTERY_PERCENT,
    CONF_LOW_FEED_DAYS,
    CONF_LOW_WATER_DAYS,
)
from .entity import MicroFarmEntity
from .number import (
    BATTERY_PERCENT,
    EGGS_TODAY,
    FEED_STOCK_KG,
    HARVEST_TODAY_KG,
    SOIL_MOISTURE_PERCENT,
    WATER_STOCK_L,
)
from .runtime import MicroFarmRuntime, get_runtime


@dataclass(frozen=True, kw_only=True)
class MicroFarmSensorDescription(SensorEntityDescription):
    """Sensor description."""

    value_fn: Callable[[MicroFarmRuntime], Any]
    attrs_fn: Callable[[MicroFarmRuntime], dict[str, Any]] | None = None


def _days(stock: float, daily_use: float) -> float | None:
    """Return autonomy in days."""
    if daily_use <= 0:
        return None
    return round(stock / daily_use, 1)


def _minimum_autonomy(runtime: MicroFarmRuntime) -> float | None:
    """Return the shortest physical-stock autonomy."""
    data = runtime.data
    values = [
        _days(runtime.get(FEED_STOCK_KG), data[CONF_DAILY_FEED_KG]),
        _days(runtime.get(WATER_STOCK_L), data[CONF_DAILY_WATER_L]),
    ]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return min(values)


def _status(runtime: MicroFarmRuntime) -> str:
    """Return a compact status."""
    data = runtime.data
    water_days = _days(runtime.get(WATER_STOCK_L), data[CONF_DAILY_WATER_L])
    feed_days = _days(runtime.get(FEED_STOCK_KG), data[CONF_DAILY_FEED_KG])
    if runtime.get(BATTERY_PERCENT) <= data[CONF_LOW_BATTERY_PERCENT]:
        return "battery_low"
    if water_days is not None and water_days <= data[CONF_LOW_WATER_DAYS]:
        return "water_low"
    if feed_days is not None and feed_days <= data[CONF_LOW_FEED_DAYS]:
        return "feed_low"
    if runtime.get(SOIL_MOISTURE_PERCENT) <= data[CONF_DRY_SOIL_PERCENT]:
        return "soil_dry"
    return "ok"


SENSORS: tuple[MicroFarmSensorDescription, ...] = (
    MicroFarmSensorDescription(
        key="feed_autonomy",
        translation_key="feed_autonomy",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda runtime: _days(
            runtime.get(FEED_STOCK_KG),
            runtime.data[CONF_DAILY_FEED_KG],
        ),
    ),
    MicroFarmSensorDescription(
        key="water_autonomy",
        translation_key="water_autonomy",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda runtime: _days(
            runtime.get(WATER_STOCK_L),
            runtime.data[CONF_DAILY_WATER_L],
        ),
    ),
    MicroFarmSensorDescription(
        key="minimum_autonomy",
        translation_key="minimum_autonomy",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=_minimum_autonomy,
    ),
    MicroFarmSensorDescription(
        key="production_status",
        translation_key="production_status",
        value_fn=_status,
        attrs_fn=lambda runtime: {
            "eggs_today": runtime.get(EGGS_TODAY),
            "harvest_today_kg": runtime.get(HARVEST_TODAY_KG),
            "feed_stock_kg": runtime.get(FEED_STOCK_KG),
            "water_stock_l": runtime.get(WATER_STOCK_L),
            "battery_percent": runtime.get(BATTERY_PERCENT),
            "soil_moisture_percent": runtime.get(SOIL_MOISTURE_PERCENT),
        },
    ),
    MicroFarmSensorDescription(
        key="eggs_today_readonly",
        translation_key="eggs_today_readonly",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda runtime: runtime.get(EGGS_TODAY),
    ),
    MicroFarmSensorDescription(
        key="harvest_today_readonly",
        translation_key="harvest_today_readonly",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement="kg",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda runtime: runtime.get(HARVEST_TODAY_KG),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    runtime = get_runtime(hass, entry)
    async_add_entities(MicroFarmSensor(runtime, description) for description in SENSORS)


class MicroFarmSensor(MicroFarmEntity, SensorEntity):
    """Computed Micro Farm sensor."""

    entity_description: MicroFarmSensorDescription

    def __init__(
        self,
        runtime: MicroFarmRuntime,
        description: MicroFarmSensorDescription,
    ) -> None:
        super().__init__(runtime)
        self.entity_description = description
        self._attr_unique_id = f"{runtime.config_entry.entry_id}_{description.key}"

    async def async_added_to_hass(self) -> None:
        """Register runtime update listener."""
        await super().async_added_to_hass()
        remove_listener = async_dispatcher_connect(
            self.hass,
            self.runtime.signal,
            self._handle_runtime_update,
        )
        self.async_on_remove(remove_listener)

    @property
    def native_value(self) -> Any:
        """Return sensor state."""
        return self.entity_description.value_fn(self.runtime)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.runtime)

    @callback
    def _handle_runtime_update(self) -> None:
        """Handle runtime updates."""
        self.async_write_ha_state()
