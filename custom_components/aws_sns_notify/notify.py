import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from homeassistant.components.notify import (
    BaseNotificationService,
    PLATFORM_SCHEMA,
)
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

CONF_AWS_ACCESS_KEY = "aws_access_key"
CONF_AWS_SECRET_KEY = "aws_secret_key"
CONF_AWS_REGION = "aws_region"
CONF_SNS_TOPIC_ARN = "sns_topic_arn"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_AWS_ACCESS_KEY): cv.string,
        vol.Required(CONF_AWS_SECRET_KEY): cv.string,
        vol.Required(CONF_AWS_REGION): cv.string,
        vol.Required(CONF_SNS_TOPIC_ARN): cv.string,
    }
)

def get_service(hass, config, discovery_info=None):
    """Get the AWS SNS notification service."""
    return AwsSnsNotificationService(
        config[CONF_AWS_ACCESS_KEY],
        config[CONF_AWS_SECRET_KEY],
        config[CONF_AWS_REGION],
        config[CONF_SNS_TOPIC_ARN],
    )

class AwsSnsNotificationService(BaseNotificationService):
    """Implementation of a notification service for AWS SNS."""

    def __init__(self, aws_access_key, aws_secret_key, aws_region, sns_topic_arn):
        """Initialize the service."""
        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key
        self._aws_region = aws_region
        self._sns_topic_arn = sns_topic_arn
        self._client = boto3.client(
            "sns",
            aws_access_key_id=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            region_name=self._aws_region,
        )

    def send_message(self, message="", **kwargs):
        """Send a message via AWS SNS."""
        try:
            self._client.publish(
                TopicArn=self._sns_topic_arn,
                Message=message,
                Subject=kwargs.get("title", "Home Assistant Notification"),
            )
            _LOGGER.info("Notification sent via AWS SNS to topic %s", self._sns_topic_arn)
        except (BotoCoreError, ClientError) as error:
            _LOGGER.error("Error sending message via AWS SNS: %s", error)
