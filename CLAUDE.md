# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

本プロジェクトは日本語で回答してください。


## Project Overview

近年、気象警報や地震、津波といった防災情報の重要性が高まっている。これらの情報をスマートホームの中核であるHome Assistant (HA) 上で一元的に管理し、通知や照明制御などのオートメーションに活用することで、ユーザーの防災意識向上と迅速な初動対応を支援することを目的とする。

本プロジェクトでは、[気象庁が提供する「気象庁防災情報XMLフォーマット」](https://xml.kishou.go.jp/xmlpull.html)」をデータソースとし、日本のユーザーが自身の居住地域や関心のある地域の防災情報をHA上で容易に扱えるようにするためのカスタムインテグレーションを開発する。

### 機能要件

#### インストールと設定 (Config Flow)
ユーザーがHAのUIから直感的に設定を完了できるようにする。

- **地域設定**
    - ユーザーがエリアコードを直接入力する必要がないように、ドロップダウンリストで地域を選択できること。
    - 1段目: 都道府県の選択
    - 2段目: 1で選択した都道府県に属する市区町村の選択
- **取得する情報の種類**
    - 以下の情報種別から、取得したいものをチェックボックスで選択できること。（初期は限定的な実装から開始することも可）
        - [ ] 気象警報・注意報・特別警報
        - [ ] 地震情報 (震度速報、震源・震度に関する情報)
        - [ ] 津波情報 (津波警報・注意報・予報)
        - [ ] 土砂災害警戒情報
        - [ ] 天気予報
- **更新間隔**
    - 気象庁サーバーの定期刊行物リストをチェックする間隔を分単位で設定できること。
    - デフォルト値は`10分`とする。最小値は`5分`とし、過度なアクセスを防ぐ。
- **複数地域の登録**
    - 複数の地域（例：自宅、勤務先、実家）を登録・管理できること。設定画面から「別の地域を追加」操作が可能であること。

#### データ提供機能 (Entity)
設定された地域ごとに1つの**Device**を作成し、その配下に情報種別ごとの**Entity**を提供する。

- **Device**
    - **Device名**: `（市区町村名） 気象庁防災情報` (例: `千代田区 気象庁防災情報`)
    - **Manufacturer**: `Japan Meteorological Agency`
    - **Model**: `JMA Disaster Information`

- **Sensor Entity**
    - **気象警報・注意報 (`sensor.chiyoda_ku_warnings`)**
        - **State**: 現在発表中の警報・注意報の概要 (例: `大雨警報 雷注意報`, `特別警報(大雨)`, `発表なし`)
        - **Attributes**:
            - `headline`: 気象庁発表ヘッドライン
            - `report_datetime`: 発表日時
            - `special_warnings`: 特別警報のリスト
            - `warnings`: 警報のリスト
            - `advisories`: 注意報のリスト
            - `raw_xml_url`: 参照したXMLのURL
    - **地震情報 (`sensor.chiyoda_ku_earthquake`)**
        - **State**: 最後に観測された自身の最大震度 (例: `震度3`, `観測なし`)
        - **Attributes**:
            - `report_datetime`: 発表日時
            - `event_id`: 地震識別ID
            - `hypocenter`: 震源地
            - `magnitude`: マグニチュード
            - `depth`: 深さ
            - `intensity_map`: 観測された震度と地域のマップ
    - *その他、津波情報などのSensor Entityも同様の思想で設計する。*

- **Binary Sensor Entity**
    - オートメーションでの利用を容易にするため、状態がON/OFFで表現されるBinary Sensorを提供する。
    - **特別警報 (`binary_sensor.chiyoda_ku_special_warning`)**: 特別警報が発表中なら`ON`
    - **警報 (`binary_sensor.chiyoda_ku_warning`)**: 何らかの警報が発表中なら`ON`
    - **注意報 (`binary_sensor.chiyoda_ku_advisory`)**: 何らかの注意報が発表中なら`ON`
    - **地震 (`binary_sensor.chiyoda_ku_earthquake_detected`)**: 設定震度以上の地震が検知されたら`ON`（一定時間後に`OFF`に戻る）

- **HACS対応**
    - Home Assistant Community Store (HACS) 経由で容易にインストールできるよう、リポジトリ構成を整える。
- **ドキュメント (README.md)**
    - 以下の内容を含む、分かりやすいドキュメントを作成する。
        - インテグレーションの概要
        - HACSを利用したインストール方法
        - 設定方法の詳細
        - 提供されるEntityの一覧と解説
        - オートメーションの記述例
- **ライセンス**
    - MIT License や Apache License 2.0 などの寛容なオープンソースライセンスを適用する。


**Repository**: https://github.com/heartstatnet/ha-disasterinformation.git

## Development Commands

Since this is a Home Assistant integration, there are no traditional build commands. Development involves:

```bash
# No build commands - HA integrations are loaded directly by Home Assistant
# Testing requires running within Home Assistant environment

# Create symlink for development (example)
ln -s /path/to/this/repo/custom_components/disasterinformation /path/to/homeassistant/custom_components/

# Restart Home Assistant to load changes
# Check logs for errors: tail -f /path/to/homeassistant/home-assistant.log
```

## Development Workflow

1. **コードの変更**: `custom_components/disasterinformation/` 内のファイルを編集
2. **Home Assistant再起動**: 変更を反映させるためにHome Assistantを再起動
3. **ログ確認**: `home-assistant.log` でエラーやデバッグ情報を確認
4. **設定テスト**: Home AssistantのUIでインテグレーションの追加・設定をテスト

## Architecture

### Home Assistant Integration Structure

This project should follow the standard Home Assistant custom integration structure:

```
custom_components/
└── disasterinformation/
    ├── __init__.py              # Integration entry point
    ├── manifest.json            # Integration metadata (required)
    ├── config_flow.py          # Configuration UI flow
    ├── const.py                # Constants and configuration
    ├── sensor.py               # Sensor platform implementation
    └── strings.json            # UI strings for configuration
```

### Key Components

- **manifest.json**: Defines integration metadata, dependencies, and requirements
- **__init__.py**: Integration setup, unload, and coordinator initialization
- **config_flow.py**: Handles user configuration through HA UI
- **sensor.py**: Implements disaster information sensors (気象警報・地震情報)
- **binary_sensor.py**: Implements binary sensors for automation triggers
- **const.py**: Domain name, default values, and API constants
- **strings.json**: UI strings for configuration (Japanese localization)
- **coordinator.py**: Data coordinator for managing API calls and data updates
- **api.py**: JMA XML API client implementation

### Integration Pattern

Home Assistant integrations typically use:
- **Coordinator pattern** for data fetching and management
- **Config entries** for user configuration storage
- **Device registry** for organizing multiple sensors
- **State classes** for sensor data representation

## Development Setup

1. Create the `custom_components/disasterinformation/` directory structure
2. Implement required files starting with `manifest.json` and `__init__.py`
3. Test by copying to Home Assistant's `custom_components/` directory
4. Use Home Assistant's configuration UI to add the integration
5. Monitor Home Assistant logs for debugging: `tail -f home-assistant.log`

## JMA XML API Integration

気象庁防災情報XMLフォーマットの特記事項:
- **データソース**: https://xml.kishou.go.jp/xmlpull.html
- **フォーマット**: XML (JMAXML形式)
- **更新頻度**: 最小5分間隔（デフォルト10分）
- **認証**: 不要（公開API）
- **エラーハンドリング**: HTTPエラー、XML解析エラー、データ不整合への対応が必要
- **地域コード**: 都道府県・市区町村コードでの地域指定
- **情報種別**: 気象警報、地震情報、津波情報など

## Configuration

Home Assistant integrations use:
- **Config flow** for initial setup through UI
- **Options flow** for runtime configuration changes
- **Configuration.yaml** entries (optional, for simple setups)

## Testing

Home Assistant integration testing:
- Manual testing within HA development environment
- Unit tests for core logic (optional but recommended)
- Integration tests using HA test framework (advanced)

### Debug Tips

- Home Assistantログレベルを`debug`に設定してデバッグ情報を確認
- `_LOGGER.debug()` を使用してカスタムログを出力
- 設定フローのテストは段階的に（都道府県選択→市区町村選択→情報種別選択）
- API呼び出し失敗時の挙動を確認（ネットワークエラー、XMLパースエラーなど）

## Important Notes

- **DOMAIN**: `disasterinformation` (const.pyで定義)
- **日本語対応**: エンティティ名、設定UI、エラーメッセージはすべて日本語
- **地域コード管理**: 都道府県・市区町村のマッピングテーブルが必要
- **データ正規化**: JMA XMLの複雑な構造を Home Assistant エンティティに適切にマッピング