import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 超时时间
timeout = 120

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = "info"
