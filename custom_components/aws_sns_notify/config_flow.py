from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.schema_config_entry_flow import SchemaFlowFormStep, SchemaOptionsFlowHandler
from .const import DOMAIN, CONF_AWS_ACCESS_KEY, CONF_AWS_SECRET_KEY, CONF_AWS_REGION, CONF_SNS_TOPIC_ARN


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
                # Optional: Validate the credentials
                import boto3
                client = boto3.client(
                    "sns",
                    aws_access_key_id=user_input[CONF_AWS_ACCESS_KEY],
                    aws_secret_access_key=user_input[CONF_AWS_SECRET_KEY],
                    region_name=user_input[CONF_AWS_REGION],
                )
                client.list_topics()  # Test AWS credentials

                # If valid, save configuration
                return self.async_create_entry(title="AWS SNS Notify", data=user_input)
            except Exception as e:
                errors["base"] = "invalid_credentials"
                _LOGGER.error("Error validating AWS credentials: %s", e)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input: dict | None = None) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)
