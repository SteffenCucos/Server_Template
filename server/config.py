
from dataclasses import dataclass
import json

from pserialize import deserialize


@dataclass
class Mongo:
    connection_string: str


@dataclass
class Network:
    host: str
    port: int


@dataclass
class Config:
    mongo: Mongo
    network: Network


__config: Config = None


def fromFile(configPath: str) -> Config:
    with open(configPath, "rb") as configFile:
        configJson = json.loads(configFile.read())
        return configJson


def get_config() -> Config:
    global __config
    if not __config:
        configJson = None
        for n in range(5):
            try:
                configJson = fromFile("../" * n + "config.json")
            except:
                continue

        if not configJson:
            raise Exception("Could not find config.json file")
        try:
            __config = deserialize(configJson, Config)
        except Exception as e:
            raise Exception("Config is invalid", e)

    return __config
