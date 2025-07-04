"""Area code management for JMA BOSAI API."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import aiohttp
import async_timeout

from .const import JMA_BOSAI_AREA_URL

_LOGGER = logging.getLogger(__name__)


class AreaManager:
    """Manages area codes and regional data from JMA BOSAI API."""

    def __init__(self) -> None:
        """Initialize the area manager."""
        self._area_data: Dict[str, Any] = {}
        self._centers: Dict[str, str] = {}
        self._offices: Dict[str, str] = {}
        self._class20s: Dict[str, str] = {}
        self._loaded = False

    async def load_area_data(self) -> bool:
        """Load area data from JMA BOSAI API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(30):
                    async with session.get(JMA_BOSAI_AREA_URL) as response:
                        if response.status == 200:
                            self._area_data = await response.json()
                            self._process_area_data()
                            self._loaded = True
                            _LOGGER.info("Area data loaded successfully")
                            _LOGGER.debug(f"Loaded centers: {list(self._area_data.get('centers', {}).keys())}")
                            return True
                        else:
                            _LOGGER.error(f"Failed to load area data: {response.status}")
                            return False
        except Exception as e:
            _LOGGER.error(f"Error loading area data: {e}")
            return False

    def _process_area_data(self) -> None:
        """Process the raw area data into usable dictionaries."""
        if not self._area_data:
            return

        # Process centers (地方)
        centers = self._area_data.get("centers", {})
        for code, info in centers.items():
            name = info.get("name", "")
            if name:
                self._centers[name] = code

        # Process offices (都道府県)
        offices = self._area_data.get("offices", {})
        for code, info in offices.items():
            name = info.get("name", "")
            if name:
                self._offices[name] = code

        # Process class20s (市区町村)
        class20s = self._area_data.get("class20s", {})
        for code, info in class20s.items():
            name = info.get("name", "")
            if name:
                self._class20s[name] = code

    def get_centers(self) -> Dict[str, str]:
        """Get available centers (地方)."""
        return self._centers.copy()

    def get_offices_for_center(self, center_code: str) -> Dict[str, str]:
        """Get offices (都道府県) for a specific center."""
        if not self._loaded:
            _LOGGER.debug(f"Area data not loaded, returning empty dict")
            return {}

        offices = {}
        centers = self._area_data.get("centers", {})
        center_info = centers.get(center_code, {})
        
        _LOGGER.debug(f"Looking for center_code: {center_code}")
        _LOGGER.debug(f"Available centers: {list(centers.keys())}")
        _LOGGER.debug(f"Center info for {center_code}: {center_info}")
        
        if "children" in center_info:
            _LOGGER.debug(f"Children of center {center_code}: {center_info['children']}")
            for office_code in center_info["children"]:
                office_info = self._area_data.get("offices", {}).get(office_code, {})
                office_name = office_info.get("name", "")
                _LOGGER.debug(f"Office {office_code}: {office_name}")
                if office_name:
                    offices[office_name] = office_code
        else:
            _LOGGER.debug(f"No children found for center {center_code}")

        _LOGGER.debug(f"Returning offices: {offices}")
        return offices

    def get_class20s_for_office(self, office_code: str) -> Dict[str, str]:
        """Get class20s (市区町村) for a specific office."""
        if not self._loaded:
            return {}

        class20s = {}
        offices = self._area_data.get("offices", {})
        office_info = offices.get(office_code, {})
        
        if "children" in office_info:
            for class10_code in office_info["children"]:
                class10_info = self._area_data.get("class10s", {}).get(class10_code, {})
                if "children" in class10_info:
                    for child_code in class10_info["children"]:
                        # Check if child is class15 or class20
                        class15_info = self._area_data.get("class15s", {}).get(child_code, {})
                        if class15_info:
                            # This is a class15, get its class20 children
                            if "children" in class15_info:
                                for class20_code in class15_info["children"]:
                                    class20_info = self._area_data.get("class20s", {}).get(class20_code, {})
                                    class20_name = class20_info.get("name", "")
                                    if class20_name:
                                        class20s[class20_name] = class20_code
                        else:
                            # This might be a direct class20
                            class20_info = self._area_data.get("class20s", {}).get(child_code, {})
                            if class20_info:
                                class20_name = class20_info.get("name", "")
                                if class20_name:
                                    class20s[class20_name] = child_code

        return class20s

    def get_area_name(self, area_code: str) -> Optional[str]:
        """Get area name for a specific area code."""
        if not self._loaded:
            return None

        # Check in centers
        centers = self._area_data.get("centers", {})
        if area_code in centers:
            return centers[area_code].get("name")

        # Check in offices
        offices = self._area_data.get("offices", {})
        if area_code in offices:
            return offices[area_code].get("name")

        # Check in class20s
        class20s = self._area_data.get("class20s", {})
        if area_code in class20s:
            return class20s[area_code].get("name")

        return None

    def get_warning_area_code(self, class20_code: str) -> Optional[str]:
        """Get warning area code (office code) for a class20 code."""
        if not self._loaded:
            return None

        class20s = self._area_data.get("class20s", {})
        class20_info = class20s.get(class20_code, {})
        
        # Find parent office code by traversing up the hierarchy
        parent_code = class20_info.get("parent")
        if parent_code:
            # Check if parent is class15
            class15s = self._area_data.get("class15s", {})
            if parent_code in class15s:
                class15_info = class15s[parent_code]
                class10_code = class15_info.get("parent")
                if class10_code:
                    class10s = self._area_data.get("class10s", {})
                    class10_info = class10s.get(class10_code, {})
                    if class10_info:
                        office_code = class10_info.get("parent")
                        if office_code:
                            return office_code
            
            # Check if parent is class10 (direct hierarchy)
            class10s = self._area_data.get("class10s", {})
            if parent_code in class10s:
                class10_info = class10s[parent_code]
                office_code = class10_info.get("parent")
                if office_code:
                    return office_code
            
            # Check if parent is directly an office
            offices = self._area_data.get("offices", {})
            if parent_code in offices:
                return parent_code

        return None

    def get_prefecture_name_by_office_code(self, office_code: str) -> Optional[str]:
        """Get prefecture name by office code."""
        if not self._loaded:
            return None
            
        offices = self._area_data.get("offices", {})
        office_info = offices.get(office_code, {})
        return office_info.get("name")

    def find_office_code_by_name(self, prefecture_name: str) -> Optional[str]:
        """Find office code by prefecture name."""
        if not self._loaded:
            return None
            
        offices = self._area_data.get("offices", {})
        for code, info in offices.items():
            if info.get("name") == prefecture_name:
                return code
        return None

    def get_class20_info(self, class20_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed class20 information."""
        if not self._loaded:
            return None
            
        class20s = self._area_data.get("class20s", {})
        return class20s.get(class20_code)

    @property
    def is_loaded(self) -> bool:
        """Check if area data is loaded."""
        return self._loaded