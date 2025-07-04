"""Config flow for 気象庁防災情報 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import aiohttp

from .const import (
    DOMAIN,
    REGION_CODES,
    PREFECTURE_CODES,
    INFORMATION_TYPES,
    EARTHQUAKE_TIME_RANGES,
    EARTHQUAKE_MIN_MAGNITUDES,
    EARTHQUAKE_MIN_INTENSITIES,
    CONF_INFORMATION_TYPE,
    CONF_REGION,
    CONF_PREFECTURE,
    CONF_CITY,
    CONF_AREA_CODE,
    CONF_UPDATE_INTERVAL,
    CONF_EARTHQUAKE_MIN_MAGNITUDE,
    CONF_EARTHQUAKE_MIN_INTENSITY,
    CONF_EARTHQUAKE_TIME_RANGE,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    INFO_TYPE_WEATHER_WARNING,
    INFO_TYPE_EARTHQUAKE,
)
from .area_manager import AreaManager

_LOGGER = logging.getLogger(__name__)


class DisasterInformationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 気象庁防災情報."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._information_type: str | None = None
        self._region: str | None = None
        self._region_code: str | None = None
        self._prefecture: str | None = None
        self._prefecture_code: str | None = None
        self._city: str | None = None
        self._area_code: str | None = None
        self._area_manager: AreaManager | None = None
        self._earthquake_time_range: str = "24"
        self._earthquake_min_magnitude: str = "0"
        self._earthquake_min_intensity: str = "0"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - information type selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._information_type = user_input[CONF_INFORMATION_TYPE]
            
            if self._information_type == INFO_TYPE_EARTHQUAKE:
                # Go to earthquake configuration
                return await self.async_step_earthquake_config()
            else:
                # Proceed to region selection for weather warnings
                return await self.async_step_region()

        data_schema = vol.Schema({
            vol.Required(CONF_INFORMATION_TYPE): vol.In(INFORMATION_TYPES)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_region(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the region selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._region = user_input[CONF_REGION]
            self._region_code = REGION_CODES.get(self._region)
            return await self.async_step_prefecture()

        data_schema = vol.Schema({
            vol.Required(CONF_REGION): vol.In(list(REGION_CODES.keys()))
        })

        return self.async_show_form(
            step_id="region",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_earthquake_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle earthquake configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._earthquake_time_range = user_input.get(CONF_EARTHQUAKE_TIME_RANGE, "24")
            self._earthquake_min_magnitude = user_input.get(CONF_EARTHQUAKE_MIN_MAGNITUDE, "0")
            self._earthquake_min_intensity = user_input.get(CONF_EARTHQUAKE_MIN_INTENSITY, "0")
            return await self.async_step_final()

        data_schema = vol.Schema({
            vol.Optional(CONF_EARTHQUAKE_TIME_RANGE, default="24"): vol.In(EARTHQUAKE_TIME_RANGES),
            vol.Optional(CONF_EARTHQUAKE_MIN_MAGNITUDE, default="0"): vol.In(EARTHQUAKE_MIN_MAGNITUDES),
            vol.Optional(CONF_EARTHQUAKE_MIN_INTENSITY, default="0"): vol.In(EARTHQUAKE_MIN_INTENSITIES),
        })

        return self.async_show_form(
            step_id="earthquake_config",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_prefecture(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the prefecture selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._prefecture = user_input[CONF_PREFECTURE]
            # Get prefecture code from area manager
            if self._area_manager:
                self._prefecture_code = self._area_manager.find_office_code_by_name(self._prefecture)
            return await self.async_step_city()

        # Initialize area manager if not already done
        if not self._area_manager:
            self._area_manager = AreaManager()
            if not await self._area_manager.load_area_data():
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="prefecture",
                    data_schema=vol.Schema({}),
                    errors=errors,
                )

        # Get prefectures for the selected region
        offices = await self._get_offices_for_region()
        
        if not offices:
            errors["base"] = "no_prefectures"
            return self.async_show_form(
                step_id="prefecture",
                data_schema=vol.Schema({}),
                errors=errors,
            )
        
        data_schema = vol.Schema({
            vol.Required(CONF_PREFECTURE): vol.In(list(offices.keys()))
        })

        return self.async_show_form(
            step_id="prefecture",
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
            # Get area code from area manager
            if self._area_manager and self._prefecture_code:
                cities = self._area_manager.get_class20s_for_office(self._prefecture_code)
                self._area_code = cities.get(self._city)
            return await self.async_step_final()

        # Get cities for the selected prefecture
        if not self._area_manager or not self._prefecture_code:
            errors["base"] = "invalid_state"
            return self.async_show_form(
                step_id="city",
                data_schema=vol.Schema({}),
                errors=errors,
            )

        cities = self._area_manager.get_class20s_for_office(self._prefecture_code)
        
        if not cities:
            errors["base"] = "no_cities"
            return self.async_show_form(
                step_id="city",
                data_schema=vol.Schema({}),
                errors=errors,
            )
        
        data_schema = vol.Schema({
            vol.Required(CONF_CITY): vol.In(list(cities.keys()))
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
            
            # Create config entry based on information type
            if self._information_type == INFO_TYPE_EARTHQUAKE:
                # Earthquake info with filters
                time_range_label = EARTHQUAKE_TIME_RANGES.get(self._earthquake_time_range, "過去24時間")
                magnitude_label = EARTHQUAKE_MIN_MAGNITUDES.get(self._earthquake_min_magnitude, "すべて")
                
                title = f"地震情報（{time_range_label}・{magnitude_label}）"
                
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_INFORMATION_TYPE: self._information_type,
                        CONF_UPDATE_INTERVAL: update_interval,
                        CONF_EARTHQUAKE_TIME_RANGE: self._earthquake_time_range,
                        CONF_EARTHQUAKE_MIN_MAGNITUDE: self._earthquake_min_magnitude,
                        CONF_EARTHQUAKE_MIN_INTENSITY: self._earthquake_min_intensity,
                    },
                )
            else:
                # Weather warnings - location required
                warning_area_code = self._prefecture_code
                if self._area_manager and self._area_code:
                    detected_warning_code = self._area_manager.get_warning_area_code(self._area_code)
                    if detected_warning_code:
                        warning_area_code = detected_warning_code
                
                return self.async_create_entry(
                    title=f"{self._prefecture} {self._city}",
                    data={
                        CONF_INFORMATION_TYPE: self._information_type,
                        CONF_REGION: self._region,
                        CONF_PREFECTURE: self._prefecture,
                        CONF_CITY: self._city,
                        CONF_AREA_CODE: self._area_code,
                        CONF_UPDATE_INTERVAL: update_interval,
                        "warning_area_code": warning_area_code,
                        "prefecture_code": self._prefecture_code,
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

    async def _get_offices_for_region(self) -> dict[str, str]:
        """Get prefectures for the selected region."""
        if not self._area_manager or not self._region_code:
            return {}
        
        return self._area_manager.get_offices_for_center(self._region_code)