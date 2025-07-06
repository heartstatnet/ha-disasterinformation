# JMA Disaster Information - Home Assistant Integration

A Home Assistant custom integration that provides real-time disaster information for Japan, including weather warnings and earthquake data from the Japan Meteorological Agency (JMA) BOSAI API.

## Features

- **Weather Warnings & Advisories**: Real-time alerts for thunderstorms, heavy rain, strong winds, snow, and other weather-related warnings with city-level precision
- **Earthquake Information**: Live earthquake data with recent 10 earthquakes history, flexible filtering by time range, magnitude, and intensity
- **Multi-Region Support**: Monitor multiple areas (home, workplace, family locations)
- **Hierarchical Area Selection**: Choose from region → prefecture → municipality
- **Advanced Dashboard Cards**: Conditional cards, time-filtered earthquake displays, and comprehensive disaster information dashboards
- **Home Assistant Automation**: Trigger automations based on disaster alerts
- **HACS Compatible**: Easy installation through Home Assistant Community Store

## Quick Start

1. Install via HACS
2. Add Integration: **Settings** → **Devices & Services** → **Add Integration** → Search "JMA Disaster Information"
3. Select your area: Region → Prefecture → Municipality
4. Configure update interval (default: 10 minutes)

---

# 気象庁防災情報 Home Assistant統合

気象庁の公式BOSAI APIを使用して、リアルタイムの防災情報をHome Assistantで利用できるカスタム統合です。

## 主な機能

- **気象警報・注意報**: 雷、大雨、強風、大雪など各種気象警報・注意報をリアルタイム取得
- **地震情報**: 全国の地震情報を取得、直近10件の地震データを保持
- **市区町村レベル対応**: 正確な地域フィルタリングによる地域固有の警報情報
- **階層的地域選択**: 地方 → 都道府県 → 市区町村の3段階選択
- **柔軟な地震フィルタ**: 時間範囲、マグニチュード、震度による地震情報フィルタリング
- **豊富なダッシュボード**: 条件付き表示、時間フィルタなど高度なダッシュボードカード
- **HACS対応**: Home Assistant Community Store経由での簡単インストール

## インストール方法

### HACS経由（推奨）

1. Home AssistantのHACSを開く
2. 「統合」をクリック
3. 右上の「...」から「カスタムリポジトリ」を選択
4. リポジトリURL: `https://github.com/heartstatnet/ha-disasterinformation`
5. カテゴリ: 「Integration」を選択
6. 「追加」をクリック
7. 「JMA Disaster Information」を検索してダウンロード
8. Home Assistantを再起動

### 手動インストール

