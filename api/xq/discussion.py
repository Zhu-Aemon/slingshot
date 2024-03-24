import requests


def decompose_users(user):
    """
    :param user: 用户，和decompose_posts一起使用
    :return: format后的用户
    """
    ukeys = user.keys()
    return_user = {
        'name': user['screen_name'] if 'screen_name' in ukeys else '',
        'uid': user['id'] if 'id' in ukeys else 0,
        'crtime': user['user']['created_at'] if 'user' in ukeys and 'created_at' in user['user'].keys() else 0,
        'udesc': user['description'] if 'description' in ukeys else '',
        'followers': user['followers_count'] if 'followers_count' in ukeys else 0,
        'followings': user['friends_count'] if 'friends_count' in ukeys else 0,
        'city': user['city'] if 'city' in ukeys else '',
        'province': user['province'] if 'province' in ukeys else '',
        'gender': user['gender'] if 'gender' in ukeys else 'n',
        'corpName': user['corpName'] if 'corpName' in ukeys else '',
        'verified': user['verified'] if 'verified' in ukeys else '',
        'views': user['view_count'] if 'view_count' in ukeys else 0,
        'is_corp': 'corpName' in ukeys,
        'posts': user['status_count'] if 'status_count' in ukeys else 0
    }
    return return_user


def decompose_comments(comment):
    """
    提取comment中的有效信息
    :param comment: 评论，和decompose_posts一起使用
    :return: format后的comment
    """
    ckeys = comment.keys()
    return_comment = {
        'time': comment['createdAt'] if 'createdAt' in ckeys else 0,
        'cid': comment['id'] if 'id' in ckeys else 0,
        'inReplyToCommentId': comment['inReplyToCommentId'] if 'inReplyToCommentId' in ckeys else 0,
        'text': comment['indexText'] if 'indexText' in ckeys else '',
        'likes': comment['likeCount'] if 'likeCount' in ckeys else 0,
        'pic_num': len(comment['picSizes']) if 'picSizes' in ckeys else 0,
        'user': decompose_users(comment['user']) if 'user' in ckeys else {}
    }
    return return_comment


def decompose_posts(post):
    """
    post的内容和相关属性，回复，还有发帖用户
    :param post: 帖子，需要喝xq_discussion一起使用
    :return: format后的帖子
    """
    # 先找到帖子内容
    pkeys = post.keys()
    return_post = {
        'title': post['title'] if 'title' in pkeys else '',
        'content': post['text'] if 'text' in pkeys else '',
        'pid': post['id'] if 'id' in pkeys else 0,
        'time': post['created_at'] if 'created_at' in pkeys else 0,
        'favs': post['fav_count'] if 'fav_count' in pkeys else 0,
        'likes': post['like_count'] if 'like_count' in pkeys else 0,
        'replys': post['reply_count'] if 'reply_count' in pkeys else 0,
        'retweets': post['retweet_count'] if 'retweet_count' in pkeys else 0,
        'rewards': post['reward_count'] if 'reward_count' in pkeys else 0,
        'controversial': post['controversial'] if 'controversial' in pkeys else 0,
        'reward_users': post['reward_user_count'] if 'reward_user_count' in pkeys else 0,
        'hot': post['hot'] if 'hot' in pkeys else False,
        'is_answer': post['is_answer'] if 'is_answer' in pkeys else False,
        'is_bonus': post['is_bonus'] if 'is_bonus' in pkeys else False,
        'is_refused': post['is_refused'] if 'is_refused' in pkeys else False,
        'is_reward': post['is_reward'] if 'is_reward' in pkeys else False,
        'pics': len(post['pic_sizes']) if 'pic_sizes' in pkeys else 0,
        'is_retweet': post['retweet_status_id'] != 0 if 'retweet_status_id' in pkeys else False,
        'user': decompose_users(post['user']) if 'user' in pkeys else {},
        'retweeted_post': decompose_users(post['retweeted_status']) if 'retweeted_status' in pkeys else '',
        'comments': [decompose_comments(x) for x in post['excellent_comments']] if 'excellent_comments' in pkeys else [],
        'has_offer': 'offer' in pkeys,
        'offer_amt': post['offer']['amount'] if 'offer' in pkeys else 0
    }
    return return_post


def xq_discussion(symbol, page=1, count=20, comment=0, hl=0, source='all', sort='alpha', q='', type_=11):
    """
    https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SZ002085&hl=0&source=all&sort=alpha&page=1&q=&type=11
    原始数据20条对应0.3MB
    :param symbol: 股票的symbol，字符串原始代码即可，不需要加SZ或者SH
    :param page: 分页
    :param count: 每页结果，最多20
    :param comment: 是否包含评论，0即包含
    :param hl: highlight？
    :param source: 默认all，全部来源
    :param sort: sort='alpha'，按热评排序；sort='time'，按时间排序
    :param q: 默认为空
    :param type_: 11，固定值
    :return: JSON格式的返回值
    """
    # 首先在各个股票代码前加上交易所标识符
    if symbol.startswith('6'):
        symbol = 'SH' + symbol
    else:
        symbol = 'SZ' + symbol
    url = "https://xueqiu.com/query/v1/symbol/search/status.json"
    params = {
        "symbol": symbol,
        "page": page,
        "count": count,
        "comment": comment,
        "hl": hl,
        "source": source,
        "sort": sort,
        "q": q,
        "type": type_
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Cookie": "xqat=52dfb79aed5f2cdd1e7c2cfc56054ac1f5b77fc3"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error": "Failed to fetch data", "status_code": response.status_code}
    # 开始提取数据
    data = response.json()
    print(data)
    total_count = data['count']
    posts = data['list']
    posts = [decompose_posts(x) for x in posts]
    return {"total_count": total_count, "posts": posts}
