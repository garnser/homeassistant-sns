from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import logging
from .const import DOMAIN, CONF_AWS_ACCESS_KEY, CONF_AWS_SECRET_KEY, CONF_AWS_REGION, CONF_SNS_TOPIC_ARN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AWS_ACCESS_KEY): str,
        vol.Required(CONF_AWS_SECRET_KEY): str,
        vol.Required(CONF_AWS_REGION): str,
        vol.Required(CONF_SNS_TOPIC_ARN): str,
    }
)


class AwsSnsNotifyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AWS SNS Notify."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                # Offload blocking validation to a separate thread
                await self.hass.async_add_executor_job(self._validate_credentials, user_input)
                return self.async_create_entry(title="AWS SNS Notify", data=user_input)
            except ValueError as e:
                errors["base"] = "invalid_credentials"
                _LOGGER.error("Error validating AWS credentials: %s", e)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    def _validate_credentials(self, user_input: dict) -> None:
        """Validate AWS credentials by listing topics."""
        import boto3
        try:
            client = boto3.client(
                "sns",
                aws_access_key_id=user_input[CONF_AWS_ACCESS_KEY],
                aws_secret_access_key=user_input[CONF_AWS_SECRET_KEY],
                region_name=user_input[CONF_AWS_REGION],
            )
            client.list_topics()  # Test if credentials work
            _LOGGER.debug("AWS credentials validated successfully")
        except Exception as e:
            _LOGGER.error("Invalid AWS credentials: %s", e)
            raise ValueError("Invalid AWS credentials")
