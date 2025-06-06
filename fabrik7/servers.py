import ctypes
import logging
import time
from dataclasses import dataclass
from threading import Thread

import snap7


@dataclass
class PLCSpec:
    name: str
    port: int
    db_number: int = 1
    db_size: int = 1024


class PLCThread(Thread):
    def __init__(self, spec: PLCSpec, log: bool = True) -> None:
        super().__init__(daemon=True)
        self.spec = spec
        self.log = log
        self.__server = snap7.server.Server()
        self.__logger = logging.getLogger(self.spec.name)

        self.__db_buffer = (ctypes.c_uint8 * spec.db_size)()
        self.__server.register_area(snap7.type.SrvArea.DB, spec.db_number, self.__db_buffer)

    def run(self) -> None:
        self.__server.start(tcp_port=self.spec.port)

        try:
            while True:
                if ev := self.__server.pick_event():
                    self.__logger.info(f'{self.__server.event_text(ev)}')

                time.sleep(0.5)
        finally:
            self.__server.stop()
            self.__server.destroy()


def launch(specs: list[PLCSpec], log: bool = True) -> dict[int, PLCThread]:
    threads = {}

    for spec in specs:
        t = PLCThread(spec, log)
        t.start()
        threads[spec.port] = t

    return threads
