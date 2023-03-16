# 该分裂思维用于渲染管理

import json
import requests
from loguru import logger
import asyncio
from cfg.botConfig import BotConfig
from urllib.parse import quote
from datebase import find_offline_file, find_latest_file
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


class Asr:
    def __init__(self):
        self.name = "asr"
        self.sessions = {}  # 保存对话对象
        self.lock = asyncio.Lock()
        self.thinking = None
        self.config = BotConfig.load_config()
        self.status = False
        self.args = True
        self.keyword = ["/识别", "/asr"]

    def activate(self):
        # 激活思维
        self.status = True
        return True

    # message：对话
    async def response(self, message, uid, gid) -> str:
        # 从消息中去除keyword
        for i in self.keyword:
            message = message.replace(i, "")
        async with self.lock:
            resp = "loading..."
            try:
                if gid == None:
                    if not find_offline_file(uid, message[1:]):
                        resp = "文件不存在"
                        file = find_latest_file(uid)
                        if file != None:
                            filename = file["name"]
                            logger.info(
                                "文件不存在，使用最近一次上传的文件:{}".format(filename))
                    else:
                        filename = message[1:]
                    if filename != None:
                        taskid = self.createTask(filename)
                        logger.info("创建任务:{}".format(taskid))
                        result = self.getTask(taskid)
                        while result["Data"]["Status"] == 1 or result["Data"]["Status"] == 0:
                            result = self.getTask(taskid)
                        if result["Data"]["Status"] == 3:
                            resp = "识别失败"
                            logger.warning("任务失败")
                            logger.warning("失败原因:{}".format(
                                result["Data"]["ErrorMsg"]))
                        elif result["Data"]["Status"] == 2:
                            print(len(result["Data"]["ResultDetail"]))
                            print(result["Data"]["ResultDetail"][0])
                            print(result["Data"]["ResultDetail"][1])
                            resp = "识别成功\n{}".format(
                                "{}/download/{}".format(self.config["domain"], quote(str(taskid)+".txt")))
                            with open('statics/'+str(taskid)+".txt", 'w') as f:
                                f.write(result["Data"]["Result"])
            except Exception as e:
                resp = "看不懂了啦！"
                logger.warning("{} 出现异常：{}".format(self.name, e))
                self.status = False
            else:
                pass
        return resp

    def createTask(self, name):  # 创建任务
        try:
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
            # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
            # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
            cred = credential.Credential(
                self.config["TencentCloudKey"]["SecretID"], self.config["TencentCloudKey"]["SecretKey"])
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = asr_client.AsrClient(cred, "", clientProfile)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.CreateRecTaskRequest()
            params = {
                "EngineModelType": "16k_zh",
                "ChannelNum": 1,
                "ResTextFormat": 3,
                "SourceType": 0,
                "Url": "{}/download/{}".format(self.config["domain"], quote(name)),
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个CreateRecTaskResponse的实例，与请求对象对应
            resp = client.CreateRecTask(req)
            # 输出json格式的字符串回包
            result = json.loads(resp.to_json_string())
            return result["Data"]["TaskId"]

        except TencentCloudSDKException as err:
            logger.warning("{} 出现异常：{}".format(self.name, err))

    def getTask(self, taskId):  # 获取任务
        try:
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
            cred = credential.Credential(
                self.config["TencentCloudKey"]["SecretID"], self.config["TencentCloudKey"]["SecretKey"])
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = asr_client.AsrClient(cred, "", clientProfile)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.DescribeTaskStatusRequest()
            params = {
                "TaskId": taskId
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个DescribeTaskStatusResponse的实例，与请求对象对应
            resp = client.DescribeTaskStatus(req)
            # 输出json格式的字符串回包
            return json.loads(resp.to_json_string())

        except TencentCloudSDKException as err:
            logger.warning("{} 出现异常：{}".format(self.name, err))

    async def close(self):
        await self.thinking.close()


# 测试
if __name__ == "__main__":
    thinking = Asr()
    thinking.activate()
    asyncio.run(thinking.response("/asr 新录音 30.m4a"), 1935576264, None)
