from loguru import logger
from cfg.botConfig import BotConfig
import pymongo

config = BotConfig.load_config()
client = pymongo.MongoClient(
    "mongodb://"+config["mongdb"]["user"]+":" + config["mongdb"]["pwd"]+"@" +
    config["mongdb"]["host"]+":"+str(config["mongdb"]["port"])+"/bot")

db = client.bot
coll_msg = db.msg
coll_botmsg = db.botmsg
coll_repeatmsg = db.repeatmsg


def find_repeatmsg(uid, gid):  # 查询重复消息
    msg_json = {"uid": uid, "gid": gid}
    result = coll_repeatmsg.find_one(msg_json)
    if result != None:
        logger.info("查询到数据库：{}", result["_id"])
    else:
        logger.info("未查询到重复消息")
    return result["repeated"]


def add_repeatmsg(msg,  uid, gid):  # 添加重复消息
    coll_repeatmsg.delete_one({"uid": uid, "gid": gid})
    msg_json = {"uid": uid, "gid": gid, "msg": msg, "repeated": False}
    result = coll_repeatmsg.insert_one(msg_json)
    logger.info("重复消息加载到数据库：{}", result.inserted_id)


def mark_repeatmsg(msg, uid, gid):  # 标记为已复读
    msgjson = {"uid": uid, "gid": gid, "msg": msg}
    coll_repeatmsg.update_one(msgjson, {"$set": {"repeated": True}})
    logger.info("已复读：{} {}", uid, gid)


def add_botmsg(msg, msgid, uid, gid):
    msg_json = {"uid": uid, "msgid": msgid, "gid": gid, "msg": msg}
    result = coll_botmsg.insert_one(msg_json)
    logger.info("bot消息加载到数据库：{}", result.inserted_id)


def add_msg(msg):
    result = coll_msg.insert_one(msg)
    logger.info("加载到数据库：{}", result.inserted_id)


def find_msg_by_id(msgid):
    msg = {"message_id": msgid}
    result = coll_msg.find_one(msg)
    if result != None:
        logger.info("查询到数据库：{}", result["_id"])
    else:
        logger.info("未查询到数据库")
    return result


def find_botmsg_by_id(msgid):
    msg = {"msgid": msgid}
    result = coll_botmsg.find_one(msg)
    if result != None:
        logger.info("查询到数据库：{}", result["_id"])
    else:
        logger.info("未查询到发言")
    return result


if __name__ == '__main__':
    # add_msg(imsg)
    find_msg_by_id(-1726724172)
    # pass
