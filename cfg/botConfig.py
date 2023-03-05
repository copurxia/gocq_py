import yaml
from loguru import logger


class BotConfig:
    @staticmethod
    def load_config():
        try:
            with open('./cfg/botconfig.yaml', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            return data
        except FileNotFoundError:
            logger.error("配置文件不存在")
        except Exception as e:
            logger.error("配置文件加载失败，错误信息：{}", e)
        return data

    @staticmethod
    def save_config(data):
        try:
            with open('./cfg/botconfig.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(data=data, stream=file, allow_unicode=True)
        except Exception as e:
            logger.error("配置文件保存失败，错误信息：{}", e)


class OpenAiConfig:
    @staticmethod
    def load_config():
        try:
            with open('./cfg/openAiConfig.yaml', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            return data
        except FileNotFoundError:
            logger.error("配置文件不存在")
        except Exception as e:
            logger.error("配置文件加载失败，错误信息：{}", e)
        return data

    @staticmethod
    def save_config(data):
        try:
            with open('./cfg/openAiConfig.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(data=data, stream=file, allow_unicode=True)
        except Exception as e:
            logger.error("配置文件保存失败，错误信息：{}", e)


# 测试
if __name__ == "__main__":
    print(BotConfig.load_config())
    logger.info("加载配置文件成功")
