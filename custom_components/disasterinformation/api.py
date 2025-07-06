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
    EARTHQUAKE_INTENSITY,
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
        min_magnitude: float = 0.0,
        min_intensity: str = "0"
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
                                earthquake_list, time_range_hours, min_magnitude, min_intensity
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
        min_magnitude: float,
        min_intensity: str
    ) -> Dict[str, Any]:
        """Get filtered earthquake details."""
        from datetime import datetime, timedelta
        
        # Calculate time threshold
        now = datetime.now()
        time_threshold = now - timedelta(hours=time_range_hours)
        
        _LOGGER.debug(f"Filtering earthquakes: time_range={time_range_hours}h, min_mag={min_magnitude}, min_intensity={min_intensity}")
        _LOGGER.debug(f"Time threshold: {time_threshold}")
        
        filtered_earthquakes = []
        
        for earthquake_info in earthquake_list:
            try:
                # Pre-filter using list.json data for efficiency
                
                # Check time filter using 'at' field (earthquake occurrence time)
                origin_time_str = earthquake_info.get("at")
                if origin_time_str:
                    origin_time = datetime.fromisoformat(origin_time_str.replace('Z', '+00:00'))
                    if origin_time.replace(tzinfo=None) < time_threshold:
                        continue
                
                # Check magnitude filter
                magnitude_str = earthquake_info.get("mag")
                if magnitude_str and magnitude_str != "--":
                    try:
                        magnitude = float(magnitude_str)
                        if magnitude < min_magnitude:
                            continue
                    except ValueError:
                        continue
                
                # Check intensity filter using 'maxi' field (maximum intensity)
                max_intensity_code = earthquake_info.get("maxi", "0")
                if not self._intensity_meets_threshold(max_intensity_code, min_intensity):
                    continue
                
                _LOGGER.debug(f"Earthquake passed filters: {earthquake_info.get('anm')} M{magnitude_str} Max震度{max_intensity_code}")
                
                # Get detailed earthquake data
                earthquake_data = await self._get_earthquake_details(earthquake_info)
                if earthquake_data:
                    # Add list.json data for completeness
                    earthquake_data.update({
                        "list_report_datetime": earthquake_info.get("rdt"),
                        "list_occurrence_time": earthquake_info.get("at"),
                        "list_area_name": earthquake_info.get("anm"),
                        "list_magnitude": magnitude_str,
                        "list_max_intensity": max_intensity_code,
                    })
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
                "report_datetime": eq.get("report_datetime", eq.get("list_report_datetime", "")),
                "hypocenter": eq.get("hypocenter", eq.get("list_area_name", "")),
                "magnitude": eq.get("magnitude", eq.get("list_magnitude", "")),
                "origin_time": eq.get("origin_time", eq.get("list_occurrence_time", "")),
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
            "min_intensity": min_intensity,
            "status": "正常" if filtered_earthquakes else "該当なし"
        }

    def _intensity_meets_threshold(self, intensity_code: str, min_intensity: str) -> bool:
        """Check if intensity meets minimum threshold."""
        if min_intensity == "0":
            return True
            
        # Convert intensity codes to numeric values for comparison
        intensity_values = {
            "1": 1, "2": 2, "3": 3, "4": 4,
            "5-": 5, "5+": 6, "6-": 7, "6+": 8, "7": 9
        }
        
        current_value = intensity_values.get(intensity_code, 0)
        threshold_value = intensity_values.get(min_intensity, 0)
        
        return current_value >= threshold_value

    async def _get_earthquake_details(self, earthquake_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get detailed earthquake information."""
        try:
            json_file = earthquake_info.get("json")
            if not json_file:
                return None

            url = f"{JMA_BOSAI_EARTHQUAKE_URL}/{json_file}"
            async with async_timeout.timeout(30):
                async with self._session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_earthquake_data(data)
                    else:
                        _LOGGER.error(f"Failed to get earthquake details: {response.status}")
                        return None
        except Exception as e:
            _LOGGER.error(f"Error getting earthquake details: {e}")
            return None

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

    def _process_earthquake_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process earthquake data into structured format."""
        processed_data = {
            "status": "地震情報なし",
            "event_id": "",
            "report_datetime": None,
            "origin_time": None,
            "hypocenter": "",
            "magnitude": None,
            "depth": None,
            "max_intensity": "",
            "max_intensity_code": "",
            "intensity_areas": [],
            "raw_data": data,
        }

        if not data:
            return processed_data

        # Extract basic information from Head section (JMA BOSAI JSON format)
        head = data.get("Head", {})
        if head:
            event_id = head.get("EventID", "")
            if event_id:
                processed_data["event_id"] = event_id

            report_datetime = head.get("ReportDateTime")
            if report_datetime:
                processed_data["report_datetime"] = report_datetime

        # Extract earthquake details from Body.Earthquake (JMA BOSAI JSON format)
        body = data.get("Body", {})
        earthquake = body.get("Earthquake", {}) if body else {}
        
        if earthquake:
            # Origin time
            origin_time = earthquake.get("OriginTime")
            if origin_time:
                processed_data["origin_time"] = origin_time

            # Hypocenter information
            hypocenter = earthquake.get("Hypocenter", {})
            if hypocenter:
                hypocenter_area = hypocenter.get("Area", {})
                if hypocenter_area:
                    hypocenter_name = hypocenter_area.get("Name", "")
                    if hypocenter_name:
                        processed_data["hypocenter"] = hypocenter_name
                    
                    # Coordinate information
                    coordinate = hypocenter_area.get("Coordinate", {})
                    if coordinate:
                        depth = coordinate.get("Depth", {}).get("Value")
                        if depth:
                            processed_data["depth"] = f"{depth}km"

            # Magnitude
            magnitude = earthquake.get("Magnitude")
            if magnitude and magnitude != "--":
                processed_data["magnitude"] = magnitude

        # Extract intensity information from Body.Intensity
        intensity_info = body.get("Intensity", {}) if body else {}
        if intensity_info:
            observation = intensity_info.get("Observation", {})
            if observation:
                # Maximum intensity
                max_intensity = observation.get("MaxInt")
                if max_intensity:
                    intensity_name = EARTHQUAKE_INTENSITY.get(max_intensity, f"震度{max_intensity}")
                    processed_data["max_intensity"] = intensity_name
                    processed_data["max_intensity_code"] = max_intensity
                    processed_data["status"] = f"最大{intensity_name}"

                # Extract intensity areas
                intensity_areas = []
                prefs = observation.get("Pref", [])
                for pref in prefs:
                    pref_name = pref.get("Name", "")
                    areas = pref.get("Area", [])
                    for area in areas:
                        area_name = area.get("Name", "")
                        max_int = area.get("MaxInt", "")
                        if max_int:
                            intensity_name = EARTHQUAKE_INTENSITY.get(max_int, f"震度{max_int}")
                            intensity_areas.append({
                                "prefecture": pref_name,
                                "area": area_name,
                                "intensity": intensity_name,
                                "intensity_code": max_int,
                            })

                processed_data["intensity_areas"] = intensity_areas

        # Set default status if not set
        if processed_data["status"] == "地震情報なし" and processed_data["event_id"]:
            processed_data["status"] = "地震発生"

        _LOGGER.debug(f"Processed earthquake data: {processed_data['hypocenter']} M{processed_data['magnitude']} 最大{processed_data['max_intensity']}")

        return processed_data