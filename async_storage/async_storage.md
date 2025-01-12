# 异步爬取并存储数据

### 2025.1.12更新

已经添加了对自定义代理url的支持，但是同时要给出决定代理提取数量的参数是什么，请在配置文件中加入下面两行：
```aiignore
PROXY_API_URL=your_proxy_url
PROXY_API_NUM_PARAM=your_proxy_num_param
```

这里解释一下，假设你的代理url是http://api.xxx.com/xxx?apikey=xxx&pwd=xx&getnum=50，那么决定你代理提取数量的参数就是getnum，所以你的配置文件应当如下：

```aiignore
PROXY_API_URL=http://api.xxx.com/xxx?apikey=xxx&pwd=xx&getnum=50
PROXY_API_NUM_PARAM=getnum
```

使用代理异步爬取数据并且存储到对应的数据库中，在使用此功能前请确保在根目录下创建.env文件，env文件的模板如下：
```aiignore
# dolphindb configuration
DDB_HOST=localhost
DDB_PORT=8848
DDB_USER=admin
DDB_PASSWORD=123456

# proxy configuration
PROXY_KEY=your_proxy_key
```
请注意本项目默认你在使用代理的时候使用的是[青果云](https://www.qg.net/business/proxyip.html?region=domestic&product_type=1&extract_mode=2)的代理，注意这不是广告，相应的key请自行购买，若使用其他代理提供商的服务，请自行修改对应的代码。在购买了相应的key之后，把上面模板中的`your_proxy_key`改成你自己的key

本项目默认使用[DolphinDB](https://dolphindb.cn/)作为数据库，如果有其他需求，请自行修改代码
