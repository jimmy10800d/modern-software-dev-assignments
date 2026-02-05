#!/usr/bin/env python3
"""
Week 3 - Weather MCP Server（天氣 MCP 伺服器）

這是一個使用 Open-Meteo API 的 MCP Server，提供天氣查詢功能。
Open-Meteo 是免費的天氣 API，不需要 API Key。

提供的工具：
1. get_current_weather - 取得目前天氣
2. get_weather_forecast - 取得未來天氣預報

執行方式：
    python -m week3.server.main
    
或使用 MCP Inspector 測試：
    npx @modelcontextprotocol/inspector python -m week3.server.main
"""

import asyncio
import json
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    INTERNAL_ERROR,
    INVALID_PARAMS,
)

# ============================================================================
# 設定日誌（MCP STDIO 模式不能用 print，要用 logging 寫到 stderr）
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # 輸出到 stderr
)
logger = logging.getLogger("weather-mcp-server")

# ============================================================================
# Open-Meteo API 設定
# ============================================================================
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# HTTP 客戶端設定
HTTP_TIMEOUT = 30.0  # 秒
MAX_RETRIES = 3

# ============================================================================
# 建立 MCP Server
# ============================================================================
server = Server("weather-mcp-server")


# ============================================================================
# 輔助函式：地理編碼（城市名稱 → 經緯度）
# ============================================================================
async def geocode_city(city: str) -> dict[str, Any] | None:
    """
    將城市名稱轉換為經緯度座標。
    
    Args:
        city: 城市名稱（如 "Tokyo", "New York", "台北"）
        
    Returns:
        包含 latitude, longitude, name, country 的字典，或 None
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            response = await client.get(
                GEOCODING_URL,
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if "results" not in data or len(data["results"]) == 0:
                logger.warning(f"找不到城市: {city}")
                return None
                
            result = data["results"][0]
            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result.get("name", city),
                "country": result.get("country", "Unknown"),
                "timezone": result.get("timezone", "UTC"),
            }
            
        except httpx.TimeoutException:
            logger.error(f"地理編碼超時: {city}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"地理編碼 HTTP 錯誤: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"地理編碼錯誤: {e}")
            return None


# ============================================================================
# 輔助函式：取得天氣資料
# ============================================================================
async def fetch_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 1,
) -> dict[str, Any] | None:
    """
    從 Open-Meteo API 取得天氣資料。
    
    Args:
        latitude: 緯度
        longitude: 經度
        forecast_days: 預報天數（1-16）
        
    Returns:
        天氣資料字典，或 None
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{OPEN_METEO_BASE_URL}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                    "timezone": "auto",
                    "forecast_days": min(forecast_days, 16),  # API 最多 16 天
                }
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException:
            logger.error("天氣 API 超時")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"天氣 API HTTP 錯誤: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"天氣 API 錯誤: {e}")
            return None


# ============================================================================
# 輔助函式：天氣代碼轉描述
# ============================================================================
def weather_code_to_description(code: int) -> str:
    """將 WMO 天氣代碼轉換為可讀描述"""
    weather_codes = {
        0: "晴朗 ☀️",
        1: "大致晴朗 🌤️",
        2: "局部多雲 ⛅",
        3: "多雲 ☁️",
        45: "霧 🌫️",
        48: "霧凇 🌫️",
        51: "毛毛雨（輕） 🌧️",
        53: "毛毛雨（中） 🌧️",
        55: "毛毛雨（重） 🌧️",
        61: "小雨 🌧️",
        63: "中雨 🌧️",
        65: "大雨 🌧️",
        71: "小雪 🌨️",
        73: "中雪 🌨️",
        75: "大雪 🌨️",
        77: "雪粒 🌨️",
        80: "陣雨（輕） 🌦️",
        81: "陣雨（中） 🌦️",
        82: "陣雨（重） 🌦️",
        85: "小雪陣雨 🌨️",
        86: "大雪陣雨 🌨️",
        95: "雷暴 ⛈️",
        96: "雷暴伴小冰雹 ⛈️",
        99: "雷暴伴大冰雹 ⛈️",
    }
    return weather_codes.get(code, f"未知天氣 (代碼: {code})")


