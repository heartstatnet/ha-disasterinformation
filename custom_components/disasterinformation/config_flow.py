"""Config flow for 気象庁防災情報 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    PREFECTURES,
    CONF_PREFECTURE,
    CONF_CITY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class DisasterInformationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 気象庁防災情報."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._prefecture: str | None = None
        self._city: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._prefecture = user_input[CONF_PREFECTURE]
            return await self.async_step_city()

        data_schema = vol.Schema({
            vol.Required(CONF_PREFECTURE): vol.In(list(PREFECTURES.keys()))
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_city(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the city selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._city = user_input[CONF_CITY]
            return await self.async_step_final()

        # For now, use a simplified city list
        # TODO: Implement actual city/region mapping based on prefecture
        cities = self._get_cities_for_prefecture(self._prefecture)
        
        data_schema = vol.Schema({
            vol.Required(CONF_CITY): vol.In(cities)
        })

        return self.async_show_form(
            step_id="city",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_final(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the final configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            
            # Create config entry
            return self.async_create_entry(
                title=f"{self._prefecture} {self._city}",
                data={
                    CONF_PREFECTURE: self._prefecture,
                    CONF_CITY: self._city,
                    CONF_UPDATE_INTERVAL: update_interval,
                },
            )

        data_schema = vol.Schema({
            vol.Optional(
                CONF_UPDATE_INTERVAL, 
                default=DEFAULT_UPDATE_INTERVAL
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL))
        })

        return self.async_show_form(
            step_id="final",
            data_schema=data_schema,
            errors=errors,
        )

    def _get_cities_for_prefecture(self, prefecture: str) -> list[str]:
        """Get cities for the selected prefecture."""
        # Simplified city mapping - in real implementation, this would be more comprehensive
        city_mapping = {
            "福岡県": ["北九州市", "福岡市", "筑豊地方", "筑後地方"],
            "東京都": ["23区", "多摩地方", "島しょ部"],
            "大阪府": ["大阪市", "北部", "東部", "南部"],
        }
        
        return city_mapping.get(prefecture, [f"{prefecture}全域"])