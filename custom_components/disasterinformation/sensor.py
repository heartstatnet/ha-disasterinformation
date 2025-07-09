"""Sensor platform for 気象庁防災情報."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_NAME_WARNING, ENTITY_NAME_EARTHQUAKE, INFO_TYPE_EARTHQUAKE, INFO_TYPE_WEATHER_WARNING


def _get_entity_prefix(config_entry: ConfigEntry) -> str:
    """Generate English entity prefix from prefecture and city."""
    prefecture = config_entry.data.get('prefecture', '')
    city = config_entry.data.get('city', '')
    
    # Simple romanization mapping for common prefectures/cities
    prefecture_map = {
        '福岡県': 'fukuoka',
        '東京都': 'tokyo',
        '大阪府': 'osaka',
        '愛知県': 'aichi',
        '神奈川県': 'kanagawa',
        '埼玉県': 'saitama',
        '千葉県': 'chiba',
        '兵庫県': 'hyogo',
        '北海道': 'hokkaido',
        '宮城県': 'miyagi',
        '広島県': 'hiroshima',
        '京都府': 'kyoto',
        '静岡県': 'shizuoka',
        '岐阜県': 'gifu',
        '茨城県': 'ibaraki',
        '栃木県': 'tochigi',
        '群馬県': 'gunma',
        '新潟県': 'niigata',
        '長野県': 'nagano',
        '山梨県': 'yamanashi',
        '富山県': 'toyama',
        '石川県': 'ishikawa',
        '福井県': 'fukui',
        '三重県': 'mie',
        '滋賀県': 'shiga',
        '奈良県': 'nara',
        '和歌山県': 'wakayama',
        '鳥取県': 'tottori',
        '島根県': 'shimane',
        '岡山県': 'okayama',
        '山口県': 'yamaguchi',
        '徳島県': 'tokushima',
        '香川県': 'kagawa',
        '愛媛県': 'ehime',
        '高知県': 'kochi',
        '福岡県': 'fukuoka',
        '佐賀県': 'saga',
        '長崎県': 'nagasaki',
        '熊本県': 'kumamoto',
        '大分県': 'oita',
        '宮崎県': 'miyazaki',
        '鹿児島県': 'kagoshima',
        '沖縄県': 'okinawa',
    }
    
    city_map = {
        '北九州市': 'kitakyushushi',
        '福岡市': 'fukuokashi',
        '札幌市': 'sapporoshi',
        '仙台市': 'sendaishi',
        '千葉市': 'chibashi',
        '横浜市': 'yokohamashi',
        '川崎市': 'kawasakishi',
        '名古屋市': 'nagoyashi',
        '京都市': 'kyotoshi',
        '大阪市': 'osakashi',
        '堺市': 'sakaishi',
        '神戸市': 'kobeshi',
        '広島市': 'hiroshimashi',
        '北九州市': 'kitakyushushi',
        '福岡市': 'fukuokashi',
    }
    
    # Convert prefecture and city to English
    prefecture_en = prefecture_map.get(prefecture, prefecture.replace('県', '').replace('府', '').replace('都', '').replace('道', ''))
    
    # For cities, use mapping if available, otherwise use romanization fallback
    if city in city_map:
        city_en = city_map[city]
    else:
        # Simple romanization for unmapped cities
        city_clean = city.replace('市', '').replace('町', '').replace('村', '').replace('区', '')
        # Convert common kanji to romaji (basic mapping)
        city_clean = city_clean.replace('東', 'higashi').replace('西', 'nishi').replace('南', 'minami').replace('北', 'kita')
        city_clean = city_clean.replace('中', 'naka').replace('上', 'kami').replace('下', 'shimo')
        city_clean = city_clean.replace('新', 'shin').replace('古', 'ko').replace('大', 'dai')
        city_clean = city_clean.replace('小', 'ko').replace('山', 'yama').replace('川', 'kawa')
        city_clean = city_clean.replace('田', 'ta').replace('本', 'hon').replace('原', 'hara')
        city_clean = city_clean.replace('島', 'shima').replace('崎', 'saki').replace('浜', 'hama')
        city_clean = city_clean.replace('野', 'no').replace('谷', 'tani').replace('丘', 'oka')
        
        if city.endswith('市'):
            city_en = city_clean + 'shi'
        elif city.endswith('町'):
            city_en = city_clean + 'cho'
        elif city.endswith('村'):
            city_en = city_clean + 'mura'
        elif city.endswith('区'):
            city_en = city_clean + 'ku'
        else:
            city_en = city_clean
    
    return f"{prefecture_en}_{city_en}"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Determine which sensors to create based on information type
    information_type = config_entry.data.get("information_type", INFO_TYPE_WEATHER_WARNING)
    
    entities = []
    
    if information_type == INFO_TYPE_EARTHQUAKE:
        # Create earthquake sensor
        entities.append(DisasterEarthquakeSensor(coordinator, config_entry))
    else:
        # Create warning sensor
        entities.append(DisasterWarningsSensor(coordinator, config_entry))
    
    async_add_entities(entities)


class DisasterWarningsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for disaster warnings."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data['prefecture']} {config_entry.data['city']} {ENTITY_NAME_WARNING}"
        entity_prefix = get_entity_prefix(config_entry.data.get('prefecture', ''), config_entry.data.get('city', ''))
        self._attr_unique_id = f"{entity_prefix}_warnings_summary"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data or self.coordinator.data.get("status") == "error":
            return "不明"
        
        # Get all types of warnings from coordinator data
        all_warnings = self.coordinator.data.get("warnings", [])
        all_advisories = self.coordinator.data.get("advisories", [])
        all_emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        
        # Check if any warnings/advisories exist
        total_alerts = len(all_warnings) + len(all_advisories) + len(all_emergency_warnings)
        if total_alerts == 0:
            return "発表なし"
        
        # Separate by severity (they're already separated in the API response)
        special_warnings = all_emergency_warnings
        regular_warnings = all_warnings  
        advisories = all_advisories
        
        if special_warnings:
            types = [warning.get("name", "不明") for warning in special_warnings]
            return f"特別警報({' '.join(types)})"
        elif regular_warnings:
            types = [warning.get("name", "不明") for warning in regular_warnings]
            return f"警報({' '.join(types)})"
        elif advisories:
            types = [warning.get("name", "不明") for warning in advisories]
            return f"注意報({' '.join(types)})"
        
        return "発表なし"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        # Get separated warning data from coordinator
        all_warnings = self.coordinator.data.get("warnings", [])
        all_advisories = self.coordinator.data.get("advisories", [])
        all_emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        
        # Extract warning names for each severity
        special_warning_types = [w.get("name", "不明") for w in all_emergency_warnings]
        warning_types = [w.get("name", "不明") for w in all_warnings]
        advisory_types = [w.get("name", "不明") for w in all_advisories]
        
        # Calculate total count
        total_count = len(all_warnings) + len(all_advisories) + len(all_emergency_warnings)
        
        return {
            "prefecture": self.coordinator.data.get("prefecture"),
            "city": self.coordinator.data.get("city"),
            "special_warnings": special_warning_types,
            "warnings": warning_types,
            "advisories": advisory_types,
            "warning_count": total_count,
            "has_special_warning": len(all_emergency_warnings) > 0,
            "has_warning": len(all_warnings) > 0,
            "has_advisory": len(all_advisories) > 0,
            "last_update": self.coordinator.data.get("last_update"),
            "status": self.coordinator.data.get("status", "unknown"),
            "raw_warnings": all_warnings + all_advisories + all_emergency_warnings,  # 詳細なデバッグ情報
        }

    @property
    def icon(self) -> str:
        """Return the icon for the sensor based on highest severity level."""
        if not self.coordinator.data:
            return "mdi:weather-sunny"
        
        # Check highest severity level and return appropriate icon
        emergency_warnings = self.coordinator.data.get("emergency_warnings", [])
        warnings = self.coordinator.data.get("warnings", [])
        advisories = self.coordinator.data.get("advisories", [])
        
        if emergency_warnings:
            return "mdi:weather-tornado"  # 特別警報 - 最高レベル
        elif warnings:
            return "mdi:weather-lightning-rainy"  # 警報 - 重要レベル
        elif advisories:
            return "mdi:weather-cloudy-alert"  # 注意報 - 注意レベル
        else:
            return "mdi:weather-sunny"  # 発表なし - 平常時


class DisasterEarthquakeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for earthquake information."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = f"{ENTITY_NAME_EARTHQUAKE}"
        entity_prefix = get_entity_prefix(config_entry.data.get('prefecture', ''), config_entry.data.get('city', ''))
        self._attr_unique_id = f"{entity_prefix}_earthquake"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data or self.coordinator.data.get("status") == "error":
            return "不明"
        
        count = self.coordinator.data.get("count", 0)
        if count == 0:
            return "該当する地震なし"
        elif count == 1:
            return "1件の地震"
        else:
            return f"{count}件の地震"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        earthquakes = data.get("earthquakes", [])
        latest = data.get("latest_earthquake")
        
        attributes = {
            "earthquake_count": data.get("count", 0),
            "time_range_hours": data.get("time_range_hours", 24),
            "min_magnitude": data.get("min_magnitude", 0.0),
            "status": data.get("status", "unknown"),
        }
        
        # Add latest earthquake details
        if latest:
            attributes.update({
                "latest_earthquake": {
                    "event_id": latest.get("event_id", ""),
                    "origin_time": latest.get("origin_time", ""),
                    "report_datetime": latest.get("report_datetime", ""),
                    "hypocenter": latest.get("hypocenter", ""),
                    "magnitude": latest.get("magnitude", ""),
                }
            })
        
        # Add recent earthquakes list (10 most recent with report_datetime, hypocenter, magnitude only)
        recent_earthquakes = data.get("recent_earthquakes", [])
        formatted_recent = []
        for eq in recent_earthquakes:
            formatted_recent.append({
                "report_datetime": eq.get("report_datetime", ""),
                "hypocenter": eq.get("hypocenter", ""),
                "magnitude": eq.get("magnitude", ""),
            })
        
        attributes["recent_earthquakes"] = formatted_recent
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:earth"