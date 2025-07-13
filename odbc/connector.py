"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

from connectors.core.connector import Connector, get_logger, ConnectorError
from .operations import operations, _check_health

logger = get_logger('odbc')


class Odbc(Connector):
    def execute(self, config, operation, params, **kwargs):
        action = operations.get(operation)
        logger.info('executing {0}'.format(action))
        return action(config, params)

    def check_health(self, config):
        try:
            logger.info('executing check health')
            return _check_health(config)
        except Exception as err:
            logger.exception(str(err))
            raise ConnectorError(str(err))
