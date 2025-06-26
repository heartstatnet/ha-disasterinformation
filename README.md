# Home Assistant Japan Meteorological Agency Disaster Information Integration

A Home Assistant custom integration that provides real-time disaster information for Japan, including weather warnings, earthquake data, and tsunami alerts from the Japan Meteorological Agency (JMA).

## Features

- **Weather Warnings & Advisories**: Get alerts for heavy rain, strong winds, snow, and other weather-related warnings
- **Earthquake Information**: Real-time earthquake data including intensity, epicenter, and magnitude
- **Tsunami Information**: Tsunami warnings, advisories, and forecasts
- **Landslide Warnings**: Soil disaster warning information
- **Weather Forecasts**: Local weather prediction data
- **Multi-Region Support**: Monitor multiple areas (home, workplace, family locations)
- **Built-in Dashboard Card**: Conditional card that only shows when alerts are active
- **Home Assistant Automation**: Trigger automations based on disaster alerts
- **HACS Compatible**: Easy installation through Home Assistant Community Store

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository: `https://github.com/heartstatnet/ha-disasterinformation`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "気象庁防災情報" or "JMA Disaster Information"
8. Click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/heartstatnet/ha-disasterinformation/releases)
2. Copy the `custom_components/disasterinformation` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "気象庁防災情報" or "JMA Disaster Information"
3. Follow the configuration steps:
   - **Select Prefecture**: Choose your prefecture from the dropdown
   - **Select Municipality**: Choose your city/ward/town from the dropdown
   - **Information Types**: Select which types of disaster information to monitor:
     - Weather warnings/advisories/special warnings
     - Earthquake information
     - Tsunami information
     - Landslide warnings
     - Weather forecasts
   - **Update Interval**: Set how often to check for updates (minimum 5 minutes, default 10 minutes)
4. Click "Submit" to complete the setup

### Multiple Regions

You can add multiple regions by repeating the configuration process. Each region will create a separate device with its own set of sensors.

## Entities

For each configured region, the integration creates a device named `[Municipality] 気象庁防災情報` (e.g., "千代田区 気象庁防災情報") with the following entities:

### Sensor Entities

#### Weather Warnings (`sensor.[area]_warnings`)
- **State**: Summary of active warnings/advisories (e.g., "大雨警報 雷注意報", "特別警報(大雨)", "発表なし")
- **Attributes**:
  - `headline`: JMA announcement headline
  - `report_datetime`: Publication datetime
  - `special_warnings`: List of special warnings
  - `warnings`: List of warnings
  - `advisories`: List of advisories
  - `raw_xml_url`: Source XML URL

#### Earthquake Information (`sensor.[area]_earthquake`)
- **State**: Maximum seismic intensity observed (e.g., "震度3", "観測なし")
- **Attributes**:
  - `report_datetime`: Publication datetime
  - `event_id`: Earthquake identification ID
  - `hypocenter`: Epicenter location
  - `magnitude`: Magnitude
  - `depth`: Depth
  - `intensity_map`: Map of observed intensities by region

### Binary Sensor Entities

For easier use in automations:

- **Special Warning** (`binary_sensor.[area]_special_warning`): ON when any special warning is active
- **Warning** (`binary_sensor.[area]_warning`): ON when any warning is active
- **Advisory** (`binary_sensor.[area]_advisory`): ON when any advisory is active
- **Earthquake Detected** (`binary_sensor.[area]_earthquake_detected`): ON when earthquake above configured intensity is detected (automatically turns OFF after specified time)

## Dashboard Cards

Here are 3 essential card configurations for displaying disaster information:

### 1. Basic Entity Card (推奨)

シンプルで確実に動作する基本カードです。

```yaml
type: entity
entity: sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_qi_xiang_jing_bao
name: 気象警報・注意報
icon: mdi:alert
```

### 2. Alert-Only Card (警報時のみ表示)

警報や注意報がある時のみ表示される条件付きカードです。

```yaml
type: conditional
conditions:
  - entity: binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_zhu_yi_bao
    state: "on"
card:
  type: entity
  entity: sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_qi_xiang_jing_bao
  name: ⚠️ 気象警報発表中
  icon: mdi:alert
```

