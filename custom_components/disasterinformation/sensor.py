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
        self._attr_name = f"{config_entry.data['prefecture']} {config_entry.data['city']} {ENTITY_NAME_WARNING}"
        self._attr_unique_id = f"{config_entry.entry_id}_warnings"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data or self.coordinator.data.get("status") == "error":
            return "不明"
        
        warnings = self.coordinator.data.get("warnings", [])
        if not warnings:
            return "発表なし"
        
        # Find the highest severity warning
        special_warnings = [w for w in warnings if w.get("severity") == "特別警報"]
        regular_warnings = [w for w in warnings if w.get("severity") == "警報"]
        advisories = [w for w in warnings if w.get("severity") == "注意報"]
        
        if special_warnings:
            types = []
            for warning in special_warnings:
                types.extend(warning.get("types", []))
            return f"特別警報({' '.join(types)})"
        elif regular_warnings:
            types = []
            for warning in regular_warnings:
                types.extend(warning.get("types", []))
            return f"警報({' '.join(types)})"
        elif advisories:
            types = []
            for warning in advisories:
                types.extend(warning.get("types", []))
            return f"注意報({' '.join(types)})"
        
        return "発表なし"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        warnings = self.coordinator.data.get("warnings", [])
        
        # Separate warnings by severity
        special_warnings = [w for w in warnings if w.get("severity") == "特別警報"]
        regular_warnings = [w for w in warnings if w.get("severity") == "警報"]
        advisories = [w for w in warnings if w.get("severity") == "注意報"]
        
        # Extract warning types for each severity
        special_warning_types = []
        warning_types = []
        advisory_types = []
        
        for warning in special_warnings:
            special_warning_types.extend(warning.get("types", []))
        
        for warning in regular_warnings:
            warning_types.extend(warning.get("types", []))
        
        for warning in advisories:
            advisory_types.extend(warning.get("types", []))
        
        return {
            "prefecture": self.coordinator.data.get("prefecture"),
            "city": self.coordinator.data.get("city"),
            "special_warnings": special_warning_types,
            "warnings": warning_types,
            "advisories": advisory_types,
            "warning_count": len(warnings),
            "has_special_warning": len(special_warnings) > 0,
            "has_warning": len(regular_warnings) > 0,
            "has_advisory": len(advisories) > 0,
            "last_update": self.coordinator.data.get("last_update"),
            "status": self.coordinator.data.get("status", "unknown"),
            "raw_warnings": warnings,  # 詳細なデバッグ情報
        }

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:weather-lightning"


class DisasterEarthquakeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for earthquake information."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{ENTITY_NAME_EARTHQUAKE}"
        self._attr_unique_id = f"{config_entry.entry_id}_earthquake"

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
            "min_intensity": data.get("min_intensity", "0"),
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
                    "depth": latest.get("depth", ""),
                    "magnitude": latest.get("magnitude", ""),
                    "max_intensity": latest.get("max_intensity", ""),
                    "max_intensity_code": latest.get("max_intensity_code", ""),
                }
            })
        
        # Add all earthquakes list (limited to essential info)
        earthquake_list = []
        for eq in earthquakes[:20]:  # Limit to 20 most recent
            earthquake_list.append({
                "origin_time": eq.get("origin_time", ""),
                "hypocenter": eq.get("hypocenter", ""),
                "depth": eq.get("depth", ""),
                "magnitude": eq.get("magnitude", ""),
                "max_intensity": eq.get("max_intensity", ""),
            })
        
        attributes["recent_earthquakes"] = earthquake_list
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:earth"