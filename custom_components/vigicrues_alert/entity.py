"""Shared entity helpers for Vigicrues Alert."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import VigicruesAlertCoordinator


class VigicruesAlertEntity(CoordinatorEntity[VigicruesAlertCoordinator]):
    """Base entity for Vigicrues Alert."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: VigicruesAlertCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer="Vigicrues / Hub'Eau",
            name=coordinator.config_entry.title,
            configuration_url="https://www.vigicrues.gouv.fr/",
        )
