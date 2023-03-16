from loguru import logger
from cfg.botConfig import BotConfig
from bson.objectid import ObjectId
import pymongo

config = BotConfig.load_config()
client = pymongo.MongoClient(
    "mongodb://"+config["mongdb"]["user"]+":" + config["mongdb"]["pwd"]+"@" +
    config["mongdb"]["host"]+":"+str(config["mongdb"]["port"])+"/bot")

db = client.bot
coll_msg = db.msg  # 消息列表
coll_botmsg = db.botmsg  # bot发言列表
coll_repeatmsg = db.repeatmsg  # 重复消息列表
coll_offline_file = db.offline_file  # 离线文件列表
coll_task = db.task  # 任务列表


def find_repeatmsg(gid):  # 查询重复消息
    msg_json = {"gid": gid}
    result = coll_repeatmsg.find_one(msg_json)
    if result == None:
        logger.info("未查询到重复消息")
    return result


def add_repeatmsg(msg, gid):  # 添加重复消息
    coll_repeatmsg.delete_one({"gid": gid})
    msg_json = {"gid": gid, "msg": msg, "repeated": False}
    coll_repeatmsg.insert_one(msg_json)


def mark_repeatmsg(msg,  gid):  # 标记为已复读
    msgjson = {"gid": gid, "msg": msg}
    coll_repeatmsg.update_one(msgjson, {"$set": {"repeated": True}})
    logger.info("已复读：{}", gid)


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


def add_offline_file(uid, time, name, size, url):
    result = coll_offline_file.insert_one(
        {"uid": uid, "time": time, "name": name, "size": size, "url": url})
    logger.info("加载离线文件到数据库：{}", result.inserted_id)


def find_offline_file(uid, name):
    result = coll_offline_file.find_one({"uid": int(uid), "name": name})
    if result != None:
        logger.info("查询到离线文件：{}", result["_id"])
        return True
    else:
        logger.info("未查询到离线文件")
        return False


def find_latest_file(uid):
    results = coll_offline_file.find(
        {"uid": int(uid)}).sort('_id', -1).limit(1)
    result = next(results)
    if result != None:
        logger.info("查询到离线文件：{}", result["_id"])
        return result
    else:
        logger.info("未查询到离线文件")
        return None


def offer_offline_file(uid, name):
    result = coll_offline_file.find_one({"uid": uid, "name": name})
    if result != None:
        result["_id"] = str(result["_id"])
        logger.info("查询到离线文件：{}", result["_id"])
        return result
    else:
        logger.info("未查询到离线文件")
        return None


def add_task(model, infile, subtype, uid, gid, taskargs):
    result = coll_task.insert_one(
        {"model": model, "status": None, "process": "", "infile": infile,
         "subftype": subtype, "uid": uid, "gid": gid, "taskargs": taskargs})
    logger.info("加载任务到数据库：{}", result.inserted_id)
    return result.inserted_id


def update_task(taskid, status, process):
    result = coll_task.update_one({"_id": ObjectId(taskid)}, {
                                  "$set": {"status": status, "process": process}})
    logger.info("更新任务状态：{}", result.matched_count)


def get_task(model):
    result = coll_task.find_one({"model": model, "status": None})
    result["_id"] = str(result["_id"])
    logger.info("查询到任务：{}", result["_id"])
    return result


if __name__ == '__main__':
    # add_msg(imsg)
    # find_msg_by_id(-1726724172)
    #add_repeatmsg("123",  123)
    mark_repeatmsg("123",  123)
    # pass
