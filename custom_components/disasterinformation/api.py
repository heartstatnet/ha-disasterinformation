"""JMA XML API client for disaster information."""
from __future__ import annotations

import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
from homeassistant.core import HomeAssistant

from .const import JMA_EXTRA_FEED_URL

_LOGGER = logging.getLogger(__name__)


class JMAApiClient:
    """Client for JMA XML API."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the API client."""
        self.hass = hass
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def async_get_disaster_info(self, prefecture: str, city: str) -> Dict[str, Any]:
        """Get disaster information for specified region."""
        try:
            session = await self._get_session()
            
            # Get Atom feed
            async with session.get(JMA_EXTRA_FEED_URL) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to fetch JMA feed: {response.status}")
                    return self._empty_data()
                
                feed_content = await response.text()
            
            # Parse Atom feed
            warnings = await self._parse_atom_feed(feed_content, prefecture, city)
            
            return {
                "prefecture": prefecture,
                "city": city,
                "warnings": warnings,
                "last_update": datetime.now().isoformat(),
                "status": "ok"
            }
            
        except Exception as e:
            _LOGGER.error(f"Error fetching disaster information: {e}")
            return self._empty_data()

    async def _parse_atom_feed(self, feed_content: str, prefecture: str, city: str) -> List[Dict[str, Any]]:
        """Parse Atom feed and extract relevant warnings."""
        try:
            root = ET.fromstring(feed_content)
            
            # Define namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            warnings = []
            
            # Find entries related to the specified prefecture
            for entry in root.findall('.//atom:entry', ns):
                title_elem = entry.find('atom:title', ns)
                content_elem = entry.find('atom:content', ns)
                updated_elem = entry.find('atom:updated', ns)
                
                if title_elem is None or content_elem is None:
                    continue
                
                title = title_elem.text or ""
                content = content_elem.text or ""
                updated = updated_elem.text if updated_elem is not None else ""
                
                # Check if this entry is related to our prefecture
                if prefecture in title or prefecture in content:
                    warning_info = self._extract_warning_info(title, content, updated)
                    if warning_info:
                        warnings.append(warning_info)
            
            return warnings
            
        except ET.ParseError as e:
            _LOGGER.error(f"XML parsing error: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Error parsing Atom feed: {e}")
            return []

    def _extract_warning_info(self, title: str, content: str, updated: str) -> Dict[str, Any] | None:
        """Extract warning information from entry."""
        try:
            # Determine warning types
            warning_types = []
            severity = "注意報"
            
            # Check for special warnings (特別警報)
            if "特別警報" in content:
                severity = "特別警報"
                if "大雨" in content:
                    warning_types.append("大雨特別警報")
                if "暴風" in content:
                    warning_types.append("暴風特別警報")
            
            # Check for warnings (警報)
            elif "警報" in content:
                severity = "警報"
                if "大雨" in content:
                    warning_types.append("大雨警報")
                if "洪水" in content:
                    warning_types.append("洪水警報")
                if "暴風" in content:
                    warning_types.append("暴風警報")
                if "波浪" in content:
                    warning_types.append("波浪警報")
            
            # Check for advisories (注意報)
            else:
                if "大雨" in content:
                    warning_types.append("大雨注意報")
                if "洪水" in content:
                    warning_types.append("洪水注意報")
                if "強風" in content:
                    warning_types.append("強風注意報")
                if "波浪" in content:
                    warning_types.append("波浪注意報")
                if "雷" in content or "落雷" in content:
                    warning_types.append("雷注意報")
                if "土砂災害" in content:
                    warning_types.append("土砂災害注意報")
                if "竜巻" in content:
                    warning_types.append("竜巻注意報")
                if "濃霧" in content:
                    warning_types.append("濃霧注意報")
            
            if not warning_types:
                return None
            
            return {
                "types": warning_types,
                "severity": severity,
                "content": content.strip(),
                "title": title.strip(),
                "updated": updated,
                "is_active": True
            }
            
        except Exception as e:
            _LOGGER.error(f"Error extracting warning info: {e}")
            return None

    def _empty_data(self) -> Dict[str, Any]:
        """Return empty data structure."""
        return {
            "prefecture": "",
            "city": "",
            "warnings": [],
            "last_update": None,
            "status": "error"
        }