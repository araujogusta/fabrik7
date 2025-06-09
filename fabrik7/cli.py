import logging
import time
from pathlib import Path
from typing import Any

import click

from fabrik7.config.loader import ConfigLoader
from fabrik7.config.models import DB, PLC, Field, _DType
from fabrik7.servers import launch

logger = logging.getLogger(__name__)


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
@click.option('--port', '-p', default=2000, help='Initial port to listen on.')
@click.option('--db-size', '-s', default=1024, help='Size of the database in bytes.')
@click.option('--db-number', '-n', default=1, help='Number of databases by PLC.')
@click.option(
    '--dtype',
    '-t',
    default='BOOL',
    type=click.Choice(['BOOL', 'BYTE', 'CHAR', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 'LREAL']),
    help='Type of the field.',
)
@click.option('--value', '-v', default='0', help='Value of the field.')
@click.option('--config-file', '-f', default=None, help='Configuration file (yaml, yml and json).')
def start(  # noqa: PLR0913
    count: int, port: int, db_size: int, db_number: int, dtype: _DType, value: Any, config_file: Path | None
) -> None:
    if config_file:
        config = ConfigLoader.load(config_file)
        plcs = config.plcs
    else:
        fields = [Field(name=f'Field{i}', offset=i * db_size, dtype=dtype, value=value) for i in range(db_number)]
        plcs = [
            PLC(name=f'PLC{i}', port=port + i, dbs=[DB(number=i + 1, size=db_size, fields=fields)])
            for i in range(count)
        ]

    started_servers = launch(plcs)
    logger.info(f'Started {len(started_servers)} servers.')

    while True:
        time.sleep(1)


if __name__ == '__main__':
    cli()
