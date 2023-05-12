from loguru import logger
from cfg.botConfig import BotConfig
from modules import binggpt, caiyun, chatgptv3, asr, xunfeigpt

config = BotConfig.load_config()

# 加载默认模块
thinking = None
bingGPT = binggpt.bingGPT()
CaiYun = caiyun.caiyun()
chatGPTv3 = chatgptv3.chatGPTv3()
Asr = asr.Asr()
Xunfei = xunfeigpt.XunfeiGPT()


def loadDefault():  # 加载默认模块
    global thinking
    if config["default"] == bingGPT.name:
        thinking = bingGPT
    elif config["default"] == CaiYun.name:
        thinking = CaiYun
    elif config["default"] == chatGPTv3.name:
        thinking = chatGPTv3
    elif config["default"] == Xunfei.name:
        thinking = Xunfei
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
    for keywords in Asr.keyword:
        if keywords in msg:
            thinking = Asr
            Default = False
    for keywords in Xunfei.keyword:
        if keywords in msg:
            thinking = Xunfei
            Default = False
    if Default == True:
        loadDefault()


def permission_ver(module, ouid, ogid):  # 权限验证
    uid = int(ouid)
    if uid in config["permission"]["superUser"]:
        logger.info("权限验证通过：{}-{}".format(uid, module))
        return True
    if ogid != None:
        gid = int(ogid)
        for i in config["permission"]["group"]:
            if i["gid"] == gid and module in i["modules"]:
                logger.info("权限验证通过：{}-{}".format(gid, module))
                return True
    # logger.warning("权限验证失败：{}-{}".format(gid, module))
    if uid != None:
        for i in config["permission"]["user"]:
            if i["uid"] == uid and module in i["modules"]:
                logger.info("权限验证通过：{}-{}".format(uid, module))
                return True
    logger.warning("权限验证失败：{}-{}".format(uid, module))
    return False


async def keyresponse(msg, uid, gid):  # 关键词回应
    resp = "error"
    global thinking
    keywords(msg)
    if not permission_ver(thinking.name, uid, gid):
        return config["responseText"]["permissionDenied"]
    if thinking.status == False:
        thinking.activate()
    logger.info("使用模块：{}".format(thinking.name))
    if thinking.name != "asr":
        resp = await thinking.response(msg)
    else:
        resp = await thinking.response(msg, uid, gid)
    return resp
