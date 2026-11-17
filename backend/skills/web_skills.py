import datetime
import urllib.parse
import urllib.request
import json
import webbrowser

def get_current_time_date() -> str:
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}, on {now.strftime('%A, %B %d, %Y')}."

def web_search(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url)
    return f"Searching the web for '{query}'."

def get_weather(city: str = "") -> str:
    """Fetch brief weather using free wttr.in endpoint or formatted query."""
    location = city.strip() if city else ""
    try:
        url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1" if location else "https://wttr.in?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            current = data['current_condition'][0]
            temp_c = current['temp_C']
            desc = current['weatherDesc'][0]['value']
            area = data['nearest_area'][0]['areaName'][0]['value']
            return f"In {area}, conditions are {desc} with a temperature of {temp_c}°C."
    except Exception:
        # Fallback to web search if offline or timeout
        if location:
            webbrowser.open(f"https://www.google.com/search?q=weather+in+{urllib.parse.quote_plus(location)}")
            return f"Checking current weather forecast for {location}."
        return "I am unable to retrieve live meteorological data at this moment."
