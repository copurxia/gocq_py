# 多进程
import multiprocessing

"""gunicorn+gevent 的配置文件"""


# 预加载资源
preload_app = True
# 绑定 ip + 端口
bind = "0.0.0.0:8000"
# 进程数 = cup数量 * 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1

# 线程数 = cup数量 * 2
threads = multiprocessing.cpu_count() * 2

# 等待队列最大长度,超过这个长度的链接将被拒绝连接
backlog = 2048

# 工作模式--协程
worker_class = "gevent"

# 最大客户客户端并发数量,对使用线程和协程的worker的工作有影响
# 服务器配置设置的值  1200：中小型项目  上万并发： 中大型
# 服务器硬件：宽带+数据库+内存
# 服务器的架构：集群 主从
worker_connections = 1200

# 进程名称
proc_name = 'gunicorn.pid'
# 进程pid记录文件
pidfile = 'app_run.log'
# 日志等级
loglevel = 'debug'
# 日志文件名
logfile = 'debug.log'
# 访问记录
accesslog = 'access.log'
# 访问记录格式
access_log_format = '%(h)s %(t)s %(U)s %(q)s'