### 3. Detailed Information Card (詳細情報)

すべての防災情報を一覧表示する詳細カードです。

```yaml
type: entities
title: 防災情報詳細
entities:
  - entity: sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_qi_xiang_jing_bao
    name: 気象警報・注意報
    icon: mdi:weather-cloudy-alert
  - entity: binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_te_bie_jing_bao
    name: 特別警報
    icon: mdi:alert-octagon
  - entity: binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_jing_bao
    name: 警報
    icon: mdi:alert
  - entity: binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_zhu_yi_bao
    name: 注意報
    icon: mdi:alert-outline
```

## Automation Examples

### Flash Lights on Special Warning
```yaml
automation:
  - alias: "Flash lights on special warning"
    trigger:
      - platform: state
        entity_id: binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_te_bie_jing_bao
        to: 'on'
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          effect: colorloop
      - service: notify.mobile_app
        data:
          message: "Special weather warning issued for Ishikawa!"
```

### Advisory Alert
```yaml
automation:
  - alias: "Advisory notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_zhu_yi_bao
        to: 'on'
    action:
      - service: notify.family
        data:
          message: "Weather advisory issued: {{ states('sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_qi_xiang_jing_bao') }}"
```

## Data Source

This integration uses the [Japan Meteorological Agency Disaster Prevention Information XML Format](https://xml.kishou.go.jp/xmlpull.html) as its data source.

- **Update Frequency**: Configurable (minimum 5 minutes, default 10 minutes)
- **Authentication**: Not required (public API)
- **Format**: JMA XML format
- **Coverage**: All prefectures and municipalities in Japan

## Development

### Project Structure
```
custom_components/disasterinformation/
├── __init__.py              # Integration entry point
├── manifest.json            # Integration metadata
├── config_flow.py          # Configuration UI flow
├── const.py                # Constants and configuration
├── sensor.py               # Sensor platform implementation
├── binary_sensor.py        # Binary sensor platform implementation
├── api.py                  # JMA XML API client
└── strings.json            # UI strings
```

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/heartstatnet/ha-disasterinformation.git
   ```

2. Create a symlink to your Home Assistant custom_components directory:
   ```bash
   ln -s /path/to/ha-disasterinformation/custom_components/disasterinformation /path/to/homeassistant/custom_components/
   ```

3. Restart Home Assistant and check logs:
   ```bash
   tail -f /path/to/homeassistant/home-assistant.log
   ```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Card Display Troubleshooting

If you're having issues with card display, try these standard Home Assistant cards instead:

### Quick Fixes
1. **Use Entity Card**: Most reliable for basic display
2. **Use Conditional Cards**: Only show when alerts are active
3. **Check Entity Names**: Ensure entity IDs match your configured areas
4. **Verify Sensors**: Check that sensors are created and updating

### Common Entity Name Patterns
Entity names are generated based on your configured area (example for Ishikawa Prefecture):
- `sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_qi_xiang_jing_bao` - Weather warnings
- `binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_jing_bao` - Warning status
- `binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_te_bie_jing_bao` - Special warning status
- `binary_sensor.shi_chuan_xian_shi_chuan_xian_quan_yu_zhu_yi_bao` - Advisory status

Note: Entity names are currently generated in transliterated form. Check your actual entity names in Developer Tools → States.

### Testing Your Setup
1. Check available entities in **Developer Tools → States**
2. Look for entities starting with `sensor.` and `binary_sensor.`
3. Use these entity IDs in the card examples above

## Support

- **Documentation**: [GitHub Repository](https://github.com/heartstatnet/ha-disasterinformation)
- **Issues**: [Report bugs or request features](https://github.com/heartstatnet/ha-disasterinformation/issues)
- **Discussions**: [Community discussions](https://github.com/heartstatnet/ha-disasterinformation/discussions)

## Disclaimer

This integration provides disaster information for reference purposes. Always follow official government announcements and evacuation orders. The developers are not responsible for any damages or losses that may occur from the use of this integration.

---

**気象庁防災情報 Home Assistant Integration**  
Bringing Japan's official disaster information to your smart home.