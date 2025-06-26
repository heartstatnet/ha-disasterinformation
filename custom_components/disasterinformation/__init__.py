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
        from .api import JMAApiClient
        
        try:
            api_client = JMAApiClient(self.hass)
            
            prefecture = self.entry.data.get("prefecture")
            city = self.entry.data.get("city")
            
            data = await api_client.async_get_disaster_info(prefecture, city)
            await api_client.async_close()
            
            return data
            
        except Exception as e:
            _LOGGER.error(f"Error updating disaster information: {e}")
            return {
                "prefecture": self.entry.data.get("prefecture"),
                "city": self.entry.data.get("city"),
                "warnings": [],
                "last_update": None,
                "status": "error"
            }