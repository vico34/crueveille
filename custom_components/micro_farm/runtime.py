"""Runtime state for the Micro Farm integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, SIGNAL_UPDATE


@dataclass
class MicroFarmRuntime:
    """Hold user-maintained production and stock values."""

    hass: HomeAssistant
    config_entry: ConfigEntry
    values: dict[str, float] = field(default_factory=dict)

    def get(self, key: str) -> float:
        """Return a tracked value."""
        return self.values.get(key, 0.0)

    def set(self, key: str, value: float, *, notify: bool = True) -> None:
        """Set a tracked value."""
        self.values[key] = max(0.0, float(value))
        if notify:
            async_dispatcher_send(self.hass, self.signal)

    def add(self, key: str, delta: float) -> None:
        """Increment a tracked value."""
        self.set(key, self.get(key) + delta)

    @property
    def signal(self) -> str:
        """Return the dispatcher signal for this entry."""
        return f"{SIGNAL_UPDATE}_{self.config_entry.entry_id}"

    @property
    def data(self) -> dict[str, Any]:
        """Return merged config data and options."""
        return {**self.config_entry.data, **self.config_entry.options}


def get_runtime(hass: HomeAssistant, entry: ConfigEntry) -> MicroFarmRuntime:
    """Return the runtime object for a config entry."""
    return hass.data[DOMAIN][entry.entry_id]
