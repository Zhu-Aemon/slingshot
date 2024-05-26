# Slingshot

PS：由于个人事务原因预计会停止更新一段时间，8月后应该可以恢复更新

`Slingshot`项目是对`akshare`项目的一个拓展，对`akshare`没有实现的一些API进行了实现

`Slignshot`关注的API主要集中于板块轮动、概念、打板和行为金融学

如果觉得本项目有用，请点一个免费的star来支持我们，同时也欢迎各位contribute

目前已经实现的一些API：

- `api.jqka.dicussion.jqka_discussion_latest`：获取某只股票在同花顺股吧最新的讨论内容
- `api.jqka.dicussion.jqka_discussion_recommended`：获取某只股票在同花顺股吧被推荐的讨论内容
- `api.jqka.hot.get_hot_intraday`：同花顺热榜分时
- `api.jqka.industry.ind_stock_list`：某板块（行业板块、概念板块、地域板块）在某个日期所有成分股的涨跌情况
- `api.jqka.industry.get_ind_list`：某一天所有板块的涨跌情况
- `api.jqka.industry.ind_index_data`：某个板块同花顺指数的日频数据
- `api.xq.discussion.xq_discussion`：雪球上关于某只股票最新的讨论
- `api.xq.kline.xq_intraday`：雪球上获取的某只股票最近的分时数据
- `api.xq.kline.xq_trades`：雪球上获取的某只股票最近的成交明细
- `api.xq.kline.xq_snapshot`：雪球上获取的某只股票最近的盘口快照
- ...待更新

### Todo：

1. 添加本地化的数据存储方案
