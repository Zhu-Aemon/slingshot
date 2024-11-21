# 异步爬取并存储数据

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