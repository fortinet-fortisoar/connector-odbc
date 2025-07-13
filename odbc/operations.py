"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

from connectors.core.connector import get_logger, ConnectorError
import json
import pyodbc

logger = get_logger('odbc')


def connect_to_db(config):
    try:
        conn = pyodbc.connect(f"DSN={config.get('dsn_name')};")
        conn.autocommit = config.get("auto_commit")
        return conn
    except pyodbc.InterfaceError as ie:
        raise ConnectorError(f"Failed to connect using DSN '{config.get('dsn_name')}': {ie}")
    except Exception as e:
        raise ConnectorError(f"Unexpected error while connecting to database: {e}")


def execute_query(config, params):
    try:
        with connect_to_db(config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(params.get('query'))
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except pyodbc.ProgrammingError as pe:
        raise ConnectorError(f"SQL syntax or execution error: {pe}")
    except pyodbc.DatabaseError as de:
        raise ConnectorError(f"Database error occurred: {de}")
    except Exception as e:
        raise ConnectorError(f"Unexpected error during query execution: {e}")


def _check_health(config):
    try:
        connect_to_db(config)
        return True
    except Exception as e:
        raise ConnectorError('{0}'.format(e))


operations = {
    'execute_query': execute_query
}
