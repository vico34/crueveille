"""Client for Hub'Eau Hydrometrie API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import asin, cos, radians, sin, sqrt
from typing import Any

from aiohttp import ClientError, ClientSession
from yarl import URL

from .const import HUBEAU_BASE_URL


class VigicruesApiError(Exception):
    """Raised when the Hub'Eau API request fails."""


@dataclass(frozen=True)
class Station:
    """Hydrometric station metadata."""

    code: str
    label: str
    latitude: float
    longitude: float
    distance_km: float | None = None


@dataclass(frozen=True)
class Observation:
    """Hydrometric observation."""

    value: float
    observed_at: datetime


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometers."""
    earth_radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class VigicruesApiClient:
    """Small async client for the Hydrometrie API."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = URL(f"{HUBEAU_BASE_URL}/{path}")
        try:
            async with self._session.get(url, params=params, timeout=20) as response:
                if response.status >= 400:
                    text = await response.text()
                    raise VigicruesApiError(
                        f"Hub'Eau returned HTTP {response.status}: {text[:200]}"
                    )
                return await response.json()
        except ClientError as err:
            raise VigicruesApiError(f"Hub'Eau request failed: {err}") from err

    async def get_station(self, station_code: str) -> Station:
        """Return metadata for one station."""
        payload = await self._get_json(
            "referentiel/stations",
            {
                "code_station": station_code,
                "format": "json",
                "size": 1,
                "fields": ",".join(
                    [
                        "code_station",
                        "libelle_station",
                        "latitude_station",
                        "longitude_station",
                    ]
                ),
            },
        )
        rows = payload.get("data") or []
        if not rows:
            raise VigicruesApiError(f"Station {station_code} introuvable")
        return _station_from_row(rows[0])

    async def find_nearest_station(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> Station:
        """Find the nearest station around a location."""
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / max(1.0, 111.0 * cos(radians(latitude)))
        payload = await self._get_json(
            "referentiel/stations",
            {
                "bbox": ",".join(
                    str(value)
                    for value in (
                        longitude - lon_delta,
                        latitude - lat_delta,
                        longitude + lon_delta,
                        latitude + lat_delta,
                    )
                ),
                "format": "json",
                "size": 200,
                "fields": ",".join(
                    [
                        "code_station",
                        "libelle_station",
                        "latitude_station",
                        "longitude_station",
                    ]
                ),
            },
        )
        stations = [
            _station_from_row(row, latitude, longitude)
            for row in payload.get("data", [])
            if row.get("latitude_station") is not None
            and row.get("longitude_station") is not None
        ]
        stations = [
            station
            for station in stations
            if station.distance_km is not None and station.distance_km <= radius_km
        ]
        if not stations:
            raise VigicruesApiError("Aucune station hydrometrique trouvee dans le rayon")
        return min(stations, key=lambda station: station.distance_km or 999999)

    async def observations(
        self,
        station_code: str,
        grandeur: str,
        history_hours: int = 6,
        size: int = 80,
    ) -> list[Observation]:
        """Return recent observations for a station and hydrometric value."""
        start = datetime.now(UTC) - timedelta(hours=history_hours)
        payload = await self._get_json(
            "observations_tr",
            {
                "code_entite": station_code,
                "grandeur_hydro": grandeur,
                "date_debut_obs": start.isoformat().replace("+00:00", "Z"),
                "sort": "desc",
                "format": "json",
                "size": size,
                "fields": "date_obs,resultat_obs",
            },
        )
        observations: list[Observation] = []
        for row in payload.get("data", []):
            if row.get("resultat_obs") is None or row.get("date_obs") is None:
                continue
            observations.append(
                Observation(
                    value=float(row["resultat_obs"]),
                    observed_at=_parse_datetime(row["date_obs"]),
                )
            )
        return observations


def _station_from_row(
    row: dict[str, Any],
    latitude: float | None = None,
    longitude: float | None = None,
) -> Station:
    station_latitude = float(row["latitude_station"])
    station_longitude = float(row["longitude_station"])
    station_distance = None
    if latitude is not None and longitude is not None:
        station_distance = distance_km(
            latitude,
            longitude,
            station_latitude,
            station_longitude,
        )
    return Station(
        code=row["code_station"],
        label=row.get("libelle_station") or row["code_station"],
        latitude=station_latitude,
        longitude=station_longitude,
        distance_km=station_distance,
    )
