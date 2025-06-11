import hashlib
import ipaddress
import logging
import time
from pathlib import Path
from typing import Any

import click

from fabrik7.config.loader import ConfigLoader
from fabrik7.config.models import DB, PLC, Field, FieldType
from fabrik7.servers import launch

logger = logging.getLogger(__name__)
FIELD_TYPE_SIZES = {
    'BOOL': 1,
    'BYTE': 1,
    'CHAR': 1,
    'WORD': 2,
    'DWORD': 4,
    'INT': 2,
    'DINT': 4,
    'REAL': 4,
    'LREAL': 8,
}


def _start(  # noqa: PLR0913
    count: int, host: str, port: int, db_size: int, db_number: int, field_number: int, field_type: FieldType, value: Any
) -> None:
    field_size = FIELD_TYPE_SIZES.get(field_type, 0)
    fields = [
        Field(name=f'Field:{i}', offset=field_size * i, type=field_type, value=value) for i in range(field_number)
    ]
    dbs = [DB(number=i + 1, size=db_size, fields=fields) for i in range(db_number)]

    base_ip_address = ipaddress.IPv4Address(host)
    plcs: list[PLC] = []
    for i in range(count):
        ip_address = str(base_ip_address + i)
        plc = PLC(name=f'PLC:{i}', host=ip_address, port=port, dbs=dbs)
        plcs.append(plc)

    launch(plcs)

    while True:
        time.sleep(1)


def _start_with_watch(config_path: Path) -> None:
    last_config_file_hash = None
    config = ConfigLoader.load(config_path)
    threads = launch(config.plcs)

    logger.info(f'Watching {config_path} for changes...')
    while True:
        current_config_file_hash = hashlib.sha256(Path(config_path).read_bytes()).hexdigest()

        if not current_config_file_hash == last_config_file_hash:
            logger.info('A change was detected. Updating PLCs...')
            last_config_file_hash = current_config_file_hash

            config = ConfigLoader.load(config_path)
            for plc in config.plcs:
                thread = threads.get(plc.name, None)

                if not thread:
                    continue

                thread.update(plc)

        time.sleep(1)


@click.group()
@click.option(
    '--log-level', '-l', type=click.Choice(['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']), help='Logging level.'
)
def cli(log_level: str) -> None:
    """Fabrik7 - Simple PLC Simulator"""
    log_level_value = getattr(logging, log_level or 'INFO')

    logging.basicConfig(
        level=log_level_value,
        format='[%(name)s] %(levelname)s %(message)s',
    )

    snap7_server_logger = logging.getLogger('snap7.server')
    snap7_server_logger.disabled = True


@cli.command()
@click.option('--count', '-c', default=1, help='Number of PLCs to simulate.')
@click.option('--host', '-h', default='127.0.0.1', help='Initial host to listen on.')
@click.option('--port', '-p', default=102, help='Initial port to listen on.')
@click.option('--db-size', '-s', default=1024, help='Size of the database in bytes.')
@click.option('--db-number', '-n', default=1, help='Number of databases by PLC.')
@click.option('--field-number', '-fn', default=1, help='Number of fields by DB.')
@click.option(
    '--field-type',
    '-t',
    default='BOOL',
    type=click.Choice(['BOOL', 'BYTE', 'CHAR', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 'LREAL']),
    help='Type of the field.',
)
@click.option('--value', '-v', default='0', help='Value of the field.')
@click.option('--config-file', '-f', default=None, help='Configuration file (yaml, yml and json).')
def start(  # noqa: PLR0913
    count: int,
    host: str,
    port: int,
    db_size: int,
    db_number: int,
    field_number: int,
    field_type: FieldType,
    value: Any,
    config_file: Path | None,
) -> None:
    if not config_file:
        _start(count, host, port, db_size, db_number, field_number, field_type, value)
        return

    _start_with_watch(config_file)


if __name__ == '__main__':
    cli()
