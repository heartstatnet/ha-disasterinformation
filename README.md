# JMA Disaster Information - Home Assistant Integration

A Home Assistant custom integration that provides real-time disaster information for Japan, including weather warnings and earthquake data from the Japan Meteorological Agency (JMA) BOSAI API.

## Features

- **Weather Warnings & Advisories**: Real-time alerts for thunderstorms, heavy rain, strong winds, snow, and other weather-related warnings
- **Earthquake Information**: Live earthquake data including intensity, epicenter, and magnitude
- **Multi-Region Support**: Monitor multiple areas (home, workplace, family locations)
- **Hierarchical Area Selection**: Choose from region → prefecture → municipality
- **Built-in Dashboard Cards**: Conditional cards that only show when alerts are active
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

- **気象警報・注意報**: 雷、大雨、強風、大雪などの気象警報・注意報をリアルタイム取得
- **地震情報**: 震源地、マグニチュード、震度分布などの最新地震情報
- **複数地域対応**: 自宅、勤務先、実家など複数地域の監視が可能
- **階層的地域選択**: 地方 → 都道府県 → 市区町村の3段階選択
- **自動化対応**: 警報・注意報をトリガーとしたHome Assistantオートメーション
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

設定した地域ごとに、`[市区町村名] 気象庁防災情報`という名前のデバイスが作成され、以下のエンティティが提供されます：

### センサーエンティティ

#### 気象警報・注意報 (`sensor.[地域名]_警報注意報`)
- **状態**: 発表中の警報・注意報の概要（例：「注意報発表中」、「警報発表中」、「発表なし」）
- **属性**:
  - `headline`: 気象庁発表ヘッドライン
  - `report_datetime`: 発表日時
  - `warnings`: 警報のリスト
  - `advisories`: 注意報のリスト
  - `emergency_warnings`: 特別警報のリスト

#### 地震情報 (`sensor.[地域名]_地震情報`)
- **状態**: 最新の地震情報（例：「最大震度3」、「地震情報なし」）
- **属性**:
  - `report_datetime`: 発表日時
  - `event_id`: 地震識別ID
  - `hypocenter`: 震源地
  - `magnitude`: マグニチュード
  - `depth`: 深さ
  - `intensity_areas`: 地域別震度情報

### バイナリセンサーエンティティ

オートメーションでの利用を容易にするため：

- **特別警報** (`binary_sensor.[地域名]_特別警報`): 特別警報発表中にON
- **警報** (`binary_sensor.[地域名]_警報`): 何らかの警報発表中にON
- **注意報** (`binary_sensor.[地域名]_注意報`): 何らかの注意報発表中にON

## ダッシュボードカード

防災情報を表示するための3つの基本カード設定：

### 1. 基本エンティティカード（推奨）

シンプルで確実に動作する基本カードです。

```yaml
type: entity
entity: sensor.tokyo_警報注意報
name: 気象警報・注意報
icon: mdi:alert
```

### 2. 警報時のみ表示カード

警報や注意報がある時のみ表示される条件付きカードです。

```yaml
type: conditional
conditions:
  - entity: binary_sensor.tokyo_注意報
    state: "on"
card:
  type: entity
  entity: sensor.tokyo_警報注意報
  name: ⚠️ 気象警報・注意報発表中
  icon: mdi:alert
```

### 3. 詳細情報カード

すべての防災情報を一覧表示する詳細カードです。

```yaml
type: entities
title: 防災情報詳細
entities:
  - entity: sensor.tokyo_警報注意報
    name: 気象警報・注意報
    icon: mdi:weather-cloudy-alert
  - entity: sensor.tokyo_地震情報
    name: 地震情報
    icon: mdi:earth
  - entity: binary_sensor.tokyo_特別警報
    name: 特別警報
    icon: mdi:alert-octagon
  - entity: binary_sensor.tokyo_警報
    name: 警報
    icon: mdi:alert
  - entity: binary_sensor.tokyo_注意報
    name: 注意報
    icon: mdi:alert-outline
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