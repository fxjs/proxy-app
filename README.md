# 万能转发：

### 安装 gunicorn、Flask

> pip install gunicorn
>
> pip install Flask

### 启动守护进程

> ./start.sh
>
参数可根据服务器配置调整，参考 gunicorn 文档，建议 --workers 配置为(2*CPU)+1。

### kill 服务

> ./stop.sh

### 配置文件 `copfig.py`

- `WHITE_LIST_DOMAINS` - 定义白名单列表

### Nginx 代理服务

```shell
location /proxy/ {
    proxy_pass    http://127.0.0.1:5000/;
}
```


### 测试
> curl http://127.0.0.1:5000/http://httpbin.org/get


### 使用场景
- 部署 https 转发 http 协议
- 有外网权限的机器转发内网服务
---

