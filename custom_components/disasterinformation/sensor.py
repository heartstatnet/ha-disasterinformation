"""Sensor platform for 気象庁防災情報."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_NAME_WARNING, ENTITY_NAME_EARTHQUAKE, INFO_TYPE_EARTHQUAKE, INFO_TYPE_WEATHER_WARNING
from .area_mapping import get_entity_prefix, get_english_name

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Determine which sensors to create based on information type
    information_type = config_entry.data.get("information_type", INFO_TYPE_WEATHER_WARNING)
    
    entities = []
    
    if information_type == INFO_TYPE_EARTHQUAKE:
        # Create earthquake sensor
        entities.append(DisasterEarthquakeSensor(coordinator, config_entry))
    else:
        # Create warning sensor
        entities.append(DisasterWarningsSensor(coordinator, config_entry))
    
    async_add_entities(entities)


class DisasterWarningsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for disaster warnings."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        prefecture_en, city_en = get_english_name(config_entry.data['prefecture'], config_entry.data['city'])
        self._attr_name = f"{prefecture_en} {city_en} Weather Alert"
        self._attr_unique_id = f"{prefecture_en.lower()}_{city_en.lower()}_weather_alert"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data or self.coordinator.data.get("status") == "error":
            return "不明"
        
        # Get all types of warnings from coordinator data
        all_warnings = self.coordinator.data.get("warnings", [])
        all_advisories = self.coordinator.data.get("advisories", [])
        all_emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        
        # Check if any warnings/advisories exist
        total_alerts = len(all_warnings) + len(all_advisories) + len(all_emergency_warnings)
        if total_alerts == 0:
            return "発表なし"
        
        # Separate by severity (they're already separated in the API response)
        special_warnings = all_emergency_warnings
        regular_warnings = all_warnings  
        advisories = all_advisories
        
        if special_warnings:
            types = [warning.get("name", "不明") for warning in special_warnings]
            return f"特別警報({' '.join(types)})"
        elif regular_warnings:
            types = [warning.get("name", "不明") for warning in regular_warnings]
            return f"警報({' '.join(types)})"
        elif advisories:
            types = [warning.get("name", "不明") for warning in advisories]
            return f"注意報({' '.join(types)})"
        
        return "発表なし"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        # Get separated warning data from coordinator
        all_warnings = self.coordinator.data.get("warnings", [])
        all_advisories = self.coordinator.data.get("advisories", [])
        all_emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        
        # Extract warning names for each severity
        special_warning_types = [w.get("name", "不明") for w in all_emergency_warnings]
        warning_types = [w.get("name", "不明") for w in all_warnings]
        advisory_types = [w.get("name", "不明") for w in all_advisories]
        
        # Calculate total count
        total_count = len(all_warnings) + len(all_advisories) + len(all_emergency_warnings)
        
        return {
            "prefecture": self.coordinator.data.get("prefecture"),
            "city": self.coordinator.data.get("city"),
            "special_warnings": special_warning_types,
            "warnings": warning_types,
            "advisories": advisory_types,
            "warning_count": total_count,
            "has_special_warning": len(all_emergency_warnings) > 0,
            "has_warning": len(all_warnings) > 0,
            "has_advisory": len(all_advisories) > 0,
            "last_update": self.coordinator.data.get("last_update"),
            "status": self.coordinator.data.get("status", "unknown"),
            "raw_warnings": all_warnings + all_advisories + all_emergency_warnings,  # 詳細なデバッグ情報
        }

    @property
    def icon(self) -> str:
        """Return the icon for the sensor based on highest severity level."""
        if not self.coordinator.data:
            return "mdi:weather-sunny"
        
        # Check highest severity level and return appropriate icon
        emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        warnings = self.coordinator.data.get("warnings", [])
        advisories = self.coordinator.data.get("advisories", [])
        
        if emergency_warnings:
            return "mdi:weather-tornado"  # 特別警報 - 最高レベル
        elif warnings:
            return "mdi:weather-lightning-rainy"  # 警報 - 重要レベル
        elif advisories:
            return "mdi:weather-cloudy-alert"  # 注意報 - 注意レベル
        else:
            return "mdi:weather-sunny"  # 発表なし - 平常時


class DisasterEarthquakeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for earthquake information."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = ENTITY_NAME_EARTHQUAKE
        self._attr_unique_id = "earthquake_information"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data or self.coordinator.data.get("status") == "error":
            return "不明"
        
        count = self.coordinator.data.get("count", 0)
        if count == 0:
            return "該当する地震なし"
        elif count == 1:
            return "1件の地震"
        else:
            return f"{count}件の地震"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        earthquakes = data.get("earthquakes", [])
        latest = data.get("latest_earthquake")
        
        attributes = {
            "earthquake_count": data.get("count", 0),
            "time_range_hours": data.get("time_range_hours", 24),
            "min_magnitude": data.get("min_magnitude", 0.0),
            "status": data.get("status", "unknown"),
        }
        
        # Add latest earthquake details
        if latest:
            attributes.update({
                "latest_earthquake": {
                    "event_id": latest.get("event_id", ""),
                    "origin_time": latest.get("origin_time", ""),
                    "report_datetime": latest.get("report_datetime", ""),
                    "hypocenter": latest.get("hypocenter", ""),
                    "magnitude": latest.get("magnitude", ""),
                }
            })
        
        # Add recent earthquakes list (10 most recent with report_datetime, hypocenter, magnitude only)
        # Filter out earthquakes without hypocenter data
        recent_earthquakes = data.get("recent_earthquakes", [])
        formatted_recent = []
        for eq in recent_earthquakes:
            hypocenter = eq.get("hypocenter", "")
            magnitude = eq.get("magnitude")
            
            # Skip earthquakes without hypocenter or magnitude data
            if not hypocenter or not magnitude:
                continue
                
            formatted_recent.append({
                "report_datetime": eq.get("report_datetime", ""),
                "hypocenter": hypocenter,
                "magnitude": magnitude,
            })
        
        attributes["recent_earthquakes"] = formatted_recent
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:earth"