import json
import jsonschema
import os

CONFIG_SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config.schema.json')

def loadConfig(configFilePath: str) -> {}:
    """Loads configuration"""
    config = {}
    with open(configFilePath) as configFile:
        config = json.load(configFile)

    configSchema = {}
    with open(CONFIG_SCHEMA_FILE_PATH, "r") as configSchemaFile:
        configSchema = json.load(configSchemaFile)

    jsonschema.validate(instance=config, schema=configSchema)

    return config

def configHasProperty(config, *args) -> bool:
    """Returns if property is in config dictionary"""
    configElement = config
    for arg in args:
        if arg not in configElement:
            return False
        configElement = configElement[arg]
    return True

def getConfigProperty(config, *args, default=None):
    """Returns property from config dictionary"""
    configElement = config
    for arg in args:
        if arg not in configElement:
            return default
        configElement = configElement[arg]
    return configElement