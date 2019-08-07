import re,os,csv,json,time,requests,random
from urllib import request

# 生成一个session对象，保存cookie等信息
s = requests.Session()

# 微博登陆
def login():
    # 登陆地址的url
    login_url = 'https://passport.weibo.cn/sso/login'

    # 构建请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36',
        'Referer': 'https://passport.weibo.cn/signin/login'
    }

    # 登陆用户信息
    data = {'username': '微博用户名',
            'password': '微博密码',
            'savestate': 1,
            'entry': 'mweibo',
            'mainpageflag': 1
            }

    # 登陆
    start_login = s.post(login_url,headers=headers,data=data)

    res = json.loads(start_login.text)

    if res['msg'] == '':
        print('登陆成功！')
    else:
        print('登录失败，原因为{0}'.format(res['msg']))


def topic_index():
    global min_since_id,flag
    flag = False
    min_since_id=''
    # 超话提取信息网址
    if flag == False:
        base_url = 'https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&containerid=1008087a8941058aaf4df5147042ce104568da_-_feed'
    else:
        base_url = 'https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&containerid=1008087a8941058aaf4df5147042ce104568da_-_feed&since_id={0}'.format(min_since_id)


    # 构建请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36',
        'Referer': 'https://m.weibo.cn/p/1008087a8941058aaf4df5147042ce104568da/super_index?jumpfrom=weibocom'
    }

    req = s.get(base_url, headers=headers)
    # 解析数据 提取相关信息
    info_json = json.loads(req.text)
    # 只提取微博相关信息
    cards = info_json['data']['cards']

    # 进一步提取用户的微博信息
    card_group = cards[2]['card_group']
    for card in card_group:
        # 创建保存用户惜的列表，以代写入csv文件
        user_list = []
        # 提取用户微博发送内容块
        mblog = card['mblog']
        # 提取用户信息块
        user = mblog['user']
        # 获取用户信息
        try:
            userinfo = user_info(user['id'])
        except:
            print('id为{0}的用户信息获取失败'.format(user['id']))
            continue

        # 将用户信息放入列表
        user_list.append(user['id'])
        user_list.extend(userinfo)

        # 获取翻页id
        r_since_id = mblog['id']
        user_list.append(r_since_id)
        # 获取微博内容并清洗
        context = re.compile(r'<[^>]+>', re.S).sub(' ', mblog['text'])

        # 除去无用信息
        text = context.replace('周杰伦超话','').strip()
        user_list.append(text)

        # 判断信息是否齐全
        if len(user_list) < 7:
            print('信息不齐全!')
            continue

        # 将数据写入crv文件
        with open('./sina_topic.csv','a',encoding='utf-8',newline='') as f:
            csv_write = csv.writer(f)
            csv_write.writerow(user_list)

        # 获取最小since_id,用于翻页请求
        if min_since_id:
            min_since_id = r_since_id if min_since_id > r_since_id else min_since_id
        else:
            min_since_id = r_since_id

        flag = True

        # 爬取间隔
        time.sleep(random.randint(3,6))




# 用户个人信息提取
def user_info(uid):
    # 用户个人信息url
    user_url = 'https://m.weibo.cn/api/container/getIndex?containerid=230283{0}_-_INFO'.format(uid)
    # 构建请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36',
        'Referer': 'https://m.weibo.cn/p/1008087a8941058aaf4df5147042ce104568da/super_index?jumpfrom=weibocom'
    }
    req = s.get(url=user_url,headers=headers)
    # 解析数据 获取相关信息
    json_user = json.loads(req.text)

    userlist = []
    # 提取用户信息
    userinfo = json_user['data']['cards'][1]['card_group']
    username = json_user['data']['cards'][0]['card_group']

    # 用户名
    user_name = username[1]['item_content']
    userlist.append(user_name)

    # 用户的性别
    user_sex = userinfo[1]['item_content']
    userlist.append(user_sex)

    # 用户的生日
    user_birth = userinfo[2]['item_content']
    pat = r"\d+"
    bir = re.findall(pat, user_birth)
    if bir == [] or len(bir) < 3 or '0000' in bir or '0001' in bir:
        userlist.append('')
    else:
        userlist.append(bir[0])

    # 用户的地区
    global user_area
    user_area = userinfo[3]['item_content']
    if '其他' in user_area or '海外' in user_area:
        userlist.append('')
    elif '单身' in user_area or '恋爱' in user_area or '已婚' in user_area:
        user_area = userinfo[4]['item_content']
        userlist.append(user_area[:2])
    elif '黑龙江' in user_area or '内蒙古' in user_area:
        userlist.append(user_area[:3])
    else:
        userlist.append(user_area[:2])

    return userlist


if __name__ == '__main__':
    login()
    if os.path.exists('sina_topic.csv'):
        os.remove('sina_topic.csv')

    for i in range(1000):
        print('正在爬取第{0}页'.format(i + 1))
        topic_index()

