""" Main loop that is run on the Raspberry Pi on the USV 🛳⚓️ """

from typing import List, Optional
from multiprocessing import Process
from serial import Serial
from src.driver.driver import init_driver_process
from src.events.events import run_event_loop
from src.database.database_listener import setup_database_handlers
from src.serial.serial_listener import setup_serial_handlers
from src.socketio.socketio_listener import setup_socketio_handlers
from src.data_classes.sensor.data_in import GpsCoord

serial: Optional[Serial] = None

route: List[GpsCoord] = []
paused_gps_coord: Optional[GpsCoord] = None
driver_process: Optional[Process] = None

with open(file="config.json", mode="r", encoding="utf-8") as file:
    pass


def run():
    """Used to start the loop in __main__"""
    setup_database_handlers()
    setup_serial_handlers()
    setup_socketio_handlers()

    driver_process = init_driver_process()
    driver_process.start()

    # Infinite event loop
    Process(target=run_event_loop).start()
