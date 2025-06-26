# 気象庁防災情報 (JMA Disaster Information)

日本の気象庁が提供する防災情報をHome Assistantで利用できるカスタムインテグレーションです。

## 主な機能

- **気象警報・注意報**: 大雨、強風、雪などの警報・注意報・特別警報
- **地震情報**: リアルタイムの地震情報（震度、震源地、マグニチュード）
- **津波情報**: 津波警報・注意報・予報
- **土砂災害警戒情報**: 土砂災害に関する警戒情報
- **天気予報**: 地域の天気予報データ
- **複数地域対応**: 自宅、職場、実家など複数地域の監視が可能

## 設定方法

1. Home Assistantの **設定** → **デバイスとサービス** → **統合を追加**
2. 「気象庁防災情報」を検索して選択
3. 都道府県と市区町村を選択
4. 取得したい情報の種類を選択
5. 更新間隔を設定（デフォルト: 10分）

## 提供されるエンティティ

### センサー
- `sensor.[地域]_warnings`: 気象警報・注意報の状態
- `sensor.[地域]_earthquake`: 地震情報

### バイナリセンサー（オートメーション用）
- `binary_sensor.[地域]_special_warning`: 特別警報発表時にON
- `binary_sensor.[地域]_warning`: 警報発表時にON
- `binary_sensor.[地域]_advisory`: 注意報発表時にON
- `binary_sensor.[地域]_earthquake_detected`: 地震検知時にON

## 専用カード

注意報・警報がある時のみ表示される専用カードが付属しています。

```yaml
type: custom:disaster-info-card
entity: sensor.your_area_warnings
```

## オートメーション例

```yaml
# 特別警報時の照明制御
automation:
  - alias: "特別警報時の警告灯"
    trigger:
      - platform: state
        entity_id: binary_sensor.tokyo_special_warning
        to: 'on'
    action:
      - service: light.turn_on
        target:
          entity_id: light.warning_light
        data:
          effect: strobe
```

## データソース

気象庁防災情報XMLフォーマット（https://xml.kishou.go.jp/xmlpull.html）を使用しています。

## 注意事項

この統合は参考情報として防災情報を提供します。公式の政府発表や避難指示に従ってください。