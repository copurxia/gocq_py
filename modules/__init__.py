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


def loadDefault():
    global thinking
    if config["default"] == bingGPT.name:
        thinking = bingGPT
    elif config["default"] == CaiYun.name:
        thinking = CaiYun
    elif config["default"] == chatGPTv3.name:
        thinking = chatGPTv3
    else:
        logger.warning("未知的默认模块：{}".format(config["default"]))

# 关键词回应


def keywords(msg):
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


async def keyresponse(msg):
    resp = "error"
    global thinking
    keywords(msg)
    if thinking.status == False:
        thinking.activate()
    logger.info("使用模块：{}".format(thinking.name))
    resp = await thinking.response(msg)
    return resp
