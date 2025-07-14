"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

from connectors.core.connector import get_logger, ConnectorError
import pyodbc

logger = get_logger('odbc')


def connect_to_db(config):
    if config.get("connection_type") == "Using DSN":
        conn_str = f"DSN={config.get('dsn_name')};"
    else:
        conn_items = [
            ("Driver", config.get("driver")),
            ("Host", config.get("host")),
            ("Port", config.get("port")),
            ("UID", config.get("username")),
            ("PWD", config.get("token")),
            ("HTTPPath", config.get("http_path")),
            ("AuthMech", config.get("auth_mech")),
            ("SSL", config.get("ssl")),
            ("ThriftTransport", config.get("thrift_transport")),
            ("Database", config.get("database"))
        ]
        conn_str_parts = []
        for key, value in conn_items:
            if value is not None and value != "":
                if key == "Driver":
                    conn_str_parts.append(f"{key}={{{value}}}")
                else:
                    conn_str_parts.append(f"{key}={value}")
        conn_str = ";".join(conn_str_parts) + ";"
        if config.get("extra_options"):
            conn_str += config["extra_options"].strip().rstrip(";") + ";"
    try:
        logger.error("The connection String is -------> {}".format(conn_str))
        conn = pyodbc.connect(conn_str)
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
