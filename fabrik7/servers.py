import ctypes
import logging
import time
from threading import Thread

import snap7
from snap7.util import set_bool, set_byte, set_dint, set_dword, set_int, set_real, set_word

from fabrik7.config.models import PLC

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
        self.__server = snap7.server.Server()
        self.__logger = logging.getLogger(self.plc.name)
        self.__db_buffers: dict[int, ctypes.Array] = {}

        for db in plc.dbs:
            buffer = (ctypes.c_uint8 * db.size)()
            self.__server.register_area(snap7.type.SrvArea.DB, db.number, buffer)
            self.__db_buffers[db.number] = buffer

            for field in db.fields:
                if field.value is None:
                    continue

                snap7_buffer = bytearray(buffer)

                writer = WRITE_FUNCTIONS.get(field.dtype)

                if not writer:
                    raise ValueError(f'Unsupported type: {field.dtype}')

                writer(snap7_buffer, field.offset, field.value)
                src_ptr = (ctypes.c_char * len(snap7_buffer)).from_buffer(snap7_buffer)
                dest_ptr = ctypes.addressof(buffer)

                ctypes.memmove(dest_ptr, src_ptr, len(snap7_buffer))

    def run(self) -> None:
        self.__server.start(tcp_port=self.plc.port)

        try:
            while True:
                if ev := self.__server.pick_event():
                    self.__logger.info(f'{self.__server.event_text(ev)}')

                time.sleep(0.5)
        finally:
            self.__server.stop()
            self.__server.destroy()


def launch(specs: list[PLC]) -> dict[int, PLCThread]:
    threads = {}

    for spec in specs:
        t = PLCThread(spec)
        t.start()
        threads[spec.port] = t

    return threads
