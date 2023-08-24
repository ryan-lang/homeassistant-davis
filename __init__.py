from datetime import timedelta
import logging
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import update_coordinator

DOMAIN = "davis_instruments"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

_LOGGER = logging.getLogger(__name__)

async def async_fetch_data(host):
    url = f"http://{host}/v1/current_conditions"
    async with aiohttp.ClientSession() as session:
        try:
            async with async_timeout.timeout(10):
                async with session.get(url) as response:
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.warning("Error fetching data: %s", err)
            raise update_coordinator.UpdateFailed("Error fetching data")

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    host = entry.data["host"]
    device_name = entry.title

    coordinator = update_coordinator.DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=f"{device_name} Data",
        update_method=lambda: async_fetch_data(host),
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Load any platforms that rely on the data from this entry.
    hass.config_entries.async_setup_platforms(entry, ["sensor"])

    return True 