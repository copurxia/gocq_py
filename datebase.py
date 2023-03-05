from loguru import logger
from cfg.botConfig import BotConfig
import pymongo

config = BotConfig.load_config()
client = pymongo.MongoClient(
    host=config["mongdb"]["host"], port=config["mongdb"]["port"])

db = client.bot
collection = db.msg


def add_msg(msg):
    result = collection.insert_one(msg)
    logger.info("加载到数据库：{}", result.inserted_id)


def find_msg_by_id(msgid):
    msg = {"message_id": msgid}
    result = collection.find_one(msg)
    if result != None:
        logger.info("查询到数据库：{}", result["_id"])
    else:
        logger.info("未查询到数据库")
    return result


if __name__ == '__main__':
    # add_msg(imsg)
    # find_msg_by_id(-1964103618)
    pass
