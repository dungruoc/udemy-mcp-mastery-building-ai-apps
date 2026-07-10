from fastmcp import FastMCP
from dotenv import load_dotenv

import httpx
import re
import logging
import queue
from logging.handlers import QueueHandler, QueueListener
import os

load_dotenv()

# 1. Setup the blocking target handler (e.g., writing to file or console)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# 2. Setup the non-blocking queue handler
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)

# 3. Configure the root logger to use ONLY the non-blocking queue handler
root_logger = logging.getLogger()
root_logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
root_logger.addHandler(queue_handler)

# 4. Start the listener in a background thread to process the queue items
listener = QueueListener(log_queue, console_handler, respect_handler_level=True)
listener.start()

# 5. Use ordinary logging syntax inside async code
logger = logging.getLogger(__name__)
mcp = FastMCP("Weather")


def format_location(location: str) -> str:
    return re.sub('\s+', '+', location.strip())

@mcp.tool
async def get_current_weather(location: str):
    """Get the current weather for a location
    Args:
        location: location (examples: Hanoi, New York, London)

    Return:
        Weather condition of the provided location
    """
    location = format_location(location)
    logger.info(f"Get weather for {location}")

    async with httpx.AsyncClient() as httpx_client:
        response = await httpx_client.get("https://wttr.in/{location}?format=j1")
        data = response.json()
        current = data['current_condition'][0]
        area = data['nearest_area'][0]['areaName'][0]['value']
        return f"Weather in {area}: {current}"


@mcp.tool
async def get_forecast_weather(location: str):
    """Get 3-day weather forecast for a location
    Args:
        location: location (examples: Hanoi, New York, London)

    Return:
        Weather forecast for the next 3 days at the location 
    """
    location = format_location(location)
    logger.info(f"Get weather forecast for {location}")

    async with httpx.AsyncClient() as httpx_client:
        response = await httpx_client.get("https://wttr.in/{location}?format=j1")
        data = response.json()
        logger.debug(data['weather'][:3])
        forecasted = "\n".join([
            f"{day['date']} | temperature: {day['mintempC']}-{day['maxtempC']} degrees celcius, average: {day['avgtempC']} degrees celcius"
            for day in data['weather'][:3]
        ])
        return f"3-day Forecast Weather:\n{forecasted}"


if __name__ == "__main__":
    mcp.run(
        transport='streamable-http',
        host=os.getenv('FASTMCP_HOST')
    )