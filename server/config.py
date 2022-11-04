
from dataclasses import dataclass
import json

from pserialize import deserialize


@dataclass
class Config:
    mongo_connection_string: str
    host: str
    port: int


def fromFile(configPath: str) -> Config:
    with open(configPath, "rb") as configFile:
        configJson = json.loads(configFile.read())
        return deserialize(configJson, Config)


def get_config() -> Config:
    try:
        return fromFile("config.json")
    except:
        return fromFile("../config.json")
