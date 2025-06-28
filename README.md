# JMA Disaster Information

A Home Assistant custom integration that provides real-time disaster information for Japan, including weather warnings, earthquake data, and tsunami alerts from the Japan Meteorological Agency (JMA).

This integration is specifically designed for Japanese users and provides disaster information in Japanese. The integration uses official JMA XML data and supports all prefectures and municipalities in Japan.

---

# 気象庁防災情報 Home Assistant インテグレーション

日本の気象庁が提供する防災情報XMLフォーマットを使用して、リアルタイムで気象警報、地震情報、津波情報などをHome Assistantに取り込むカスタムインテグレーションです。

## 主な機能

- **気象警報・注意報・特別警報**: 大雨、強風、雪などの気象関連警報の取得
- **地震情報**: 震度、震源地、マグニチュードなどのリアルタイム地震データ
- **津波情報**: 津波警報・注意報・予報の取得
- **土砂災害警戒情報**: 土砂災害に関する警戒情報
- **天気予報**: 地域の天気予報データ
- **複数地域対応**: 自宅、職場、実家など複数地域の監視
- **Home Assistantオートメーション**: 防災情報に基づく自動化の実行
- **HACS対応**: Home Assistant Community Storeから簡単インストール

![Configuration UI](docs/images/ui.png)

*気象庁が提供する防災情報の統合が可能です！*

## インストール

### HACS（推奨）

1. Home AssistantでHACSを開く
2. 「Integrations」をクリック
3. 右上の三点メニューから「Custom repositories」を選択
4. このリポジトリを追加: `https://github.com/heartstatnet/ha-disasterinformation`
5. カテゴリで「Integration」を選択
6. 「Add」をクリック
7. 「気象庁防災情報」で検索
8. 「Download」をクリック
9. Home Assistantを再起動

### 手動インストール

