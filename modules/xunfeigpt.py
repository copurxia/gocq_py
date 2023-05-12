# 该分裂思维正用于chatgpt

from modules.xunfei import generate_chat_id, ask_question, set_name
from loguru import logger
import asyncio


class XunfeiGPT:
    def __init__(self):
        self.name = "XunfeiGPT"
        self.sessions = {}  # 保存对话对象
        self.lock = asyncio.Lock()
        self.new = True
        self.thinking = None
        self.status = False
        self.keyword = ["/xunfei"]

    def activate(self):
        self.chat_id = generate_chat_id()
        return True

    # message：对话，id：谁说的
    async def response(self, message) -> str:
        # 从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i, "")
        resp = ""
        async with self.lock:
            try:
                resp = ask_question(self.chat_id, message)
                if self.new:
                    resp = set_name(message, self.chat_id)
                    self.new = False
            except Exception as e:
                resp = "error"
                logger.warning("{} 出现异常：{}".format(self.name, e))
                self.status = False
                self.new = True
        return resp


# 测试
if __name__ == "__main__":
    thinking = XunfeiGPT()
    thinking.activate()
    asyncio.run(thinking.response("如何评价早八"))
