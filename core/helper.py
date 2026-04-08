import webbrowser

def say_hello(name):
    return f"hello {name}! welcome to AURA !"

def add_numbers(a, b):
    return a + b

def get_day_motivation(name):
    return f"you've got this {name}! Keep building Aura"

def get_greeting(hour):
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    elif hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

class SystemExecutive:
    """
    The Agency Protocol: Executes physical desktop/system-level tasks.
    """
    
    @staticmethod
    def open_browser(url: str) -> str:
        """Opens the MacBook browser to a given URL."""
        try:
            webbrowser.open(url)
            return f"Opened {url} in your browser."
        except Exception as e:
            return f"Failed to open browser: {e}"

    @staticmethod
    def open_live_news() -> str:
        # Defaults to BBC Live or anything neutral
        url = "https://www.bbc.com/news/live"
        return SystemExecutive.open_browser(url)

    @staticmethod
    def open_weather_map() -> str:
        # Typical weather satellite
        url = "https://zoom.earth/"
        return SystemExecutive.open_browser(url)