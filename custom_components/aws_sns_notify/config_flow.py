from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.schema_config_entry_flow import SchemaFlowFormStep, SchemaOptionsFlowHandler
from .const import DOMAIN

CONF_AWS_ACCESS_KEY = "aws_access_key"
CONF_AWS_SECRET_KEY = "aws_secret_key"
CONF_AWS_REGION = "aws_region"
CONF_SNS_TOPIC_ARN = "sns_topic_arn"

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
        if user_input is not None:
            # Validate and save configuration
            return self.async_create_entry(title="AWS SNS Notify", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA
        )

    async def async_step_import(self, user_input: dict | None = None) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)
