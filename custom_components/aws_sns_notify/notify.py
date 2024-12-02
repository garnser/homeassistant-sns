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
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "aws_sns_notify"

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AWS SNS notification entity."""
    async_add_entities([AwsSnsNotificationEntity(entry.entry_id, entry.data)])


class AwsSnsNotificationEntity(NotifyEntity):
    """Implement the notification entity service for AWS SNS."""

    _attr_supported_features = NotifyEntityFeature.TITLE
    _attr_name = DOMAIN
    _attr_icon = "mdi:message-text"

    def __init__(self, unique_id: str, config: dict) -> None:
        """Initialize AWS SNS notify entity."""
        self._attr_unique_id = unique_id
        self._aws_access_key = config.get("aws_access_key")
        self._aws_secret_key = config.get("aws_secret_key")
        self._aws_region = config.get("aws_region")
        self._sns_topic_arn = config.get("sns_topic_arn")

        # Initialize SNS client
        import boto3

        self._client = boto3.client(
            "sns",
            aws_access_key_id=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            region_name=self._aws_region,
        )

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message via AWS SNS."""
        try:
            # Determine whether to send to a topic or individual phone number
            target = self._sns_topic_arn
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
            _LOGGER.error("Error sending message via AWS SNS: %s", error)
            raise HomeAssistantError(f"Error sending message: {error}") from error
