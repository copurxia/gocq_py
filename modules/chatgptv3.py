# 该分裂思维正用于chatgpt

from revChatGPT.V3 import Chatbot
from loguru import logger
import asyncio
from cfg.botConfig import OpenAiConfig


class chatGPTv3:
    def __init__(self):
        self.name = "chatGPT-official"
        self.sessions = {}  # 保存对话对象
        self.lock = asyncio.Lock()
        self.thinking = None
        self.config = OpenAiConfig.load_config()
        self.status = False
        self.keyword = ["/chatgpt_official"]

    def activate(self):
        if not (self.config["api_key"]):
            logger.error(
                "openAiConfig.json 配置文件出错！api_key不存在")
            return False
        try:
            self.thinking = Chatbot(
                api_key=self.config["api_key"],
                proxy=self.config["proxy"],
                max_tokens=100,
            )
            logger.info("chatGPT: 初始化成功")
        except Exception as e:
            logger.warning("{} 初始化失败：{}".format(self.name, e))
            return False
        self.status = True
        return True

    # message：对话，id：谁说的
    async def response(self, message) -> str:
        # 从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i, "")
        resp = ""
        async with self.lock:
            try:
                resps = self.thinking.ask(message)
                for i in resps:
                    logger.info("chatGPT: {}".format(i))
                    resp += i
                logger.info("chatGPT: {}".format(resp))
            except Exception as e:
                resp = "error"
                logger.warning("{} 出现异常：{}".format(self.name, e))
                self.status = False
            return resp


# 测试
if __name__ == "__main__":
    thinking = chatGPTv3()
    thinking.activate()
    asyncio.run(thinking.response("你好"))
