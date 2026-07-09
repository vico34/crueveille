"""Shared entity helpers for Micro Farm."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .runtime import MicroFarmRuntime


class MicroFarmEntity:
    """Base entity for Micro Farm."""

    _attr_has_entity_name = True

    def __init__(self, runtime: MicroFarmRuntime) -> None:
        self.runtime = runtime
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, runtime.config_entry.entry_id)},
            manufacturer="Micro Farm",
            name=runtime.config_entry.title,
        )
