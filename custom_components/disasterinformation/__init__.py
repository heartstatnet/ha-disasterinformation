"""気象庁防災情報 integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up 気象庁防災情報 from a config entry."""
    
    # Create data update coordinator
    coordinator = DisasterInformationCoordinator(hass, entry)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class DisasterInformationCoordinator(DataUpdateCoordinator):
    """Data coordinator for disaster information."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        update_interval = timedelta(
            minutes=entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
    
    async def _async_update_data(self) -> dict:
        """Fetch data from JMA API."""
        from .api import JMABosaiApiClient
        from .const import INFO_TYPE_EARTHQUAKE, INFO_TYPE_WEATHER_WARNING
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                api_client = JMABosaiApiClient(session)
                
                information_type = self.entry.data.get("information_type", INFO_TYPE_WEATHER_WARNING)
                
                if information_type == INFO_TYPE_EARTHQUAKE:
                    # Get earthquake data with filters
                    time_range = int(self.entry.data.get("earthquake_time_range", "24"))
                    min_magnitude = float(self.entry.data.get("earthquake_min_magnitude", "0"))
                    min_intensity = self.entry.data.get("earthquake_min_intensity", "0")
                    
                    data = await api_client.get_earthquake_data(
                        time_range_hours=time_range,
                        min_magnitude=min_magnitude,
                        min_intensity=min_intensity
                    )
                    
                    if data:
                        data["information_type"] = INFO_TYPE_EARTHQUAKE
                        return data
                    else:
                        return {
                            "information_type": INFO_TYPE_EARTHQUAKE,
                            "earthquakes": [],
                            "count": 0,
                            "status": "error"
                        }
                        
                else:
                    # Get weather warning data
                    warning_area_code = self.entry.data.get("warning_area_code")
                    if not warning_area_code:
                        return {
                            "information_type": INFO_TYPE_WEATHER_WARNING,
                            "status": "error",
                            "warnings": []
                        }
                    
                    city_area_code = self.entry.data.get("area_code")
                    data = await api_client.get_warning_data(warning_area_code, city_area_code)
                    
                    if data:
                        data["information_type"] = INFO_TYPE_WEATHER_WARNING
                        data["prefecture"] = self.entry.data.get("prefecture")
                        data["city"] = self.entry.data.get("city")
                        return data
                    else:
                        return {
                            "information_type": INFO_TYPE_WEATHER_WARNING,
                            "prefecture": self.entry.data.get("prefecture"),
                            "city": self.entry.data.get("city"),
                            "warnings": [],
                            "status": "error"
                        }
            
        except Exception as e:
            _LOGGER.error(f"Error updating disaster information: {e}")
            information_type = self.entry.data.get("information_type", INFO_TYPE_WEATHER_WARNING)
            
            if information_type == INFO_TYPE_EARTHQUAKE:
                return {
                    "information_type": INFO_TYPE_EARTHQUAKE,
                    "earthquakes": [],
                    "count": 0,
                    "status": "error"
                }
            else:
                return {
                    "information_type": INFO_TYPE_WEATHER_WARNING,
                    "prefecture": self.entry.data.get("prefecture"),
                    "city": self.entry.data.get("city"),
                    "warnings": [],
                    "status": "error"
                }