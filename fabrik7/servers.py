import ctypes
import logging
import time
from threading import Thread

import snap7

from fabrik7.config.models import PLC


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
