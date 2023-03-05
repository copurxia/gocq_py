# 该分裂思维正用于彩云小译

import json
import requests
from loguru import logger
import asyncio
from cfg.botConfig import BotConfig


class caiyun:
    def __init__(self):
        self.name = "caiyun"
        self.sessions = {}  # 保存对话对象
        self.lock = asyncio.Lock()
        self.thinking = None
        self.config = BotConfig.load_config()
        self.status = False
        self.keyword = ["/caiyun", "/译", "/翻译"]

    def activate(self):
        # 激活思维
        self.status = True
        return True

    # message：对话
    async def response(self, message) -> str:
        # 从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i, "")
        async with self.lock:
            #resp = ""
            try:
                url = "http://api.interpreter.caiyunai.com/v1/translator"
                token = self.config["caiyunToken"]
                source = [message]
                payload = {
                    "source": source,
                    "trans_type": "auto2zh",
                    "request_id": "demo",
                    "detect": True,
                }

                headers = {
                    "content-type": "application/json",
                    "x-authorization": "token " + token,
                }

                response = requests.request(
                    "POST", url, data=json.dumps(payload), headers=headers)
            except Exception as e:
                resp = "看不懂了啦！"
                logger.warning("{} 出现异常：{}".format(self.name, e))
                self.status = False
            else:
                resp = json.loads(response.text)["target"][0]
                logger.info("{} 返回：{}".format(self.name, resp))
            return resp

    async def close(self):
        await self.thinking.close()


# 测试
if __name__ == "__main__":
    thinking = caiyun()
    thinking.activate()
    asyncio.run(thinking.response("hello"))
