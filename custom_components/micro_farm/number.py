"""Number entities for Micro Farm."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfMass, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import MicroFarmEntity
from .runtime import MicroFarmRuntime, get_runtime


@dataclass(frozen=True, kw_only=True)
class MicroFarmNumberDescription(NumberEntityDescription):
    """Number description."""

    initial_value: float = 0.0


EGGS_TODAY = "eggs_today"
HARVEST_TODAY_KG = "harvest_today_kg"
FEED_STOCK_KG = "feed_stock_kg"
WATER_STOCK_L = "water_stock_l"
BATTERY_PERCENT = "battery_percent"
SOIL_MOISTURE_PERCENT = "soil_moisture_percent"

NUMBERS: tuple[MicroFarmNumberDescription, ...] = (
    MicroFarmNumberDescription(
        key=EGGS_TODAY,
        translation_key=EGGS_TODAY,
        native_min_value=0,
        native_max_value=500,
        native_step=1,
        mode=NumberMode.BOX,
    ),
    MicroFarmNumberDescription(
        key=HARVEST_TODAY_KG,
        translation_key=HARVEST_TODAY_KG,
        native_min_value=0,
        native_max_value=500,
        native_step=0.1,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        mode=NumberMode.BOX,
    ),
    MicroFarmNumberDescription(
        key=FEED_STOCK_KG,
        translation_key=FEED_STOCK_KG,
        native_min_value=0,
        native_max_value=1000,
        native_step=0.1,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        mode=NumberMode.BOX,
    ),
    MicroFarmNumberDescription(
        key=WATER_STOCK_L,
        translation_key=WATER_STOCK_L,
        native_min_value=0,
        native_max_value=10000,
        native_step=1,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        mode=NumberMode.BOX,
    ),
    MicroFarmNumberDescription(
        key=BATTERY_PERCENT,
        translation_key=BATTERY_PERCENT,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        initial_value=100,
        mode=NumberMode.SLIDER,
    ),
    MicroFarmNumberDescription(
        key=SOIL_MOISTURE_PERCENT,
        translation_key=SOIL_MOISTURE_PERCENT,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        initial_value=50,
        mode=NumberMode.SLIDER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    runtime = get_runtime(hass, entry)
    async_add_entities(MicroFarmNumber(runtime, description) for description in NUMBERS)


class MicroFarmNumber(MicroFarmEntity, NumberEntity, RestoreEntity):
    """Editable production or stock value."""

    entity_description: MicroFarmNumberDescription

    def __init__(
        self,
        runtime: MicroFarmRuntime,
        description: MicroFarmNumberDescription,
    ) -> None:
        super().__init__(runtime)
        self.entity_description = description
        self._attr_unique_id = f"{runtime.config_entry.entry_id}_{description.key}"

    async def async_added_to_hass(self) -> None:
        """Restore previous value."""
        await super().async_added_to_hass()
        value = self.entity_description.initial_value
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                value = float(last_state.state)
            except ValueError:
                value = self.entity_description.initial_value
        self.runtime.set(self.entity_description.key, value, notify=False)

        remove_listener = async_dispatcher_connect(
            self.hass,
            self.runtime.signal,
            self._handle_runtime_update,
        )
        self.async_on_remove(remove_listener)

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self.runtime.get(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        """Set the current value."""
        self.runtime.set(self.entity_description.key, value)
        self.async_write_ha_state()

    @callback
    def _handle_runtime_update(self) -> None:
        """Handle runtime updates."""
        self.async_write_ha_state()
