"""Constants for the Vigicrues Alert integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "vigicrues_alert"

CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS_KM = "radius_km"
CONF_STATION_CODE = "station_code"
CONF_WARNING_HEIGHT_M = "warning_height_m"
CONF_CRITICAL_HEIGHT_M = "critical_height_m"
CONF_WARNING_RISE_CM_H = "warning_rise_cm_h"
CONF_CRITICAL_RISE_CM_H = "critical_rise_cm_h"
CONF_FORECAST_HOURS = "forecast_hours"
CONF_ALERT_LEVEL = "alert_level"

DEFAULT_RADIUS_KM = 20.0
DEFAULT_WARNING_RISE_CM_H = 10.0
DEFAULT_CRITICAL_RISE_CM_H = 25.0
DEFAULT_FORECAST_HOURS = 3
DEFAULT_ALERT_LEVEL = "warning"

SCAN_INTERVAL = timedelta(minutes=15)

HUBEAU_BASE_URL = "https://hubeau.eaufrance.fr/api/v2/hydrometrie"

ATTRIBUTION = "Donnees Hub'Eau Hydrometrie, operees par le Service Central Vigicrues"

RISK_CLEAR = "clear"
RISK_WATCH = "watch"
RISK_WARNING = "warning"
RISK_CRITICAL = "critical"

RISK_ORDER = {
    RISK_CLEAR: 0,
    RISK_WATCH: 1,
    RISK_WARNING: 2,
    RISK_CRITICAL: 3,
}
