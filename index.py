import asyncio
import requests
from json import dumps
from os import path, getcwd
from flask import Flask, request, send_from_directory, make_response
from loguru import logger
from gevent import pywsgi
from api import msgserve, repeat, c1c, sendMsg
from modules import permission_ver
import datebase
from cfg.botConfig import BotConfig

# 加载配置文件
try:
    config = BotConfig.load_config()
except Exception as e:
    logger.error("配置文件读取失败：{}", e)
    exit(1)

app = Flask(__name__)


# 处理线程函数


async def postserve(postjson):
    # 无视心跳包
    if postjson.get('post_type') == "meta_event" and postjson.get('meta_event_type') == "heartbeat":
        return 'OK'
    match postjson.get('post_type'):
        case "message":
            # 无视重复消息并记录
            if datebase.find_msg_by_id(postjson.get('message_id')) != None:
                return 'OK'
            else:
                datebase.add_msg(postjson)
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
                    await msgserve(message[1:], uid, gid)
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
                    datebase.add_offline_file(postjson.get('user_id'),
                                              postjson.get('time'),
                                              postjson.get('file').get('name'),
                                              postjson.get('file').get('size'),
                                              postjson.get('file').get('url'))
                    if postjson.get('file').get('size') < 1024*1024*1024*5:  # 小于5G
                        logger.info("开始下载离线文件")
                        file = postjson.get('file').get('url')
                        open(path.join(getcwd(), "statics", postjson.get('file').get(
                            'name')), 'wb').write(requests.get(file).content)
        case default:
            pass
    # 服务器处理消息


@app.route('/', methods=["POST"])
async def serve_gocq():
    await postserve(request.get_json())
    return 'OK'


@app.route('/add_tasks/', methods=["POST"])
def add_tasks():
    logger.info("接收到添加任务请求：{}", request.get_json())
    try:
        id = datebase.add_task(request.get_json().get('model'),
                               None,
                               request.get_json().get('subtype'),
                               request.get_json().get('uid'),
                               request.get_json().get('gid'),
                               request.get_json().get('taskargs'))
    except Exception as e:
        logger.error("添加任务失败：{}", e)
        return 'error'
    return str(id)


@app.route('/report_tasks_status/', methods=["POST"])
def report_tasks():
    status = request.get_json().get('status')
    logger.info("接收到任务状态报告：{}", status)
    if status == "error":
        logger.error("任务执行失败：{}", request.get_json().get('process'))
    elif status == "done":
        logger.success("任务执行成功：{}", request.get_json().get('process'))
        sendMsg(request.get_json().get('uid'), request.get_json().get('gid'),
                "{}任务执行成功".format(request.get_json().get('id')))
    try:
        datebase.update_task(request.get_json().get('id'),
                             request.get_json().get('status'),
                             request.get_json().get('process'))
    except Exception as e:
        logger.error("添加任务失败：{}", e)
        return 'error'
    return 'OK'


@app.route('/get_tasks/', methods=["GET"])
def get_tasks():
    logger.info("接收到获取任务请求")
    model = request.args.get('model')
    if model != None:
        return dumps(datebase.get_task(model))
    return "error"


@app.route('/get_offline_file/', methods=["GET"])
def get_offline_file():
    logger.info("接收到获取离线文件请求")
    uid = request.args.get('uid')
    name = request.args.get('name')
    if uid != None and name != None:
        return dumps(datebase.offer_offline_file(int(uid), name))
    return "error"


@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = getcwd()+"/statics/"  # 假设在当前目录
    response = make_response(send_from_directory(
        directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode().decode('latin-1'))
    return response


@app.route('/upload_file/', methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    file_ext = path.splitext(uploaded_file.filename)[1]
    if file_ext not in config['upload_extension']:
        return 400
    if uploaded_file.filename != '':
        uploaded_file.save("statics/"+uploaded_file.filename)
    return "OK"


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
