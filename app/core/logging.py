import logging
import os
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.logging import LoggingIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ENV = os.getenv("ENV", "development")

LOG_LEVEL = logging.DEBUG if ENV == "development" else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

if SENTRY_DSN:
    sentry_logging = LoggingIntegration(
        level=LOG_LEVEL, event_level=logging.ERROR
    )
    sentry_init(dsn=SENTRY_DSN, integrations=[sentry_logging], environment=ENV)