# ============================================================================
# MCP 工具定義
# ============================================================================
@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 MCP 工具"""
    return [
        Tool(
            name="get_current_weather",
            description="取得指定城市的目前天氣狀況，包含溫度、濕度、風速等資訊。",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名稱（如 'Tokyo', 'New York', 'Taipei', '台北'）",
                    },
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="get_weather_forecast",
            description="取得指定城市的未來天氣預報（最多 7 天），包含每日高低溫、降雨機率等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名稱（如 'Tokyo', 'New York', 'Taipei'）",
                    },
                    "days": {
                        "type": "integer",
                        "description": "預報天數（1-7，預設 3）",
                        "minimum": 1,
                        "maximum": 7,
                        "default": 3,
                    },
                },
                "required": ["city"],
            },
        ),
    ]


# ============================================================================
# MCP 工具實作
# ============================================================================
@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """處理工具呼叫"""
    
    logger.info(f"收到工具呼叫: {name}, 參數: {arguments}")
    
    try:
        if name == "get_current_weather":
            return await handle_get_current_weather(arguments)
        elif name == "get_weather_forecast":
            return await handle_get_weather_forecast(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"錯誤：未知的工具 '{name}'"
            )]
    except Exception as e:
        logger.exception(f"工具執行錯誤: {e}")
        return [TextContent(
            type="text",
            text=f"錯誤：執行工具時發生問題 - {str(e)}"
        )]


async def handle_get_current_weather(arguments: dict[str, Any]) -> list[TextContent]:
    """處理 get_current_weather 工具"""
    
    # 驗證參數
    city = arguments.get("city", "").strip()
    if not city:
        return [TextContent(
            type="text",
            text="錯誤：請提供城市名稱（city 參數）"
        )]
    
    # 地理編碼
    location = await geocode_city(city)
    if not location:
        return [TextContent(
            type="text",
            text=f"錯誤：找不到城市 '{city}'，請確認城市名稱是否正確"
        )]
    
    # 取得天氣
    weather = await fetch_weather(location["latitude"], location["longitude"])
    if not weather:
        return [TextContent(
            type="text",
            text=f"錯誤：無法取得 {city} 的天氣資料，請稍後再試"
        )]
    
    # 解析目前天氣
    current = weather.get("current", {})
    
    result = {
        "城市": f"{location['name']}, {location['country']}",
        "座標": f"({location['latitude']}, {location['longitude']})",
        "時區": weather.get("timezone", "Unknown"),
        "目前天氣": {
            "溫度": f"{current.get('temperature_2m', 'N/A')}°C",
            "體感描述": weather_code_to_description(current.get("weather_code", -1)),
            "相對濕度": f"{current.get('relative_humidity_2m', 'N/A')}%",
            "風速": f"{current.get('wind_speed_10m', 'N/A')} km/h",
            "風向": f"{current.get('wind_direction_10m', 'N/A')}°",
        },
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def handle_get_weather_forecast(arguments: dict[str, Any]) -> list[TextContent]:
    """處理 get_weather_forecast 工具"""
    
    # 驗證參數
    city = arguments.get("city", "").strip()
    if not city:
        return [TextContent(
            type="text",
            text="錯誤：請提供城市名稱（city 參數）"
        )]
    
    days = arguments.get("days", 3)
    if not isinstance(days, int) or days < 1 or days > 7:
        days = 3  # 預設 3 天
    
    # 地理編碼
    location = await geocode_city(city)
    if not location:
        return [TextContent(
            type="text",
            text=f"錯誤：找不到城市 '{city}'，請確認城市名稱是否正確"
        )]
    
    # 取得天氣預報
    weather = await fetch_weather(location["latitude"], location["longitude"], forecast_days=days)
    if not weather:
        return [TextContent(
            type="text",
            text=f"錯誤：無法取得 {city} 的天氣預報，請稍後再試"
        )]
    
    # 解析每日預報
    daily = weather.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    weather_codes = daily.get("weather_code", [])
    precipitations = daily.get("precipitation_sum", [])
    wind_speeds = daily.get("wind_speed_10m_max", [])
    
    forecast_list = []
    for i in range(min(days, len(dates))):
        forecast_list.append({
            "日期": dates[i] if i < len(dates) else "N/A",
            "天氣": weather_code_to_description(weather_codes[i]) if i < len(weather_codes) else "N/A",
            "最高溫": f"{max_temps[i]}°C" if i < len(max_temps) else "N/A",
            "最低溫": f"{min_temps[i]}°C" if i < len(min_temps) else "N/A",
            "降雨量": f"{precipitations[i]} mm" if i < len(precipitations) else "N/A",
            "最大風速": f"{wind_speeds[i]} km/h" if i < len(wind_speeds) else "N/A",
        })
    
    result = {
        "城市": f"{location['name']}, {location['country']}",
        "預報天數": days,
        "每日預報": forecast_list,
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


# ============================================================================
# 主程式入口
# ============================================================================
async def main():
    """啟動 MCP Server（STDIO 模式）"""
    logger.info("啟動 Weather MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
