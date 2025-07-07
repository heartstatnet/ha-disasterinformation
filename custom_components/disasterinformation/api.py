"""API client for JMA BOSAI API."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp
import async_timeout

from .const import (
    JMA_BOSAI_WARNING_URL,
    JMA_BOSAI_EARTHQUAKE_URL,
    WARNING_CODES,
    WARNING_SEVERITY,
)

_LOGGER = logging.getLogger(__name__)


class JMABosaiApiClient:
    """Client for JMA BOSAI API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def get_warning_data(self, area_code: str, city_area_code: str = None) -> Optional[Dict[str, Any]]:
        """Get warning data for a specific area."""
        try:
            url = f"{JMA_BOSAI_WARNING_URL}/{area_code}.json"
            async with async_timeout.timeout(30):
                async with self._session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_warning_data(data, area_code, city_area_code)
                    else:
                        _LOGGER.error(f"Failed to get warning data: {response.status}")
                        return None
        except Exception as e:
            _LOGGER.error(f"Error getting warning data: {e}")
            return None

    async def get_earthquake_data(
        self, 
        time_range_hours: int = 24,
        min_magnitude: float = 0.0
    ) -> Optional[Dict[str, Any]]:
        """Get filtered earthquake data."""
        try:
            # Get earthquake list first
            list_url = f"{JMA_BOSAI_EARTHQUAKE_URL}/list.json"
            async with async_timeout.timeout(30):
                async with self._session.get(list_url) as response:
                    if response.status == 200:
                        earthquake_list = await response.json()
                        if earthquake_list:
                            # Filter and get multiple earthquake details
                            return await self._get_filtered_earthquakes(
                                earthquake_list, time_range_hours, min_magnitude
                            )
                    else:
                        _LOGGER.error(f"Failed to get earthquake list: {response.status}")
                        return None
        except Exception as e:
            _LOGGER.error(f"Error getting earthquake data: {e}")
            return None

    async def _get_filtered_earthquakes(
        self, 
        earthquake_list: List[Dict[str, Any]], 
        time_range_hours: int,
        min_magnitude: float
    ) -> Dict[str, Any]:
        """Get filtered earthquake details using only list.json data."""
        from datetime import datetime, timedelta
        
        # Calculate time threshold
        now = datetime.now()
        time_threshold = now - timedelta(hours=time_range_hours)
        
        _LOGGER.debug(f"Filtering earthquakes: time_range={time_range_hours}h, min_mag={min_magnitude}")
        _LOGGER.debug(f"Time threshold: {time_threshold}")
        
        filtered_earthquakes = []
        
        for earthquake_info in earthquake_list:
            try:
                # Check time filter using 'at' field (earthquake occurrence time)
                origin_time_str = earthquake_info.get("at")
                if origin_time_str:
                    origin_time = datetime.fromisoformat(origin_time_str.replace('Z', '+00:00'))
                    if origin_time.replace(tzinfo=None) < time_threshold:
                        continue
                
                # Check magnitude filter
                magnitude_str = earthquake_info.get("mag")
                if magnitude_str and magnitude_str != "--" and magnitude_str != "M不明":
                    try:
                        magnitude = float(magnitude_str)
                        if magnitude < min_magnitude:
                            continue
                    except ValueError:
                        continue
                
                _LOGGER.debug(f"Earthquake passed filters: {earthquake_info.get('anm')} M{magnitude_str}")
                
                # Create simplified earthquake data from list.json only
                earthquake_data = {
                    "event_id": earthquake_info.get("eid", ""),
                    "report_datetime": earthquake_info.get("rdt", ""),
                    "origin_time": earthquake_info.get("at", ""),
                    "hypocenter": earthquake_info.get("anm", ""),
                    "magnitude": magnitude_str if magnitude_str and magnitude_str != "--" else None,
                    "status": "地震発生"
                }
                filtered_earthquakes.append(earthquake_data)
                
                # Limit to reasonable number
                if len(filtered_earthquakes) >= 50:
                    break
                    
            except Exception as e:
                _LOGGER.warning(f"Error processing earthquake {earthquake_info}: {e}")
                continue
        
        # Sort by origin time (newest first)
        filtered_earthquakes.sort(
            key=lambda x: x.get("list_occurrence_time", x.get("origin_time", "")), reverse=True
        )
        
        _LOGGER.debug(f"Filtered earthquakes: {len(filtered_earthquakes)} out of {len(earthquake_list)}")
        
        # Create recent earthquakes list (last 10 with essential info only)
        recent_earthquakes = []
        for eq in filtered_earthquakes[:10]:
            recent_eq = {
                "report_datetime": eq.get("report_datetime", ""),
                "hypocenter": eq.get("hypocenter", ""),
                "magnitude": eq.get("magnitude", ""),
                "origin_time": eq.get("origin_time", ""),
                "event_id": eq.get("event_id", ""),
            }
            recent_earthquakes.append(recent_eq)

        return {
            "earthquakes": filtered_earthquakes,
            "count": len(filtered_earthquakes),
            "latest_earthquake": filtered_earthquakes[0] if filtered_earthquakes else None,
            "recent_earthquakes": recent_earthquakes,
            "time_range_hours": time_range_hours,
            "min_magnitude": min_magnitude,
            "status": "正常" if filtered_earthquakes else "該当なし"
        }


    def _process_warning_data(self, data: Dict[str, Any], target_area_code: str, city_area_code: str = None) -> Dict[str, Any]:
        """Process warning data into structured format."""
        processed_data = {
            "status": "発表なし",
            "warnings": [],
            "advisories": [],
            "emergency_warnings": [],
            "headline": "",
            "report_datetime": None,
            "target_area": "",
            "raw_data": data,
        }

        if not data:
            return processed_data

        # Extract basic information
        if "headline" in data:
            processed_data["headline"] = data["headline"]

        if "reportDatetime" in data:
            processed_data["report_datetime"] = data["reportDatetime"]

        if "targetArea" in data:
            processed_data["target_area"] = data["targetArea"]

        # Process area types and warnings
        area_types = data.get("areaTypes", [])
        active_warnings = []
        active_advisories = []
        active_emergency_warnings = []

        _LOGGER.debug(f"Processing warning data for target area code: {target_area_code}, city area code: {city_area_code}")

        for area_type in area_types:
            areas = area_type.get("areas", [])
            for area in areas:
                area_name = area.get("name", "")
                area_code = area.get("code", "")
                
                _LOGGER.debug(f"Checking area: {area_name} (code: {area_code})")
                
                # Check for warnings and filter by city area code if specified
                warnings = area.get("warnings", [])
                for warning in warnings:
                    warning_status = warning.get("status")
                    
                    if warning_status in ["発表", "継続"]:
                        warning_code = warning.get("code")
                        
                        # Check if warning applies to the specific city
                        warning_applies = False
                        
                        # JMA BOSAI API structure: warnings are directly under each area
                        # If city_area_code is specified, only include warnings from that specific area
                        if city_area_code:
                            # Only include warnings from the specific city area code
                            if area_code == city_area_code:
                                warning_applies = True
                        else:
                            # If no specific city is specified, include all warnings from the target area
                            warning_applies = True
                        
                        if warning_applies:
                            # Determine warning type and severity
                            warning_type = self._determine_warning_type(warning_code)
                            
                            warning_info = {
                                "code": warning_code,
                                "name": warning_type["name"],
                                "severity": warning_type["severity"],
                                "area": area_name,
                                "area_code": area_code,
                                "status": warning_status,
                            }
                            
                            _LOGGER.debug(f"Found applicable warning: {warning_info}")
                            
                            if warning_type["severity"] == "特別警報":
                                active_emergency_warnings.append(warning_info)
                            elif warning_type["severity"] == "警報":
                                active_warnings.append(warning_info)
                            elif warning_type["severity"] == "注意報":
                                active_advisories.append(warning_info)

        # Update processed data
        processed_data["warnings"] = active_warnings
        processed_data["advisories"] = active_advisories
        processed_data["emergency_warnings"] = active_emergency_warnings

        # Set overall status
        if active_emergency_warnings:
            processed_data["status"] = "特別警報発表中"
        elif active_warnings:
            processed_data["status"] = "警報発表中"
        elif active_advisories:
            processed_data["status"] = "注意報発表中"

        _LOGGER.debug(f"Final processed data: {processed_data['status']}, warnings: {len(active_warnings)}, advisories: {len(active_advisories)}")

        return processed_data

    def _determine_warning_type(self, warning_code: str) -> Dict[str, str]:
        """Determine warning type and severity from code."""
        # Default values
        warning_info = {
            "name": f"警報コード{warning_code}",
            "severity": "注意報"
        }
        
        if warning_code in WARNING_CODES:
            warning_name = WARNING_CODES[warning_code]
            warning_info["name"] = warning_name
            
            # Determine severity based on name
            if "特別警報" in warning_name:
                warning_info["severity"] = "特別警報"
            elif "警報" in warning_name:
                warning_info["severity"] = "警報"
            else:
                warning_info["severity"] = "注意報"
        
        return warning_info

