import asyncio
from flask import Flask, request
from loguru import logger
from gevent import pywsgi
from api import msgserve
from datebase import find_msg_by_id, add_msg
from cfg.botConfig import BotConfig

# 加载配置文件
try:
    config = BotConfig.load_config()
except Exception as e:
    logger.error("配置文件读取失败：{}", e)
    exit(1)

app = Flask(__name__)

# 重复消息排除
msgid = set()

# 服务器处理消息


@app.route('/', methods=["POST"])
async def post_data():
    global msgid
    # 跳过心跳事件
    if request.get_json().get('post_type') == "meta_event" and request.get_json().get('meta_event_type') == "heartbeat":
        return 'OK'
    if find_msg_by_id(request.get_json().get('message_id')) != None:
        return 'OK'
    else:
        add_msg(request.get_json())
    match request.get_json().get('post_type'):
        case "message":
            if request.get_json().get('message_type') == 'private':
                uid = request.get_json().get('sender').get('user_id')  # 获取发送者的 QQ 号
                message = request.get_json().get('raw_message')  # 获取消息内容
                logger.info("{}发来：{}", uid, message[:20])
                await msgserve(message.replace(
                    "[CQ:at,qq="+str(config["gocq"]["qq"])+"]", ""), uid, None)
            elif request.get_json().get('message_type') == 'group':  # 如果是群聊信息
                gid = request.get_json().get('group_id')  # 获取群号
                uid = request.get_json().get('sender').get('user_id')  # 获取发送者的 QQ 号
                message = request.get_json().get('raw_message')  # 获取消息内容
                logger.info("群聊{}的{}发来：{}", gid, uid, message[:20])
                if config["at"] == True:
                    if "[CQ:at,qq="+str(config["gocq"]["qq"])+"]" in message:
                        logger.info("接收到@消息")
                        await msgserve(message.replace(
                            "[CQ:at,qq="+str(config["gocq"]["qq"])+"]", ""), uid, gid)
                elif config["slash"] == True:
                    if message[0] == "/":
                        await msgserve(message, uid, gid)
                else:
                    await msgserve(message, uid, gid)
        case "notice":

            pass
        case default:
            pass
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
    else:
        logger.info("服务器启动成功")
