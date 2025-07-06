"""Binary sensor platform for 気象庁防災情報."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INFO_TYPE_EARTHQUAKE, INFO_TYPE_WEATHER_WARNING

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Determine which binary sensors to create based on information type
    information_type = config_entry.data.get("information_type", INFO_TYPE_WEATHER_WARNING)
    
    entities = []
    
    if information_type == INFO_TYPE_EARTHQUAKE:
        # Create earthquake binary sensor
        entities.append(DisasterEarthquakeBinarySensor(coordinator, config_entry))
    else:
        # Create warning binary sensors
        entities.extend([
            DisasterSpecialWarningBinarySensor(coordinator, config_entry),
            DisasterWarningBinarySensor(coordinator, config_entry),
            DisasterAdvisoryBinarySensor(coordinator, config_entry),
        ])
    
    async_add_entities(entities)


class DisasterSpecialWarningBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for special warnings (特別警報)."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data['prefecture']} {config_entry.data['city']} 特別警報"
        self._attr_unique_id = f"{config_entry.entry_id}_special_warning"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self) -> bool:
        """Return true if special warning is active."""
        if not self.coordinator.data:
            return False
        
        emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        return len(emergency_warnings) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        
        types = [w.get("name", "不明") for w in emergency_warnings]
        
        return {
            "warning_types": types,
            "warning_count": len(emergency_warnings),
        }

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor."""
        return "mdi:alert" if self.is_on else "mdi:shield-check"


class DisasterWarningBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for warnings (警報)."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data['prefecture']} {config_entry.data['city']} 警報"
        self._attr_unique_id = f"{config_entry.entry_id}_warning"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self) -> bool:
        """Return true if warning is active."""
        if not self.coordinator.data:
            return False
        
        warnings = self.coordinator.data.get("warnings", [])
        emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        return len(warnings) > 0 or len(emergency_warnings) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        warnings = self.coordinator.data.get("warnings", [])
        emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        
        types = []
        types.extend([w.get("name", "不明") for w in warnings])
        types.extend([w.get("name", "不明") for w in emergency_warnings])
        
        return {
            "warning_types": types,
            "warning_count": len(warnings) + len(emergency_warnings),
        }

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor."""
        return "mdi:weather-lightning" if self.is_on else "mdi:weather-sunny"


class DisasterAdvisoryBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for advisories (注意報)."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data['prefecture']} {config_entry.data['city']} 注意報"
        self._attr_unique_id = f"{config_entry.entry_id}_advisory"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self) -> bool:
        """Return true if advisory is active."""
        if not self.coordinator.data:
            return False
        
        advisories = self.coordinator.data.get("advisories", [])
        return len(advisories) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        advisories = self.coordinator.data.get("advisories", [])
        
        types = [w.get("name", "不明") for w in advisories]
        
        return {
            "warning_types": types,
            "warning_count": len(advisories),
        }

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor."""
        return "mdi:information" if self.is_on else "mdi:check-circle"


class DisasterEarthquakeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for earthquake detection."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"地震検知"
        self._attr_unique_id = f"{config_entry.entry_id}_earthquake_detected"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY
        self._last_earthquake_time = None

    @property
    def is_on(self) -> bool:
        """Return true if earthquake is detected."""
        if not self.coordinator.data:
            return False
        
        latest_earthquake = self.coordinator.data.get("latest_earthquake")
        if not latest_earthquake:
            return False
        
        # Check if there's a new earthquake (within last 30 minutes)
        origin_time = latest_earthquake.get("origin_time")
        if origin_time:
            try:
                from datetime import datetime, timedelta
                earthquake_time = datetime.fromisoformat(origin_time.replace('Z', '+00:00'))
                now = datetime.now()
                
                # Consider earthquake "active" for 30 minutes after occurrence
                time_diff = now - earthquake_time.replace(tzinfo=None)
                return time_diff <= timedelta(minutes=30)
                
            except Exception as e:
                _LOGGER.warning(f"Error parsing earthquake time: {e}")
                return False
        
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        latest_earthquake = self.coordinator.data.get("latest_earthquake")
        count = self.coordinator.data.get("count", 0)
        
        attributes = {
            "earthquake_count": count,
            "time_range_hours": self.coordinator.data.get("time_range_hours", 24),
        }
        
        if latest_earthquake:
            attributes.update({
                "latest_earthquake_time": latest_earthquake.get("origin_time", ""),
                "latest_hypocenter": latest_earthquake.get("hypocenter", ""),
                "latest_magnitude": latest_earthquake.get("magnitude", ""),
                "latest_max_intensity": latest_earthquake.get("max_intensity", ""),
                "latest_depth": latest_earthquake.get("depth", ""),
            })
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor."""
        return "mdi:earth" if self.is_on else "mdi:earth-off"