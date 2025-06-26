"""Sensor platform for 気象庁防災情報."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_NAME_WARNING

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Create warning sensor
    entities = [
        DisasterWarningsSensor(coordinator, config_entry),
    ]
    
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