1. [リリースページ](https://github.com/heartstatnet/ha-disasterinformation/releases)から最新版をダウンロード
2. `custom_components/disasterinformation`フォルダをHome Assistantの`custom_components`ディレクトリにコピー
3. Home Assistantを再起動

## 設定方法

1. **設定** → **デバイスとサービス** → **統合を追加**
2. 「JMA Disaster Information」を検索
3. 設定手順に従って進む:
   - **地方選択**: 北海道地方、東北地方、関東甲信地方など
   - **都道府県選択**: 選択した地方内の都道府県
   - **市区町村選択**: 選択した都道府県内の市区町村
   - **更新間隔**: データ取得間隔を設定（最小5分、デフォルト10分）
4. 「送信」をクリックして設定完了

### 複数地域の追加

設定プロセスを繰り返すことで、複数の地域を追加できます。各地域は個別のデバイスとして作成され、独自のセンサーセットを持ちます。

## エンティティ

この統合では、2つのタイプのエンティティが提供されます：

### 1. 気象警報・注意報エンティティ（地域選択時）

設定した地域ごとに、`[都道府県名] [市区町村名] 気象庁防災情報`という名前のデバイスが作成されます。

#### 気象警報・注意報センサー (`sensor.[地域名中国語音写]_jing_bao_zhu_yi_bao`)
- **状態**: 発表中の警報・注意報の概要（例：「雷注意報」、「大雨警報」、「発表なし」）
- **主要属性**:
  - `warnings`: 警報のリスト（名前、重要度、地域コード、状態）
  - `advisories`: 注意報のリスト（名前、重要度、地域コード、状態）
  - `emergency_warnings`: 特別警報のリスト
  - `warning_count`: 発表中の警報・注意報数
  - `status`: 全体状態（「警報発表中」、「注意報発表中」、「発表なし」）
  - `last_update`: 最終更新時刻

**エンティティ名の例**:
- 北九州市: `sensor.fu_gang_xian_bei_jiu_zhou_shi_jing_bao_zhu_yi_bao`
- 那覇市: `sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao`
- 東京都千代田区: `sensor.dong_jing_du_qian_dai_tian_qu_jing_bao_zhu_yi_bao`

### 2. 地震情報エンティティ（全国対象）

#### 地震情報センサー (`sensor.di_zhen_qing_bao`)
- **状態**: フィルタ条件に該当する地震数（例：「3件の地震」、「該当する地震なし」）
- **主要属性**:
  - `recent_earthquakes`: **直近10件の地震情報**
    - `report_datetime`: 報告日時
    - `hypocenter`: 震源地
    - `magnitude`: マグニチュード
  - `latest_earthquake`: 最新地震の詳細情報
  - `earthquake_count`: フィルタ条件に該当する地震数
  - `time_range_hours`: 検索時間範囲（時間）
  - `min_magnitude`: 最小マグニチュード
  - `min_intensity`: 最小震度

## ダッシュボードカード

防災情報を効果的に表示するためのカード設定例：

### 1. 気象警報・注意報カード

設定した地域の気象警報・注意報を表示します。

```yaml
type: entity
entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
name: 気象警報・注意報
icon: mdi:weather-lightning
```

### 2. 警報時のみ表示する条件付きカード

警報や注意報が発表されている時のみ表示されます。

```yaml
type: conditional
conditions:
  - entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
    state_not: "発表なし"
card:
  type: entities
  title: ⚠️ 気象警報・注意報発表中
  entities:
    - entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
      name: 現在の状況
  show_header_toggle: false
```

### 3. 地震情報カード（基本）

全国の地震情報を表示します。

```yaml
type: entity
entity: sensor.di_zhen_qing_bao
name: 地震情報
icon: mdi:earth
```

### 4. 直近1時間の地震情報カード（詳細）

直近1時間以内に発生した地震のみを表示する高度なカードです。

```yaml
type: markdown
title: 🔍 直近1時間の地震情報
content: |
  {% set earthquakes = state_attr('sensor.di_zhen_qing_bao', 'recent_earthquakes') %}
  {% if earthquakes %}
    {% set ns = namespace(recent_eq=[]) %}
    {% for eq in earthquakes %}
      {% set report_time = strptime(eq.report_datetime, '%Y-%m-%dT%H:%M:%S%z') %}
      {% set current_time = now() %}
      {% set time_diff = (current_time - report_time).total_seconds() / 3600 %}
      {% if time_diff <= 1 %}
        {% set ns.recent_eq = ns.recent_eq + [eq] %}
      {% endif %}
    {% endfor %}
    
    {% if ns.recent_eq %}
      | 時刻 | 震源地 | マグニチュード |
      |------|--------|----------------|
      {% for eq in ns.recent_eq %}
      | {{ as_timestamp(strptime(eq.report_datetime, '%Y-%m-%dT%H:%M:%S%z')) | timestamp_custom('%m/%d %H:%M') }} | {{ eq.hypocenter }} | M{{ eq.magnitude }} |
      {% endfor %}
      
      **{{ ns.recent_eq | length }}件の地震が過去1時間以内に発生**
    {% else %}
      ✅ 直近1時間以内に地震は発生していません
    {% endif %}
  {% else %}
    ❌ 地震データを取得できませんでした
  {% endif %}
```

### 5. 総合防災ダッシュボード

気象警報と地震情報を統合した総合ダッシュボードです。

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
        name: 気象警報・注意報
        icon: mdi:weather-lightning
      - type: entity
        entity: sensor.di_zhen_qing_bao
        name: 地震情報
        icon: mdi:earth
  
  - type: conditional
    conditions:
      - entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
        state_not: "発表なし"
    card:
      type: entities
      title: ⚠️ 発表中の警報・注意報
      entities:
        - entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
          attribute: warnings
          name: 警報
        - entity: sensor.chong_sheng_xian_na_ba_shi_jing_bao_zhu_yi_bao
          attribute: advisories
          name: 注意報
      show_header_toggle: false
  
  - type: markdown
    title: 📊 最新10件の地震情報
    content: |
      {% set earthquakes = state_attr('sensor.di_zhen_qing_bao', 'recent_earthquakes') %}
      {% if earthquakes %}
        | 報告日時 | 震源地 | M |
        |----------|--------|---|
        {% for eq in earthquakes[:5] %}
        | {{ as_timestamp(strptime(eq.report_datetime, '%Y-%m-%dT%H:%M:%S%z')) | timestamp_custom('%m/%d %H:%M') }} | {{ eq.hypocenter }} | {{ eq.magnitude }} |
        {% endfor %}
        
        {% if earthquakes | length > 5 %}
        *他{{ earthquakes | length - 5 }}件の地震情報あり*
        {% endif %}
      {% else %}
        データなし
      {% endif %}
```

## データソース

この統合は[気象庁防災情報API（BOSAI API）](https://www.jma.go.jp/bosai/)をデータソースとして使用しています。

- **更新頻度**: 設定可能（最小5分、デフォルト10分）
- **認証**: 不要（公開API）
- **フォーマット**: JSON形式
- **対象範囲**: 日本全国の都道府県・市区町村

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## サポート

- **ドキュメント**: [GitHubリポジトリ](https://github.com/heartstatnet/ha-disasterinformation)
- **問題報告**: [バグ報告や機能要求](https://github.com/heartstatnet/ha-disasterinformation/issues)
- **ディスカッション**: [コミュニティディスカッション](https://github.com/heartstatnet/ha-disasterinformation/discussions)

## 免責事項

この統合は参考目的で防災情報を提供します。常に政府公式の発表や避難指示に従ってください。開発者は、この統合の使用により生じる可能性のある損害や損失について責任を負いません。

---

**JMA Disaster Information - Home Assistant Integration**  
日本の公式防災情報をスマートホームに。