# Gocq_py

缓慢开发中

[lissettecarlr/kuon](https://github.com/lissettecarlr/kuon/)的自用gocq实现

项目使用poetry管理依赖需要3.10以上版本python

使用mongdb作为消息存储

支持对回复的消息进行处理

并附带戳一戳提醒

> 可参照example书写配置文件

## 使用

gocq、mongodb需要自行安装
安装配置请参考官方文档
先启动本项目再启动gocq

bing与chatgpt使用[acheong08](https://github.com/acheong08)的方案，具体配置文件可参考原项目生成

彩云小译的API需要自行申请

gocq的配置文件中需要添加
```yaml
- http: # HTTP 通信设置
      address: 0.0.0.0:5700 # HTTP监听地址
      timeout: 5 # 反向 HTTP 超时时间, 单位秒，<5 时将被忽略
      long-polling: # 长轮询拓展
        enabled: false # 是否开启
        max-queue-size: 2000 # 消息队列大小，0 表示不限制队列大小，谨慎使用
      middlewares:
        <<: *default # 引用默认中间件
      post: # 反向HTTP POST地址列表
        - url: "http://127.0.0.1:8000/" # 地址 具体课参照botconfig.yaml内容
          secret: "" # 密钥
          max-retries: 0 # 最大重试，0 时禁用
          retries-interval: 1500 # 重试时间，单位毫秒，0 时立即
```

执行以下命令进行安装

第一次运行可能耗时较久

```bash
git clone https://github.com/copurxia/gocq_py.git
cd gocq_py
poetry use 3.10 # 3.10以上版本
poetry install
poetry run python index.py
```

## 附加
虽然是自用项目，但也欢迎pr

如果有什么问题可以提issue