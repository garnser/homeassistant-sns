import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AWS SNS Notify from a config entry."""
    _LOGGER.debug("async_setup_entry called for AWS SNS Notify")  # Add this
    try:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = entry.data

        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "notify")
        )
        _LOGGER.debug("AWS SNS Notify forward entry setup initiated")
        return True
    except Exception as e:
        _LOGGER.error("Error during async_setup_entry in __init__.py: %s", e)  # Log any errors
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "notify")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