1. [リリースページ](https://github.com/heartstatnet/ha-disasterinformation/releases)から最新版をダウンロード
2. `custom_components/disasterinformation` フォルダをHome Assistantの `custom_components` ディレクトリにコピー
3. Home Assistantを再起動

## 設定

### 設定手順

1. **設定** → **デバイスとサービス** → **統合を追加** に移動
2. 「JMA Disaster Information」で検索

<img src="docs/images/Screenshot_2025-06-26-17-24-39-671_io.homeassistant.companion.android.jpg" alt="Step 1: Integration Search" width="300">

3. 設定手順に従って設定:
   - **都道府県の選択**: ドロップダウンから都道府県を選択

<img src="docs/images/Screenshot_2025-06-26-17-24-42-816_io.homeassistant.companion.android.jpg" alt="Step 2: Prefecture Selection" width="300">

   - **市区町村の選択**: ドロップダウンから市区町村を選択

<img src="docs/images/Screenshot_2025-06-26-17-24-45-616_io.homeassistant.companion.android.jpg" alt="Step 3: Municipality Selection" width="300">

   - **更新間隔**: 更新チェックの間隔を設定（最小5分、デフォルト10分）

<img src="docs/images/Screenshot_2025-06-26-17-24-47-783_io.homeassistant.companion.android.jpg" alt="Step 4: Update Interval Configuration" width="300">

4. 「送信」をクリックして設定完了

## エンティティ

設定された地域ごとに `[市区町村名] 気象庁防災情報`（例：「北九州市 気象庁防災情報」）という名前のデバイスが作成され、以下のエンティティが提供されます：

### センサーエンティティ

#### 気象警報 (`sensor.[都道府県名]_[市区町村名]_qi_xiang_jing_bao`)
- **名前**: `[都道府県名] [市区町村名] 気象警報` (例: `福岡県 北九州市 気象警報`)
- **状態**: 発表中の警報・注意報の概要（例：「大雨警報 雷注意報」、「特別警報(大雨)」、「発表なし」）
- **属性**:
  - `prefecture`: 都道府県名
  - `city`: 市区町村名
  - `special_warnings`: 特別警報のリスト
  - `warnings`: 警報のリスト
  - `advisories`: 注意報のリスト
  - `warning_count`: 警報数
  - `has_special_warning`: 特別警報有無
  - `has_warning`: 警報有無
  - `has_advisory`: 注意報有無
  - `last_update`: 最終更新時刻
  - `status`: ステータス
  - `raw_warnings`: 詳細な警報情報

### バイナリセンサーエンティティ

オートメーションでの使用を容易にするため：

#### 特別警報 (`binary_sensor.[都道府県名]_[市区町村名]_te_bie_jing_bao`)
- **名前**: `[都道府県名] [市区町村名] 特別警報` (例: `福岡県 北九州市 特別警報`)
- **状態**: 特別警報発表時にON
- **属性**: `warning_types`, `warning_count`
- **アイコン**: `mdi:shield-check`

#### 警報 (`binary_sensor.[都道府県名]_[市区町村名]_jing_bao`)
- **名前**: `[都道府県名] [市区町村名] 警報` (例: `福岡県 北九州市 警報`)
- **状態**: 警報発表時にON
- **属性**: `warning_types`, `warning_count`
- **アイコン**: `mdi:weather-sunny`

#### 注意報 (`binary_sensor.[都道府県名]_[市区町村名]_zhu_yi_bao`)
- **名前**: `[都道府県名] [市区町村名] 注意報` (例: `福岡県 北九州市 注意報`)
- **状態**: 注意報発表時にON
- **属性**: `warning_types`, `warning_count`
- **アイコン**: `mdi:check-circle`

## ダッシュボードカード

防災情報を表示するための3つの基本カード設定：

### 1. 基本エンティティカード

```yaml
type: entity
entity: sensor.fu_gang_xian_bei_jiu_zhou_shi_qi_xiang_jing_bao
name: 気象警報・注意報
icon: mdi:weather-lightning
```

### 2. 警報時のみ表示されるカード

```yaml
type: conditional
conditions:
  - entity: binary_sensor.fu_gang_xian_bei_jiu_zhou_shi_jing_bao
    state: "on"
card:
  type: entity
  entity: sensor.fu_gang_xian_bei_jiu_zhou_shi_qi_xiang_jing_bao
  name: ⚠️ 気象警報発表中
  icon: mdi:alert
```

### 3. 詳細情報カード

```yaml
type: entities
title: 防災情報詳細
entities:
  - entity: sensor.fu_gang_xian_bei_jiu_zhou_shi_qi_xiang_jing_bao
    name: 気象警報・注意報
    icon: mdi:weather-lightning
  - entity: binary_sensor.fu_gang_xian_bei_jiu_zhou_shi_te_bie_jing_bao
    name: 特別警報
    icon: mdi:shield-check
  - entity: binary_sensor.fu_gang_xian_bei_jiu_zhou_shi_jing_bao
    name: 警報
    icon: mdi:weather-sunny
  - entity: binary_sensor.fu_gang_xian_bei_jiu_zhou_shi_zhu_yi_bao
    name: 注意報
    icon: mdi:check-circle
```

## データソース

このインテグレーションは[気象庁防災情報XMLフォーマット](https://xml.kishou.go.jp/xmlpull.html)をデータソースとして使用しています。

- **更新頻度**: 設定可能（最小5分、デフォルト10分）
- **認証**: 不要（公開API）
- **フォーマット**: JMA XMLフォーマット
- **対応範囲**: 日本全国の都道府県・市区町村


## サポート

- **ドキュメント**: [GitHubリポジトリ](https://github.com/heartstatnet/ha-disasterinformation)
- **問題報告**: [バグ報告・機能要望](https://github.com/heartstatnet/ha-disasterinformation/issues)
- **ディスカッション**: [コミュニティディスカッション](https://github.com/heartstatnet/ha-disasterinformation/discussions)

## 免責事項

このインテグレーションは参考目的で防災情報を提供します。必ず公式の政府発表および避難指示に従ってください。本インテグレーションの使用により生じた損害について開発者は責任を負いません。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

---

**気象庁防災情報 Home Assistant インテグレーション**  
日本の公式防災情報をスマートホームに！