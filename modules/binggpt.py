# 该分裂思维正用于bingChat
from EdgeGPT import Chatbot, ConversationStyle
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig
from time import sleep
import os
import re


class bingGPT:
    def __init__(self):
        self.name = "bingChat"
        self.sessions = {}  # 保存对话对象
        #self.lock = asyncio.Lock()
        self.thinking = None
        self.config = OpenAiConfig.load_config()
        self.status = False
        self.keyword = ["/bing", "/必应"]

    async def activate(self):
        # 判断是否存在cookies文件
        cookiesPath = os.path.join(os.path.dirname(
            __file__), "../cfg", "bingCookies.json")
        if not os.path.exists(cookiesPath):
            logger.error(
                "bingCookies.json 配置文件未找到！请配置 Bing 到 {}".format(cookiesPath))
            return False
        try:
            self.thinking = await Chatbot.create(cookiePath=cookiesPath)
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name, e))
            return False
        self.status = True
        return True

    # message：对话
    async def response(self, message) -> str:
        logger.info("bingGPT处理对话")
        if (self.thinking == None):
            logger.error("bingGPT未初始化！")
            return ""
        try:
            respo = await self.thinking.ask(prompt=message,
                                            conversation_style=ConversationStyle.creative)
            logger.info("bingGPT:{}".format(respo))
            resp = respo["item"]["messages"][1]["text"]
            #rmurl = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=:]*', re.S)
            #resp = re.sub(rmurl, '', resp)
            logger.info("bingGPT:{}".format(resp))
        except Exception as e:
            resp = "error"
            logger.warning("{} 出现异常：{}".format(self.name, e))
            self.status = False
        return resp

    async def close(self):
        await self.thinking.close()


# 测试
if __name__ == "__main__":
    thinking = bingGPT()
    thinking.activate()
    asyncio.run(thinking.response("你好"))
