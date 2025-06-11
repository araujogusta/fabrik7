import ctypes
import logging
import time
from threading import Thread

import snap7
from snap7.util import set_bool, set_byte, set_dint, set_dword, set_int, set_real, set_word

from fabrik7.config.models import DB, PLC, Field

WRITE_FUNCTIONS = {
    'BOOL': lambda buf, offset, val: set_bool(buf, offset, 0, bool(val)),
    'BYTE': lambda buf, offset, val: set_byte(buf, offset, int(val)),
    'WORD': lambda buf, offset, val: set_word(buf, offset, int(val)),
    'DWORD': lambda buf, offset, val: set_dword(buf, offset, int(val)),
    'INT': lambda buf, offset, val: set_int(buf, offset, int(val)),
    'DINT': lambda buf, offset, val: set_dint(buf, offset, int(val)),
    'REAL': lambda buf, offset, val: set_real(buf, offset, float(val)),
}


class PLCThread(Thread):
    def __init__(self, plc: PLC) -> None:
        super().__init__(daemon=True)
        self.plc = plc
        self._server = snap7.server.Server()
        self._logger = logging.getLogger(self.plc.name)
        self._db_buffers: dict[int, ctypes.Array] = {}

        self._register_db_areas()
        self._initialize_db_values()

    def _register_db_areas(self) -> None:
        """Registers the DB areas with the Snap7 server."""
        for db in self.plc.dbs:
            buffer = (ctypes.c_uint8 * db.size)()
            self._server.register_area(snap7.type.SrvArea.DB, db.number, buffer)
            self._db_buffers[db.number] = buffer

    def _initialize_db_values(self) -> None:
        """Initializes the DB values based on the PLC configuration."""
        for db in self.plc.dbs:
            buffer = self._db_buffers[db.number]

            for field in db.fields:
                if field.value is None:
                    continue

                self._write_field_value(buffer, field)

    def _write_field_value(self, buffer: ctypes.Array, field: Field) -> None:
        """Writes a single field value to the buffer."""
        snap7_buffer = bytearray(buffer)

        writer = WRITE_FUNCTIONS.get(field.type)

        if not writer:
            raise ValueError(f'Unsupported type: {field.type}')

        writer(snap7_buffer, field.offset, field.value)
        src_ptr = (ctypes.c_char * len(snap7_buffer)).from_buffer(snap7_buffer)
        dest_ptr = ctypes.addressof(buffer)

        ctypes.memmove(dest_ptr, src_ptr, len(snap7_buffer))

    def run(self) -> None:
        self._server.start_to(self.plc.host, self.plc.port)

        try:
            while True:
                if ev := self._server.pick_event():
                    self._logger.info(f'{self._server.event_text(ev)}')

                time.sleep(0.5)
        finally:
            self._server.stop()
            self._server.destroy()

    def update(self, plc: PLC) -> None:
        """Updates the PLC data and server with new values."""
        if plc.name != self.plc.name:
            self._logger.warning(f'Update called with PLC config for a different PLC: {plc.name} != {self.plc.name}')
            return

        for db in plc.dbs:
            existing_db = next((d for d in self.plc.dbs if d.number == db.number), None)
            if not existing_db:
                self._logger.warning(f'DB {db.number} not found in existing PLC config. Skipping update for this DB.')
                continue

            buffer = self._db_buffers.get(db.number)
            if not buffer:
                self._logger.error(f'No buffer found for DB number {db.number}')
                continue

            self._update_db(buffer, db)

    def _update_db(self, buffer: ctypes.Array, db: DB) -> None:
        """Updates a single DB with new values."""

        for field in db.fields:
            if field.value is None:
                continue
            self._write_field_value(buffer, field)


def launch(specs: list[PLC]) -> dict[str, PLCThread]:
    threads = {}

    for spec in specs:
        t = PLCThread(spec)
        t.start()
        threads[spec.name] = t

    return threads
