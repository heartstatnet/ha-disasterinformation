"""Constants for the 気象庁防災情報 integration."""

DOMAIN = "disasterinformation"

# JMA BOSAI API URLs
JMA_BOSAI_BASE_URL = "https://www.jma.go.jp/bosai"
JMA_BOSAI_AREA_URL = f"{JMA_BOSAI_BASE_URL}/common/const/area.json"
JMA_BOSAI_WARNING_URL = f"{JMA_BOSAI_BASE_URL}/warning/data/warning"
JMA_BOSAI_EARTHQUAKE_URL = f"{JMA_BOSAI_BASE_URL}/quake/data"

# Default configuration
DEFAULT_UPDATE_INTERVAL = 10  # minutes
MIN_UPDATE_INTERVAL = 5  # minutes

# Entity names
ENTITY_NAME_WARNING = "警報・注意報"
ENTITY_NAME_EARTHQUAKE = "地震情報"

# Configuration keys
CONF_INFORMATION_TYPE = "information_type"
CONF_REGION = "region"
CONF_PREFECTURE = "prefecture"
CONF_CITY = "city"
CONF_AREA_CODE = "area_code"
CONF_UPDATE_INTERVAL = "update_interval"

# Information types
INFO_TYPE_WEATHER_WARNING = "weather_warning"
INFO_TYPE_EARTHQUAKE = "earthquake"

# Information type options
INFORMATION_TYPES = {
    INFO_TYPE_WEATHER_WARNING: "気象警報・注意報（地域選択必要）",
    INFO_TYPE_EARTHQUAKE: "地震情報（全国対象）"
}

# Earthquake configuration
CONF_EARTHQUAKE_MIN_MAGNITUDE = "earthquake_min_magnitude"
CONF_EARTHQUAKE_MIN_INTENSITY = "earthquake_min_intensity"
CONF_EARTHQUAKE_TIME_RANGE = "earthquake_time_range"

# Earthquake filter options
EARTHQUAKE_TIME_RANGES = {
    "1": "過去1時間",
    "6": "過去6時間", 
    "24": "過去24時間",
    "168": "過去1週間"
}

EARTHQUAKE_MIN_MAGNITUDES = {
    "0": "すべて",
    "2.0": "M2.0以上",
    "3.0": "M3.0以上",
    "4.0": "M4.0以上",
    "5.0": "M5.0以上"
}

EARTHQUAKE_MIN_INTENSITIES = {
    "0": "すべて",
    "1": "震度1以上",
    "2": "震度2以上", 
    "3": "震度3以上",
    "4": "震度4以上",
    "5-": "震度5弱以上"
}

# Warning types and codes - JMA公式警報コード対応表に基づく正確なマッピング
WARNING_CODES = {
    "00": "解除",
    "02": "暴風雪警報",
    "03": "大雨警報",
    "04": "洪水警報",
    "05": "暴風警報",
    "06": "大雪警報",
    "07": "波浪警報",
    "08": "高潮警報",
    "09": "土砂災害警報",
    "10": "大雨注意報",
    "12": "大雪注意報",
    "13": "風雪注意報",
    "14": "雷注意報",
    "15": "強風注意報",
    "16": "波浪注意報",
    "17": "融雪注意報",
    "18": "洪水注意報",
    "19": "高潮注意報",
    "20": "濃霧注意報",
    "21": "乾燥注意報",
    "22": "なだれ注意報",
    "23": "低温注意報",
    "24": "霜注意報",
    "25": "着氷注意報",
    "26": "着雪注意報",
    "27": "その他の注意報",
    "29": "土砂災害注意報",
    "32": "暴風雪特別警報",
    "33": "大雨特別警報",
    "35": "暴風特別警報",
    "36": "大雪特別警報",
    "37": "波浪特別警報",
    "38": "高潮特別警報",
    "39": "土砂災害特別警報",
    "43": "大雨危険警報",
    "48": "高潮危険警報",
    "49": "土砂災害危険警報",
}

# Warning severity levels
WARNING_SEVERITY = {
    "特別警報": "emergency",
    "警報": "warning", 
    "注意報": "advisory",
}

# Earthquake intensity levels
EARTHQUAKE_INTENSITY = {
    "1": "震度1",
    "2": "震度2", 
    "3": "震度3",
    "4": "震度4",
    "5-": "震度5弱",
    "5+": "震度5強",
    "6-": "震度6弱",
    "6+": "震度6強",
    "7": "震度7",
}

# JMA BOSAI API centers (地方コード) - 実際のarea.jsonから取得
REGION_CODES = {
    "北海道地方": "010100",
    "東北地方": "010200", 
    "関東甲信地方": "010300",
    "東海地方": "010400",
    "北陸地方": "010500",
    "近畿地方": "010600",
    "中国地方（山口県を除く）": "010700",
    "四国地方": "010800",
    "九州北部地方（山口県を含む）": "010900",
    "九州南部・奄美地方": "011000",
    "沖縄地方": "011100",
}

# JMA BOSAI API offices (都道府県コード) - 警報・注意報データ取得用
PREFECTURE_CODES = {
    "北海道": "016000",
    "青森県": "020000",
    "岩手県": "030000",
    "宮城県": "040000",
    "秋田県": "050000",
    "山形県": "060000",
    "福島県": "070000",
    "茨城県": "080000",
    "栃木県": "090000",
    "群馬県": "100000",
    "埼玉県": "110000",
    "千葉県": "120000",
    "東京都": "130000",
    "神奈川県": "140000",
    "新潟県": "150000",
    "富山県": "160000",
    "石川県": "170000",
    "福井県": "180000",
    "山梨県": "190000",
    "長野県": "200000",
    "岐阜県": "210000",
    "静岡県": "220000",
    "愛知県": "230000",
    "三重県": "240000",
    "滋賀県": "250000",
    "京都府": "260000",
    "大阪府": "270000",
    "兵庫県": "280000",
    "奈良県": "290000",
    "和歌山県": "300000",
    "鳥取県": "310000",
    "島根県": "320000",
    "岡山県": "330000",
    "広島県": "340000",
    "山口県": "350000",
    "徳島県": "360000",
    "香川県": "370000",
    "愛媛県": "380000",
    "高知県": "390000",
    "福岡県": "400000",
    "佐賀県": "410000",
    "長崎県": "420000",
    "熊本県": "430000",
    "大分県": "440000",
    "宮崎県": "450000",
    "鹿児島県": "460000",
    "沖縄県": "471000",
}