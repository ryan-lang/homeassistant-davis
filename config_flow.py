import logging
import voluptuous as vol
from homeassistant import config_entries
from . import async_fetch_data, DOMAIN

_LOGGER = logging.getLogger(__name__)

class DavisInstrumentsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input["host"]
            try:
                data = await async_fetch_data(host)
                device_name = data["data"]["name"]
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(device_name)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=device_name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                }
            ),
            errors=errors,
        )