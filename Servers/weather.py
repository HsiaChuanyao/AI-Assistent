from fastmcp import FastMCP
import requests

mcp = FastMCP("weather")

@mcp.tool()
def get_location(location:str):
    """Get the location information, including latitude and longitude, in order to use it to get weather information

    Args:
        location: the city or location name.

    Return:
        return the location information to the user.
    """

    geocoed_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": 1,
        "language": "zh",
        "format": "json"
    }

    geo_response = requests.get(geocoed_url, params=params)
    geo_data = geo_response.json()
    geo_response.raise_for_status()

    if not geo_data["results"]:
        return "No location found, please check and try again!"

    city = geo_data["results"][0]["name"]
    country = geo_data["results"][0]["country"]
    latitude = geo_data["results"][0]["latitude"]
    longitude = geo_data["results"][0]["longitude"]

    geo_report = (
        f"""
        city: {city}
        country: {country}
        latitude: {latitude}
        longitude: {longitude}
        """.strip()
    )

    return geo_report

@mcp.tool()
def get_weather(location:str, days:int = 0):
    """Get the weather information based on the given information(city and days).

    Args:
        location: the name of the city or location.
        days: the number of days to get the forecast weather information (0=current, 1=tomorrow, 2=day after tomorrow, max=5)

    Returns:
        return the results based on the location and days.

    """

    try:
        if days < 0 or days > 5:
            return "Invalid number of days, please check and try again!"

        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": location,
            "count": 1,
            "language": "zh",
            "format": "json"
        }
        geo_response = requests.get(geocode_url, params=params)
        geo_data = geo_response.json()
        geo_response.raise_for_status()

        if not geo_data["results"]:
            return "No location found, please check and try again!"

        latitude = geo_data["results"][0]["latitude"]
        longitude = geo_data["results"][0]["longitude"]

        base_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m, relative_humidity_2m, apparent_temperature, wind_speed_10m",
            "daily": "temperature_2m_max, temperature_2m_min, sunrise, sunset, precipitation_sum, windspeed_10m_max, windgusts_10m_max, winddirection_10m_dominant",
            "timezone": "auto",
            "forecast_days": days+1
        }

        response = requests.get(base_url, params=params)
        data = response.json()
        status = response.status_code

        if status in [400, 401, 403, 404, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542]:
            return "Error: {}".format(status)


        if days == 0:
            report= {
                "Current weather": {
                    "Temperature": f"{data["current"]["temperature_2m"]}℃",
                    "Relative humidity": f"{data["current"]["relative_humidity_2m"]}%",
                    "Apparent temperature": f"{data["current"]["apparent_temperature"]}℃",
                    "Wind speed": f"{data["current"]["wind_speed_10m"]}m/s",
                    "weather code": data["current"]["weather_code"],
                }
            }

        elif days == 1:
            report = {
                "Tomorrow": {
                    "Temperature max": f"{data["daily"]["temperature_2m_max"][1]}℃",
                    "Temperature min": f"{data["daily"]["temperature_2m_min"][1]}℃",
                    "Sunrise": data["daily"]["sunrise"][1],
                    "Sunset": data["daily"]["sunset"][1],
                    "Precipitation": data["daily"]["precipitation_sum"][1],
                    "weather code": data["daily"]["weather_code"][1]
                }
            }
        else :
            report = {
                "Date": data["daily"]["time"][2],
                "Temperature max": f"{data["daily"]["temperature_2m_max"][2]}℃",
                "Temperature min": f"{data["daily"]["temperature_2m_min"][2]}℃",
                "Sunrise": data["daily"]["sunrise"][2],
                "Sunset": data["daily"]["sunset"][2],
                "Precipitation": data["daily"]["precipitation_sum"][2],
                "Wind speed": f"{data["daily"]["windspeed_10m_max"][2]}m/s",
                "Wind gusts": f"{data["daily"]["windgusts_10m_max"][2]}m/s",
                "Wind direction": data["daily"]["winddirection_10m_dominant"][2],
                "weather code": data["daily"]["weather_code"][days]
            }

    except requests.exceptions.Timeout as e:
        return "Error: {}".format(e)
    except requests.exceptions.ConnectionError as e:
        return "Error: {}".format(e)
    except Exception as e:
        return "Error: {}".format(e)

    return report


if __name__ == "__main__":
    mcp.run()



