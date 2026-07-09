"""Button entities for Micro Farm."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MicroFarmEntity
from .number import EGGS_TODAY, HARVEST_TODAY_KG
from .runtime import MicroFarmRuntime, get_runtime


@dataclass(frozen=True, kw_only=True)
class MicroFarmButtonDescription(ButtonEntityDescription):
    """Button description."""

    press_fn: Callable[[MicroFarmRuntime], None]


BUTTONS: tuple[MicroFarmButtonDescription, ...] = (
    MicroFarmButtonDescription(
        key="add_egg",
        translation_key="add_egg",
        press_fn=lambda runtime: runtime.add(EGGS_TODAY, 1),
    ),
    MicroFarmButtonDescription(
        key="reset_daily_production",
        translation_key="reset_daily_production",
        press_fn=lambda runtime: (
            runtime.set(EGGS_TODAY, 0, notify=False),
            runtime.set(HARVEST_TODAY_KG, 0),
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons."""
    runtime = get_runtime(hass, entry)
    async_add_entities(MicroFarmButton(runtime, description) for description in BUTTONS)


class MicroFarmButton(MicroFarmEntity, ButtonEntity):
    """Micro Farm action button."""

    entity_description: MicroFarmButtonDescription

    def __init__(
        self,
        runtime: MicroFarmRuntime,
        description: MicroFarmButtonDescription,
    ) -> None:
        super().__init__(runtime)
        self.entity_description = description
        self._attr_unique_id = f"{runtime.config_entry.entry_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        self.entity_description.press_fn(self.runtime)
