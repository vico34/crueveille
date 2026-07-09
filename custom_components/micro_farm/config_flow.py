"""Config flow for Micro Farm."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_DAILY_FEED_KG,
    CONF_DAILY_WATER_L,
    CONF_DRY_SOIL_PERCENT,
    CONF_LOW_BATTERY_PERCENT,
    CONF_LOW_FEED_DAYS,
    CONF_LOW_WATER_DAYS,
    CONF_NAME,
    DEFAULT_DAILY_FEED_KG,
    DEFAULT_DAILY_WATER_L,
    DEFAULT_DRY_SOIL_PERCENT,
    DEFAULT_LOW_BATTERY_PERCENT,
    DEFAULT_LOW_FEED_DAYS,
    DEFAULT_LOW_WATER_DAYS,
    DEFAULT_NAME,
    DOMAIN,
)


class MicroFarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Micro Farm."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                data = _clean_input(user_input)
            except ValueError:
                errors["base"] = "invalid_number"
            else:
                await self.async_set_unique_id("micro_farm")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=data[CONF_NAME], data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return MicroFarmOptionsFlow(config_entry)


class MicroFarmOptionsFlow(config_entries.OptionsFlow):
    """Handle Micro Farm options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Manage options."""
        if user_input is not None:
            try:
                return self.async_create_entry(title="", data=_clean_input(user_input))
            except ValueError:
                return self.async_show_form(
                    step_id="init",
                    data_schema=_schema({**self._config_entry.data, **user_input}),
                    errors={"base": "invalid_number"},
                )

        defaults = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    """Return the config schema."""
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Optional(
                CONF_DAILY_FEED_KG,
                default=str(defaults.get(CONF_DAILY_FEED_KG, DEFAULT_DAILY_FEED_KG)),
            ): str,
            vol.Optional(
                CONF_DAILY_WATER_L,
                default=str(defaults.get(CONF_DAILY_WATER_L, DEFAULT_DAILY_WATER_L)),
            ): str,
            vol.Optional(
                CONF_LOW_FEED_DAYS,
                default=str(defaults.get(CONF_LOW_FEED_DAYS, DEFAULT_LOW_FEED_DAYS)),
            ): str,
            vol.Optional(
                CONF_LOW_WATER_DAYS,
                default=str(defaults.get(CONF_LOW_WATER_DAYS, DEFAULT_LOW_WATER_DAYS)),
            ): str,
            vol.Optional(
                CONF_LOW_BATTERY_PERCENT,
                default=str(
                    defaults.get(
                        CONF_LOW_BATTERY_PERCENT,
                        DEFAULT_LOW_BATTERY_PERCENT,
                    )
                ),
            ): str,
            vol.Optional(
                CONF_DRY_SOIL_PERCENT,
                default=str(defaults.get(CONF_DRY_SOIL_PERCENT, DEFAULT_DRY_SOIL_PERCENT)),
            ): str,
        }
    )


def _clean_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize user input."""
    cleaned = dict(user_input)
    cleaned[CONF_NAME] = str(cleaned.get(CONF_NAME) or DEFAULT_NAME).strip() or DEFAULT_NAME
    for key in (
        CONF_DAILY_FEED_KG,
        CONF_DAILY_WATER_L,
        CONF_LOW_FEED_DAYS,
        CONF_LOW_WATER_DAYS,
        CONF_LOW_BATTERY_PERCENT,
        CONF_DRY_SOIL_PERCENT,
    ):
        cleaned[key] = _positive_float(cleaned[key])
    return cleaned


def _positive_float(value: Any) -> float:
    """Return a positive float."""
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise ValueError("invalid_number") from err
    if number < 0:
        raise ValueError("invalid_number")
    return number
