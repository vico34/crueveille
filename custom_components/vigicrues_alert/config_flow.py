"""Config flow for Vigicrues Alert."""

from __future__ import annotations

from typing import Any, Dict, Optional

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
    RISK_ORDER,
    RISK_CRITICAL,
    RISK_WARNING,
)


class VigicruesAlertConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vigicrues Alert."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: Optional[Dict[str, Any]] = None,
    ):
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                user_input = _clean_input(user_input)
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

    def _schema(self, user_input: Optional[Dict[str, Any]] = None) -> vol.Schema:
        defaults = user_input or {}
        return _schema(
            defaults,
            default_latitude=self.hass.config.latitude,
            default_longitude=self.hass.config.longitude,
        )

    async def _validate_and_title(self, user_input: Dict[str, Any]) -> str:
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
        user_input: Optional[Dict[str, Any]] = None,
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
    defaults: Dict[str, Any],
    *,
    default_latitude: float,
    default_longitude: float,
    include_name: bool = True,
) -> vol.Schema:
    number_input = vol.Any(str, int, float)
    fields: Dict[Any, Any] = {}
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
                default=str(latitude),
            ): number_input,
            vol.Optional(
                CONF_LONGITUDE,
                default=str(longitude),
            ): number_input,
            vol.Optional(
                CONF_RADIUS_KM,
                default=str(defaults.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)),
            ): number_input,
            vol.Optional(
                CONF_WARNING_HEIGHT_M,
                default=defaults.get(CONF_WARNING_HEIGHT_M, ""),
            ): number_input,
            vol.Optional(
                CONF_CRITICAL_HEIGHT_M,
                default=defaults.get(CONF_CRITICAL_HEIGHT_M, ""),
            ): number_input,
            vol.Optional(
                CONF_WARNING_RISE_CM_H,
                default=str(
                    defaults.get(CONF_WARNING_RISE_CM_H, DEFAULT_WARNING_RISE_CM_H)
                ),
            ): number_input,
            vol.Optional(
                CONF_CRITICAL_RISE_CM_H,
                default=str(
                    defaults.get(CONF_CRITICAL_RISE_CM_H, DEFAULT_CRITICAL_RISE_CM_H)
                ),
            ): number_input,
            vol.Optional(
                CONF_FORECAST_HOURS,
                default=str(defaults.get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS)),
            ): number_input,
            vol.Optional(
                CONF_ALERT_LEVEL,
                default=defaults.get(CONF_ALERT_LEVEL, DEFAULT_ALERT_LEVEL),
            ): vol.In([RISK_WARNING, RISK_CRITICAL]),
        }
    )
    return vol.Schema(fields)


def _clean_input(user_input: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = dict(user_input)
    for key in (CONF_STATION_CODE, CONF_NAME):
        if key in cleaned:
            cleaned[key] = str(cleaned[key]).strip()
            if not cleaned[key]:
                cleaned.pop(key)
    for key in (CONF_WARNING_HEIGHT_M, CONF_CRITICAL_HEIGHT_M):
        if key in cleaned and cleaned[key] == "":
            cleaned.pop(key)
        elif key in cleaned:
            cleaned[key] = _float_value(cleaned[key], key, minimum=0)

    cleaned[CONF_LATITUDE] = _float_value(cleaned[CONF_LATITUDE], CONF_LATITUDE)
    cleaned[CONF_LONGITUDE] = _float_value(cleaned[CONF_LONGITUDE], CONF_LONGITUDE)
    cleaned[CONF_RADIUS_KM] = _float_value(
        cleaned.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM),
        CONF_RADIUS_KM,
        minimum=1,
        maximum=100,
    )
    cleaned[CONF_WARNING_RISE_CM_H] = _float_value(
        cleaned.get(CONF_WARNING_RISE_CM_H, DEFAULT_WARNING_RISE_CM_H),
        CONF_WARNING_RISE_CM_H,
        minimum=0,
    )
    cleaned[CONF_CRITICAL_RISE_CM_H] = _float_value(
        cleaned.get(CONF_CRITICAL_RISE_CM_H, DEFAULT_CRITICAL_RISE_CM_H),
        CONF_CRITICAL_RISE_CM_H,
        minimum=0,
    )
    cleaned[CONF_FORECAST_HOURS] = _int_value(
        cleaned.get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS),
        CONF_FORECAST_HOURS,
        minimum=1,
        maximum=24,
    )
    if cleaned.get(CONF_ALERT_LEVEL) not in RISK_ORDER:
        cleaned[CONF_ALERT_LEVEL] = DEFAULT_ALERT_LEVEL
    return cleaned


def _float_value(
    value: Any,
    key: str,
    *,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
) -> float:
    try:
        normalized = value.replace(",", ".") if isinstance(value, str) else value
        number = float(normalized)
    except (TypeError, ValueError) as err:
        raise ValueError("invalid_number") from err
    if minimum is not None and number < minimum:
        raise ValueError("invalid_number")
    if maximum is not None and number > maximum:
        raise ValueError("invalid_number")
    return number


def _int_value(
    value: Any,
    key: str,
    *,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as err:
        raise ValueError("invalid_number") from err
    if minimum is not None and number < minimum:
        raise ValueError("invalid_number")
    if maximum is not None and number > maximum:
        raise ValueError("invalid_number")
    return number


def _unique_id(user_input: Dict[str, Any]) -> str:
    if user_input.get(CONF_STATION_CODE):
        return f"station:{user_input[CONF_STATION_CODE]}"
    latitude = round(float(user_input[CONF_LATITUDE]), 4)
    longitude = round(float(user_input[CONF_LONGITUDE]), 4)
    radius = round(float(user_input[CONF_RADIUS_KM]), 1)
    return f"location:{latitude}:{longitude}:{radius}"
