"""Config flow for Vigicrues Alert."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_ALERT_LEVEL,
    CONF_CRITICAL_HEIGHT_M,
    CONF_CRITICAL_RISE_CM_H,
    CONF_FORECAST_HOURS,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS_KM,
    CONF_STATION_CODE,
    CONF_WARNING_HEIGHT_M,
    CONF_WARNING_RISE_CM_H,
    DEFAULT_ALERT_LEVEL,
    DEFAULT_CRITICAL_RISE_CM_H,
    DEFAULT_FORECAST_HOURS,
    DEFAULT_RADIUS_KM,
    DEFAULT_WARNING_RISE_CM_H,
    DOMAIN,
    RISK_CRITICAL,
    RISK_WARNING,
)


class VigicruesAlertConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vigicrues Alert."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = _clean_input(user_input)
            try:
                title = await self._validate_and_title(user_input)
            except ValueError as err:
                errors["base"] = str(err)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(_unique_id(user_input))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ):
        """Return the options flow."""
        return VigicruesAlertOptionsFlow(config_entry)

    def _schema(self, user_input: dict[str, Any] | None = None) -> vol.Schema:
        defaults = user_input or {}
        return _schema(
            defaults,
            default_latitude=self.hass.config.latitude,
            default_longitude=self.hass.config.longitude,
        )

    async def _validate_and_title(self, user_input: dict[str, Any]) -> str:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        from .api import VigicruesApiClient

        client = VigicruesApiClient(async_get_clientsession(self.hass))
        station_code = user_input.get(CONF_STATION_CODE)
        if station_code:
            station = await client.get_station(station_code)
        else:
            latitude = user_input.get(CONF_LATITUDE)
            longitude = user_input.get(CONF_LONGITUDE)
            if latitude is None or longitude is None:
                raise ValueError("missing_location")
            station = await client.find_nearest_station(
                float(latitude),
                float(longitude),
                float(user_input[CONF_RADIUS_KM]),
            )
        name = user_input.get(CONF_NAME)
        return name or f"Vigicrues {station.label}"


class VigicruesAlertOptionsFlow(config_entries.OptionsFlow):
    """Handle Vigicrues Alert options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Manage options by replacing the config entry data."""
        if user_input is not None:
            data = dict(self._config_entry.data)
            data.update(_clean_input(user_input))
            self.hass.config_entries.async_update_entry(self._config_entry, data=data)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                dict(self._config_entry.data),
                default_latitude=self.hass.config.latitude,
                default_longitude=self.hass.config.longitude,
                include_name=False,
            ),
        )


def _schema(
    defaults: dict[str, Any],
    *,
    default_latitude: float,
    default_longitude: float,
    include_name: bool = True,
) -> vol.Schema:
    fields: dict[Any, Any] = {}
    latitude = defaults.get(CONF_LATITUDE, default_latitude)
    longitude = defaults.get(CONF_LONGITUDE, default_longitude)
    if latitude is None:
        latitude = 46.6
    if longitude is None:
        longitude = 2.4

    if include_name:
        fields[vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, ""))] = str

    fields.update(
        {
            vol.Optional(
                CONF_STATION_CODE,
                default=defaults.get(CONF_STATION_CODE, ""),
            ): str,
            vol.Optional(
                CONF_LATITUDE,
                default=latitude,
            ): vol.Coerce(float),
            vol.Optional(
                CONF_LONGITUDE,
                default=longitude,
            ): vol.Coerce(float),
            vol.Optional(
                CONF_RADIUS_KM,
                default=defaults.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM),
            ): vol.All(vol.Coerce(float), vol.Range(min=1, max=100)),
            vol.Optional(
                CONF_WARNING_HEIGHT_M,
                default=defaults.get(CONF_WARNING_HEIGHT_M, ""),
            ): vol.Any("", vol.Coerce(float)),
            vol.Optional(
                CONF_CRITICAL_HEIGHT_M,
                default=defaults.get(CONF_CRITICAL_HEIGHT_M, ""),
            ): vol.Any("", vol.Coerce(float)),
            vol.Optional(
                CONF_WARNING_RISE_CM_H,
                default=defaults.get(
                    CONF_WARNING_RISE_CM_H,
                    DEFAULT_WARNING_RISE_CM_H,
                ),
            ): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Optional(
                CONF_CRITICAL_RISE_CM_H,
                default=defaults.get(
                    CONF_CRITICAL_RISE_CM_H,
                    DEFAULT_CRITICAL_RISE_CM_H,
                ),
            ): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Optional(
                CONF_FORECAST_HOURS,
                default=defaults.get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
            vol.Optional(
                CONF_ALERT_LEVEL,
                default=defaults.get(CONF_ALERT_LEVEL, DEFAULT_ALERT_LEVEL),
            ): vol.In([RISK_WARNING, RISK_CRITICAL]),
        }
    )
    return vol.Schema(fields)


def _clean_input(user_input: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(user_input)
    for key in (CONF_STATION_CODE, CONF_NAME):
        if key in cleaned:
            cleaned[key] = str(cleaned[key]).strip()
            if not cleaned[key]:
                cleaned.pop(key)
    for key in (CONF_WARNING_HEIGHT_M, CONF_CRITICAL_HEIGHT_M):
        if key in cleaned and cleaned[key] == "":
            cleaned.pop(key)
    return cleaned


def _unique_id(user_input: dict[str, Any]) -> str:
    if user_input.get(CONF_STATION_CODE):
        return f"station:{user_input[CONF_STATION_CODE]}"
    latitude = round(float(user_input[CONF_LATITUDE]), 4)
    longitude = round(float(user_input[CONF_LONGITUDE]), 4)
    radius = round(float(user_input[CONF_RADIUS_KM]), 1)
    return f"location:{latitude}:{longitude}:{radius}"
