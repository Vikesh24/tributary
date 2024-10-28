# import the flask web framework
from crypt import methods

from flask import Flask, request
import json
from redis import Redis
from loguru import logger


HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

# create a Flask server, and allow us to interact with it using the app variable
app = Flask(__name__)
database = Redis(host="redis", port=6379, db=0, decode_responses=True)

@app.route("/")
def hello():
    return "Hello World!"

# define an endpoint which accepts POST requests, and is reachable from the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")


    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200

@app.route('/record', methods=['GET'])
def get_engine_data():
    engine_temperatures = [float(temperature) for temperature in database.lrange(DATA_KEY, 0, -1)]
    logger.info(f"engine temperature list contains these values: {engine_temperatures}")

    logger.info(f"Getting current engine temperature value")
    current_engine_temperature = engine_temperatures[0]
    logger.info(f"Current engine temperature is {current_engine_temperature}")

    logger.info(f"Getting the averager temperature of the engine")
    average_engine_temperature = sum(engine_temperatures) / len(engine_temperatures)
    logger.info(f"Average temperature of the engine is {average_engine_temperature}")
    return {
        "success": True,
        "current engine temperature": current_engine_temperature,
        "average engine temperature": round(average_engine_temperature,2)
    }, 200