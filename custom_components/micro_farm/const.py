"""Constants for the Micro Farm integration."""

from __future__ import annotations

DOMAIN = "micro_farm"

CONF_NAME = "name"
CONF_DAILY_FEED_KG = "daily_feed_kg"
CONF_DAILY_WATER_L = "daily_water_l"
CONF_LOW_FEED_DAYS = "low_feed_days"
CONF_LOW_WATER_DAYS = "low_water_days"
CONF_LOW_BATTERY_PERCENT = "low_battery_percent"
CONF_DRY_SOIL_PERCENT = "dry_soil_percent"

DEFAULT_NAME = "Micro ferme"
DEFAULT_DAILY_FEED_KG = 0.8
DEFAULT_DAILY_WATER_L = 8.0
DEFAULT_LOW_FEED_DAYS = 3.0
DEFAULT_LOW_WATER_DAYS = 2.0
DEFAULT_LOW_BATTERY_PERCENT = 25.0
DEFAULT_DRY_SOIL_PERCENT = 30.0

SIGNAL_UPDATE = f"{DOMAIN}_update"
