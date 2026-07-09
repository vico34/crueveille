"""Binary sensors for Micro Farm."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
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
from .number import BATTERY_PERCENT, FEED_STOCK_KG, SOIL_MOISTURE_PERCENT, WATER_STOCK_L
from .runtime import MicroFarmRuntime, get_runtime


@dataclass(frozen=True, kw_only=True)
class MicroFarmBinarySensorDescription(BinarySensorEntityDescription):
    """Binary sensor description."""

    is_on_fn: Callable[[MicroFarmRuntime], bool]


def _low_stock_days(stock: float, daily_use: float, threshold_days: float) -> bool:
    """Return true when a stock is at or below its day threshold."""
    if daily_use <= 0:
        return False
    return stock / daily_use <= threshold_days


BINARY_SENSORS: tuple[MicroFarmBinarySensorDescription, ...] = (
    MicroFarmBinarySensorDescription(
        key="feed_low",
        translation_key="feed_low",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda runtime: _low_stock_days(
            runtime.get(FEED_STOCK_KG),
            runtime.data[CONF_DAILY_FEED_KG],
            runtime.data[CONF_LOW_FEED_DAYS],
        ),
    ),
    MicroFarmBinarySensorDescription(
        key="water_low",
        translation_key="water_low",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda runtime: _low_stock_days(
            runtime.get(WATER_STOCK_L),
            runtime.data[CONF_DAILY_WATER_L],
            runtime.data[CONF_LOW_WATER_DAYS],
        ),
    ),
    MicroFarmBinarySensorDescription(
        key="battery_low",
        translation_key="battery_low",
        device_class=BinarySensorDeviceClass.BATTERY,
        is_on_fn=lambda runtime: runtime.get(BATTERY_PERCENT)
        <= runtime.data[CONF_LOW_BATTERY_PERCENT],
    ),
    MicroFarmBinarySensorDescription(
        key="soil_dry",
        translation_key="soil_dry",
        device_class=BinarySensorDeviceClass.MOISTURE,
        is_on_fn=lambda runtime: runtime.get(SOIL_MOISTURE_PERCENT)
        <= runtime.data[CONF_DRY_SOIL_PERCENT],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    runtime = get_runtime(hass, entry)
    async_add_entities(
        MicroFarmBinarySensor(runtime, description) for description in BINARY_SENSORS
    )


class MicroFarmBinarySensor(MicroFarmEntity, BinarySensorEntity):
    """Micro Farm alert binary sensor."""

    entity_description: MicroFarmBinarySensorDescription

    def __init__(
        self,
        runtime: MicroFarmRuntime,
        description: MicroFarmBinarySensorDescription,
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
    def is_on(self) -> bool:
        """Return true when the alert condition is active."""
        return self.entity_description.is_on_fn(self.runtime)

    @callback
    def _handle_runtime_update(self) -> None:
        """Handle runtime updates."""
        self.async_write_ha_state()
