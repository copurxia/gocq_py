import requests
import asyncio
from loguru import logger
from cfg.botConfig import BotConfig
from datebase import find_msg_by_id
import modules

config = BotConfig.load_config()

# 戳一戳


def c1c(uid, gid):
    sendMsg("[CQ:poke,qq={}]".format(uid), uid, gid)


def sendMsg(msg, uid, gid):
    #msg = msg.rstrip("\n")
    if msg == "error":
        msg = config["responseText"]["error"]
    try:
        if gid != None:  # 如果是群聊信息
            status = requests.get(
                url='{0}send_group_msg?group_id={1}&message={2}'.format(config["gocq"]["http"], gid, msg))
            logger.info("发送消息状态：{}", status.text)
        else:
            requests.get(
                url='{0}send_private_msg?user_id={1}&message={2}'.format(config["gocq"]["http"], uid, msg))
    except Exception as e:
        logger.error("发送消息失败：{}", e)
    else:
        logger.info("发送消息成功：{}", msg)


# 更高优先级的回应


async def msgserve(msg, uid, gid):
    if msg == "测试":
        sendMsg(config["responseText"]["ping"], uid, gid)
    elif msg == "确认模块状态":
        if modules.thinking == None:
            sendMsg(config["responseText"]["nullText"], uid, gid)
        else:
            sendMsg(config["responseText"]["moduleStatus"].format(
                modules.thinking.name), uid, gid)
    else:
        # 检查是否为回复消息
        if "[CQ:reply,id=" in msg:
            sti = msg.find("[CQ:reply,id=")
            edi = msg.find("]", sti)
            recq = msg[sti:edi+1]
            msid = int(msg[sti+13:edi])
            logger.info("回复消息ID：{}", msid)
            msg = msg.replace(recq, "")
            msgo = find_msg_by_id(msid)
            if msgo != None:
                msg += "\n"+msgo["raw_message"]
                ruid = msgo['sender']['user_id']
                msg = msg.replace("[CQ:at,qq="+str(ruid)+"]", "")
                #logger.info("处理消息内容：{}", msg)
        resp = await modules.keyresponse(msg)
        sendMsg(resp, uid, gid)
        if gid != None:
            c1c(uid, gid)


# 测试
if __name__ == "__main__":
    pass
    #msgserve("测试", "测试私聊", None)
    #msgserve("测试", None, "测试群组")
    #c1c("测试私聊", "测试群组")
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(msgserve("下午好", "测试私聊", None))
    # loop.close()
