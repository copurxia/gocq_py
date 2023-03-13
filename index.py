import asyncio
from flask import Flask, request
from loguru import logger
from gevent import pywsgi
from api import msgserve, repeat, c1c
from modules import permission_ver
from datebase import find_msg_by_id, add_msg, add_offline_file
from cfg.botConfig import BotConfig
import threading

# 加载配置文件
try:
    config = BotConfig.load_config()
except Exception as e:
    logger.error("配置文件读取失败：{}", e)
    exit(1)

app = Flask(__name__)


class postserveThread(threading.Thread):
    def __init__(self, postjson):
        threading.Thread.__init__(self)
        self.postjson = postjson

    def run(self):
        try:
            asyncio.run(postserve(self.postjson))
        except Exception as e:
            logger.error("服务器处理消息失败：{}", e)


# 处理线程函数


async def postserve(postjson):
    # 无视心跳包
    if postjson.get('post_type') == "meta_event" and postjson.get('meta_event_type') == "heartbeat":
        return 'OK'
    match postjson.get('post_type'):
        case "message":
            # 无视重复消息并记录
            if find_msg_by_id(postjson.get('message_id')) != None:
                return 'OK'
            else:
                add_msg(postjson)
            if postjson.get('message_type') == 'private':
                uid = postjson.get('sender').get('user_id')  # 获取发送者的 QQ 号
                message = postjson.get('raw_message')  # 获取消息内容
                logger.info("{}发来：{}", uid, message[:20])
                await msgserve(message.replace(
                    "[CQ:at,qq="+str(config["gocq"]["qq"])+"]", ""), uid, None)
            elif postjson.get('message_type') == 'group':  # 如果是群聊信息
                gid = postjson.get('group_id')  # 获取群号
                uid = postjson.get('sender').get('user_id')  # 获取发送者的 QQ 号
                message = postjson.get('raw_message')  # 获取消息内容
                logger.info("群聊{}的{}发来：{}", gid, uid, message[:20])
                if permission_ver("repeat", uid, gid):  # 复读模块
                    repeat(message, uid, gid)
                if config["at"] and "[CQ:at,qq="+str(config["gocq"]["qq"])+"]" in message:
                    logger.info("接收到@消息")
                    await msgserve(message.replace(
                        "[CQ:at,qq="+str(config["gocq"]["qq"])+"]", ""), uid, gid)
                if config["slash"] and message[0] == "/":
                    logger.info("接收到/消息")
                    await msgserve(message, uid, gid)
                if config["at"] == False and config["slash"] == False:
                    await msgserve(message, uid, gid)
        case "notice":
            #logger.info("接收到通知：{}", postjson)
            match postjson.get('notice_type'):
                case "notify":
                    if postjson.get('sub_type') == "poke":
                        if postjson.get('target_id') == config["gocq"]["qq"]:
                            c1c(postjson.get('user_id'),
                                postjson.get('group_id'))
                case "offline_file":
                    logger.info("接收到{}离线文件：{}", postjson.get(
                        'user_id'), postjson.get('file').get('name'))
                    add_offline_file(postjson.get('user_id'),
                                     postjson.get('time'),
                                     postjson.get('file').get('name'),
                                     postjson.get('file').get('size'),
                                     postjson.get('file').get('url'))
        case default:
            pass
    # 服务器处理消息


@app.route('/', methods=["POST"])
async def post_data():
    postserveThread(request.get_json()).start()
    return 'OK'


# 服务器启动
if __name__ == '__main__':
    # 此处的 host和 port对应上面 yml文件的设置
    # app.run(debug=True, host='127.0.0.1',port=config["gocq"]["rhttp"])    # 本地调试用
    try:
        server = pywsgi.WSGIServer(
            ('0.0.0.0', config["gocq"]["rhttp"]), app, log=None)  # 服务器部署用
        logger.info("开始启动")
        server.serve_forever()
    except Exception as e:
        logger.error("服务器启动失败：{}", e)
        exit(1)
