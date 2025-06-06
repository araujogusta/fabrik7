import logging
import time

import click

from fabrik7.servers import PLCSpec, launch

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
def start(count: int, port: int, db_size: int, db_number: int) -> None:
    specs = [PLCSpec(name=f'PLC{i + 1}', port=port + i, db_size=db_size, db_number=db_number) for i in range(count)]
    launch(specs)

    logger.info(f'{count} PLCs running on ports {port} - {port + count - 1}')
    logger.info('Press Ctrl+C to exit')

    while True:
        time.sleep(1)


if __name__ == '__main__':
    cli()
