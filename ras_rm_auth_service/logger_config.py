import logging
import os
import sys

import flask
from flask import g
from structlog import configure
from structlog.stdlib import add_log_level, filter_by_level
from structlog.processors import JSONRenderer, TimeStamper


def logger_initial_config(log_level=None):
    """Configures the logger"""
    service_name = 'ras-rm-auth-service'
    logger_date_format = os.getenv('LOGGING_DATE_FORMAT', "%Y-%m-%dT%H:%M%s")
    logger_format = "%(message)s"

    if not log_level:
        log_level = os.getenv('SMS_LOG_LEVEL', 'INFO')

    try:
        indent = int(os.getenv('JSON_INDENT_LOGGING'))
    except (TypeError, ValueError):
        indent = None

    def add_service(logger, method_name, event_dict):  # pylint: disable=unused-argument
        """
        Add the service name to the event dict.
        """
        event_dict['service'] = service_name
        return event_dict

    def add_severity_level(logger, method_name, event_dict): # pylint: disable=unused-argument
        """
        Add the log level to the event dict.
        """
        if method_name == "warn":
            # The stdlib has an alias
            method_name = "warning"

        event_dict["severity"] = method_name
        return event_dict


    logging.basicConfig(stream=sys.stdout, level=log_level, format=logger_format)
    configure(processors=[add_severity_level, add_log_level, filter_by_level, add_service,
                          TimeStamper(fmt=logger_date_format, utc=True, key="created_at"), JSONRenderer(indent=indent)])
    oauth_log = logging.getLogger("requests_oauthlib")
    oauth_log.addHandler(logging.NullHandler())
    oauth_log.propagate = False
