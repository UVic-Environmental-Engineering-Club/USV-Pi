import asyncio
import json
from enum import Enum, auto

from pymongo import MongoClient
import socketio
from typing import Optional
from serial import Serial
from typing import List, Optional, Dict, Callable, Any, Tuple
from src.data_classes.sensor.data_in import GpsCoord
from src.events.event_type import EventType


SERIAL: Optional[Serial] = None
MONGO_CLIENT: Optional[MongoClient] = None

with open(file="config.json", mode="r", encoding="utf-8") as file:
    config = json.load(file)
    env = config["env"]

    try:
        SERIAL = Serial(config["port"], config["baudrate"], timeout=config["timeout"])
    except Exception as error:
        print("Could not open serial port.", error)
        SERIAL = None

    try:
        if env == "dev":
            MONGO_CLIENT = MongoClient(
                config["mongo_url_dev"].replace(
                    "<password>", config["mongo_dev_password"]
                )
            )
        else:
            MONGO_CLIENT = MongoClient(config["mongo_url_prod"])

    except Exception as error:
        print("Could not open database.", error)
        MONGO_CLIENT = None

DATA: Dict[str, List[GpsCoord]] = {"route": [], "shore": []}
SUBSCRIBERS: Dict[EventType, List[Callable[[Any], Any]]] = {}
EVENT_LIST: asyncio.Queue[Tuple[EventType, Any]] = asyncio.Queue()

SIO = socketio.AsyncClient()

USV_DB = MONGO_CLIENT.usv
GPS_DATA_COLLECTION = USV_DB.gps_data


class State(Enum):
    STOP = auto()
    DRIVE = auto()
    COLLISION_DETECTION = auto()
    SHORE_DETECTION = auto()
    EMERGENCY = auto()
    ADJUST_RUDDERS = auto()
    GO_TO_POINT = auto()
