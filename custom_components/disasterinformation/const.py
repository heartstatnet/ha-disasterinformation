"""Constants for the 気象庁防災情報 integration."""

DOMAIN = "disasterinformation"

# API URLs
JMA_EXTRA_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
JMA_REGULAR_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/regular.xml"

# Default configuration
DEFAULT_UPDATE_INTERVAL = 10  # minutes
MIN_UPDATE_INTERVAL = 5  # minutes

# Entity names
ENTITY_NAME_WARNING = "気象警報"
ENTITY_NAME_EARTHQUAKE = "地震情報"

# Configuration keys
CONF_PREFECTURE = "prefecture"
CONF_CITY = "city"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_INFORMATION_TYPES = "information_types"

# Information types
INFO_TYPE_WEATHER_WARNING = "weather_warning"
INFO_TYPE_EARTHQUAKE = "earthquake"
INFO_TYPE_TSUNAMI = "tsunami"

# Prefectures (都道府県)
PREFECTURES = {
    "福岡県": "40",
    "北海道": "01",
    "青森県": "02",
    "岩手県": "03",
    "宮城県": "04",
    "秋田県": "05",
    "山形県": "06",
    "福島県": "07",
    "茨城県": "08",
    "栃木県": "09",
    "群馬県": "10",
    "埼玉県": "11",
    "千葉県": "12",
    "東京都": "13",
    "神奈川県": "14",
    "新潟県": "15",
    "富山県": "16",
    "石川県": "17",
    "福井県": "18",
    "山梨県": "19",
    "長野県": "20",
    "岐阜県": "21",
    "静岡県": "22",
    "愛知県": "23",
    "三重県": "24",
    "滋賀県": "25",
    "京都府": "26",
    "大阪府": "27",
    "兵庫県": "28",
    "奈良県": "29",
    "和歌山県": "30",
    "鳥取県": "31",
    "島根県": "32",
    "岡山県": "33",
    "広島県": "34",
    "山口県": "35",
    "徳島県": "36",
    "香川県": "37",
    "愛媛県": "38",
    "高知県": "39",
    "佐賀県": "41",
    "長崎県": "42",
    "熊本県": "43",
    "大分県": "44",
    "宮崎県": "45",
    "鹿児島県": "46",
    "沖縄県": "47",
}