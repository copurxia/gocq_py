from loguru import logger
from cfg.botConfig import BotConfig
from modules import binggpt
from modules import caiyun
#import chatgptv1
from modules import chatgptv3

config = BotConfig.load_config()

# 加载默认模块
thinking = None
bingGPT = binggpt.bingGPT()
CaiYun = caiyun.caiyun()
chatGPTv3 = chatgptv3.chatGPTv3()


def loadDefault():  # 加载默认模块
    global thinking
    if config["default"] == bingGPT.name:
        thinking = bingGPT
    elif config["default"] == CaiYun.name:
        thinking = CaiYun
    elif config["default"] == chatGPTv3.name:
        thinking = chatGPTv3
    else:
        logger.warning("未知的默认模块：{}".format(config["default"]))


def keywords(msg):  # 关键词判断
    global thinking
    Default = True
    for keywords in CaiYun.keyword:
        if keywords in msg:
            thinking = CaiYun
            Default = False
    for keywords in bingGPT.keyword:
        if keywords in msg:
            thinking = bingGPT
            Default = False
    for keywords in chatGPTv3.keyword:
        if keywords in msg:
            thinking = chatGPTv3
            Default = False
    if Default == True:
        loadDefault()


def per_veri(moudule, uid, gid):  # 权限验证
    if uid != None:
        for i in config["permission"]["user"]:
            logger.info("i：{}".format(i))
            if i["uid"] == uid and moudule in i["modules"]:
                logger.info("权限验证成功：{} {}", moudule, uid)
                return True
    if gid != None:
        for i in config["permission"]["group"]:
            logger.info("i：{}".format(i))
            if i["gid"] == gid and moudule in i["modules"]:
                logger.info("权限验证成功：{} {}", moudule, gid)
                return True
    logger.info("权限验证失败：{} {} {}", moudule, uid, gid)
    return False


async def keyresponse(msg, uid, gid):  # 关键词回应
    resp = "error"
    global thinking
    keywords(msg)
    if thinking.status == False:
        thinking.activate()
    if not per_veri(thinking.name, uid, gid):
        return config["responseText"]["permissionDenied"]
    logger.info("使用模块：{}".format(thinking.name))
    resp = await thinking.response(msg)
    return resp
