from __future__ import annotations

import logging

from botocore.exceptions import BotoCoreError, ClientError
from homeassistant.components.notify import (
    ATTR_TITLE_DEFAULT,
    NotifyEntity,
    NotifyEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, CONF_AWS_ACCESS_KEY, CONF_AWS_SECRET_KEY, CONF_AWS_REGION, CONF_SNS_TOPIC_ARN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AWS SNS notification entity."""
    _LOGGER.debug("Starting async_setup_entry for AWS SNS Notify")
    try:
        async_add_entities([AwsSnsNotificationEntity(entry.entry_id, entry.data, hass)])
        _LOGGER.debug("AWS SNS Notify entity added successfully")
    except Exception as e:
        _LOGGER.error("Error in async_setup_entry: %s", e)


class AwsSnsNotificationEntity(NotifyEntity):
    """Implement the notification entity service for AWS SNS."""

    _attr_supported_features = NotifyEntityFeature.TITLE | NotifyEntityFeature.TARGET
    _attr_name = "AWS SNS Notify"
    _attr_icon = "mdi:message-text"

    def __init__(self, unique_id: str, config: dict, hass: HomeAssistant) -> None:
        """Initialize AWS SNS notify entity."""
        _LOGGER.debug("Initializing AWS SNS Notify entity with unique_id: %s", unique_id)
        self._attr_unique_id = unique_id
        self._config = config
        self._hass = hass

        import boto3

        try:
            self._client = boto3.client(
                "sns",
                aws_access_key_id=config[CONF_AWS_ACCESS_KEY],
                aws_secret_access_key=config[CONF_AWS_SECRET_KEY],
                region_name=config[CONF_AWS_REGION],
            )
            _LOGGER.debug("SNS client initialized successfully")
        except Exception as e:
            _LOGGER.error("Error initializing SNS client: %s", e)
            raise

    async def async_send_message(self, message: str, title: str | None = None, **kwargs) -> None:
        """Send a message via AWS SNS."""
        targets = kwargs.get("target")
        if not targets:
            _LOGGER.error("No target specified for AWS SNS notification")
            raise HomeAssistantError("No target specified for AWS SNS notification")

        if not isinstance(targets, list):
            targets = [targets]

        try:
            for target in targets:
                await self._hass.async_add_executor_job(self._send_message, target, message, title)
                _LOGGER.debug("Message sent to target: %s", target)
        except Exception as e:
            _LOGGER.error("Error sending message via AWS SNS: %s", e)
            raise HomeAssistantError(f"Error sending message: {e}") from e

    def _send_message(self, target: str, message: str, title: str | None = None) -> None:
        """Blocking method to send a message to a target."""
        try:
            if target.startswith("+"):
                self._client.publish(PhoneNumber=target, Message=message)
                _LOGGER.info("SMS sent to %s via AWS SNS", target)
            else:
                self._client.publish(
                    TopicArn=target,
                    Message=message,
                    Subject=title or ATTR_TITLE_DEFAULT,
                )
                _LOGGER.info("Notification sent to topic %s via AWS SNS", target)
        except (BotoCoreError, ClientError) as error:
            _LOGGER.error("Error sending message to %s via AWS SNS: %s", target, error)
            raise
