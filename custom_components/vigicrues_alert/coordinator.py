"""Data coordinator for Vigicrues Alert."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from statistics import mean

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import Observation, Station, VigicruesApiClient, VigicruesApiError
from .const import (
    CONF_CRITICAL_HEIGHT_M,
    CONF_CRITICAL_RISE_CM_H,
    CONF_FORECAST_HOURS,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS_KM,
    CONF_STATION_CODE,
    CONF_WARNING_HEIGHT_M,
    CONF_WARNING_RISE_CM_H,
    DEFAULT_CRITICAL_RISE_CM_H,
    DEFAULT_FORECAST_HOURS,
    DEFAULT_RADIUS_KM,
    DEFAULT_WARNING_RISE_CM_H,
    DOMAIN,
    RISK_CLEAR,
    RISK_CRITICAL,
    RISK_WATCH,
    RISK_WARNING,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class VigicruesAlertData:
    """Current station data and computed risk."""

    station: Station
    water_level_m: float | None
    flow_m3_s: float | None
    height_observed_at: datetime | None
    flow_observed_at: datetime | None
    rise_cm_h: float | None
    forecast_height_m: float | None
    risk_level: str
    alert_reason: str


class VigicruesAlertCoordinator(DataUpdateCoordinator[VigicruesAlertData]):
    """Fetch data from Hub'Eau and compute local alert state."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
        )
        self._client = VigicruesApiClient(async_get_clientsession(hass))
        self._station: Station | None = None

    async def _async_update_data(self) -> VigicruesAlertData:
        try:
            station = await self._async_station()
            height_obs = await self._client.observations(station.code, "H")
            flow_obs = await self._client.observations(station.code, "Q")
            return self._build_data(station, height_obs, flow_obs)
        except VigicruesApiError as err:
            raise UpdateFailed(str(err)) from err
        except (KeyError, TypeError, ValueError) as err:
            raise ConfigEntryError(f"Configuration Vigicrues invalide: {err}") from err

    async def _async_station(self) -> Station:
        if self._station is not None:
            return self._station

        station_code = self.config_entry.data.get(CONF_STATION_CODE)
        if station_code:
            self._station = await self._client.get_station(station_code)
            return self._station

        latitude = float(self.config_entry.data[CONF_LATITUDE])
        longitude = float(self.config_entry.data[CONF_LONGITUDE])
        radius_km = float(self.config_entry.data.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM))
        self._station = await self._client.find_nearest_station(
            latitude,
            longitude,
            radius_km,
        )
        return self._station

    def _build_data(
        self,
        station: Station,
        height_obs: list[Observation],
        flow_obs: list[Observation],
    ) -> VigicruesAlertData:
        latest_height = height_obs[0] if height_obs else None
        latest_flow = flow_obs[0] if flow_obs else None

        water_level_m = latest_height.value / 1000 if latest_height else None
        flow_m3_s = latest_flow.value / 1000 if latest_flow else None
        rise_cm_h = _rise_cm_per_hour(height_obs)

        forecast_hours = int(
            self.config_entry.data.get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS)
        )
        forecast_height_m = None
        if water_level_m is not None and rise_cm_h is not None:
            forecast_height_m = water_level_m + (rise_cm_h / 100) * forecast_hours

        risk_level, alert_reason = self._risk_level(
            water_level_m,
            rise_cm_h,
            forecast_height_m,
        )

        return VigicruesAlertData(
            station=station,
            water_level_m=water_level_m,
            flow_m3_s=flow_m3_s,
            height_observed_at=latest_height.observed_at if latest_height else None,
            flow_observed_at=latest_flow.observed_at if latest_flow else None,
            rise_cm_h=rise_cm_h,
            forecast_height_m=forecast_height_m,
            risk_level=risk_level,
            alert_reason=alert_reason,
        )

    def _risk_level(
        self,
        water_level_m: float | None,
        rise_cm_h: float | None,
        forecast_height_m: float | None,
    ) -> tuple[str, str]:
        warning_height = self.config_entry.data.get(CONF_WARNING_HEIGHT_M)
        critical_height = self.config_entry.data.get(CONF_CRITICAL_HEIGHT_M)
        warning_rise = float(
            self.config_entry.data.get(
                CONF_WARNING_RISE_CM_H,
                DEFAULT_WARNING_RISE_CM_H,
            )
        )
        critical_rise = float(
            self.config_entry.data.get(
                CONF_CRITICAL_RISE_CM_H,
                DEFAULT_CRITICAL_RISE_CM_H,
            )
        )

        if water_level_m is None:
            return RISK_WATCH, "aucune hauteur d'eau recente"

        if critical_height is not None and water_level_m >= float(critical_height):
            return RISK_CRITICAL, "hauteur critique atteinte"

        if critical_height is not None and forecast_height_m is not None:
            if forecast_height_m >= float(critical_height):
                return RISK_CRITICAL, "hauteur critique anticipee"

        if rise_cm_h is not None and rise_cm_h >= critical_rise:
            return RISK_CRITICAL, "montee tres rapide"

        if warning_height is not None and water_level_m >= float(warning_height):
            return RISK_WARNING, "hauteur de vigilance atteinte"

        if warning_height is not None and forecast_height_m is not None:
            if forecast_height_m >= float(warning_height):
                return RISK_WARNING, "hauteur de vigilance anticipee"

        if rise_cm_h is not None and rise_cm_h >= warning_rise:
            return RISK_WARNING, "montee rapide"

        if rise_cm_h is not None and rise_cm_h > 0:
            return RISK_WATCH, "niveau en hausse"

        return RISK_CLEAR, "pas de signal local"


def _rise_cm_per_hour(observations: list[Observation]) -> float | None:
    """Compute a robust recent trend in centimeters per hour."""
    if len(observations) < 2:
        return None

    newest = observations[0]
    candidates = [
        obs
        for obs in observations[1:]
        if (newest.observed_at - obs.observed_at).total_seconds() >= 1800
    ]
    if not candidates:
        return None

    oldest = candidates[-1]
    hours = (newest.observed_at - oldest.observed_at).total_seconds() / 3600
    if hours <= 0:
        return None

    direct_slope = ((newest.value - oldest.value) / 10) / hours
    pairwise_slopes = []
    ordered = list(reversed(observations))
    for previous, current in zip(ordered, ordered[1:], strict=False):
        delta_h = (current.observed_at - previous.observed_at).total_seconds() / 3600
        if delta_h > 0:
            pairwise_slopes.append(((current.value - previous.value) / 10) / delta_h)

    if not pairwise_slopes:
        return round(direct_slope, 2)
    return round(mean([direct_slope, mean(pairwise_slopes)]), 2)


def utc_iso(value: datetime | None) -> str | None:
    """Return an ISO timestamp for extra state attributes."""
    if value is None:
        return None
    return value.astimezone(UTC).isoformat()
