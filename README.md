# Slingshot

PS：由于个人事务原因预计会停止更新一段时间，8月后应该可以恢复更新

`Slingshot`项目是对`akshare`项目的一个拓展，对`akshare`没有实现的一些API进行了实现

`Slignshot`关注的API主要集中于板块轮动、概念、打板和行为金融学

如果觉得本项目有用，请点一个免费的star来支持我们，同时也欢迎各位contribute

目前已经实现的API：

- `api.em.calendar.trading_days`：获取从某一日开始的交易日历
- `api.jqka.breadth.breadth_live`：获取实时的市场宽度数据
- `api.jqka.breadth.breadth_intraday`：获取历史某日分时的市场宽度数据
- `api.jqka.cash_flow.hshkconnect_net_buy`：获取沪深港通的资金流向数据
- `api.jqka.dicussion.jqka_discussion_latest`：获取某只股票在同花顺股吧最新的讨论内容
- `api.jqka.dicussion.jqka_discussion_recommended`：获取某只股票在同花顺股吧被推荐的讨论内容
- `api.jqka.hot.get_hot_intraday`：同花顺热榜分时
- `api.jqka.industry.ind_stock_list`：某板块（行业板块、概念板块、地域板块）在某个日期所有成分股的涨跌情况
- `api.jqka.industry.get_ind_list`：某一天所有板块的涨跌情况
- `api.jqka.industry.ind_k_recent`：某个板块同花顺指数的日频数据，最近80条
- `api.jqka.industry.ind_k_all`：某个板块同花顺指数的全部日频数据
- `api.jqka.lhb.get_lhb_data`：获取龙虎榜某一日的详细数据
- `api.jqka.limits.daily_limits`：获取某一日涨停股票的详细信息
- `api.jqka.limits.daily_limits_hot`：获取按照板块热度排列的涨停板信息
- `api.jqka.limits.daily_cont`：获取每日连板的股票
- `api.xq.discussion.xq_discussion`：雪球上关于某只股票最新的讨论
- `api.xq.kline.xq_intraday`：雪球上获取的某只股票最近的分时数据
- `api.xq.kline.xq_trades`：雪球上获取的某只股票最近的成交明细
- `api.xq.kline.xq_snapshot`：雪球上获取的某只股票最近的盘口快照
- `api.xq.kline.xq_kline`：从雪球上获得的股票k线数据
