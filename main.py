import os
import logging
import json
import requests
import re
import time
from bs4 import BeautifulSoup

path = 'meipian/'    # 储存位置

# 日志配置
log_file_path = os.path.join(path, "logfile.log")
log_level = "DEBUG"  # 日志级别
log_format = "%(asctime)s - %(levelname)s - %(message)s"

def setup_logging():
    level = getattr(logging, log_level.upper(), logging.DEBUG)
    logging.basicConfig(
        filename=log_file_path,
        level=level,
        format=log_format
    )

wrong_url = []

def time_to_translate(time_stamp):  # 时间戳转换
    if time_stamp:
        time_local = time.localtime(int(time_stamp))
        d_time = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
        return d_time

def creat_dir(path):  # 判断是否新文章，并创建目录
    if os.path.exists(path) is False:
        os.makedirs(path)
        log_txt = f"{time_to_translate(time.time())}\t创建新文件夹{path}"
        logging.info(log_txt)
        print(log_txt)
    os.chdir(path)

def download(url, path):  # 数据流下载（音乐、图片）
    response = requests.get(url).content
    if os.path.isfile(path):
        print(f'出现同名文件：{path}')
        pass
    else:
        f = open(path, 'wb')
        f.write(response)
        f.close()

def get_kugou_music(music_id):      #来自酷狗的音乐
    music_info = 'https://child.meipian.cn/article/article-mobile/service/article/musicInfo'
    data = {
        'music_id':music_id
    }
    try:
        r = requests.post(music_info, json=data)
        music_url = json.loads(r.text)['data']['url']
        music_desc = json.loads(r.text)['data']['name']
        music_detial = [music_url, music_desc]
        return music_detial
    except Exception as e:
        log_txt = f'{time_to_translate(time.time())}\t{e}'
        logging.info(log_txt)
        print(e)

def GetJson(url):    # 从页面源码中截取数据字典，转存json格式文件
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        scripts = soup.find_all('script')
        js = None
        for script in scripts:
            if script.string and "var ARTICLE_DETAIL" in script.string:
                js = script.string
                break

        if not js:
            print("未找到合适的 JavaScript 内容")

        match = re.search(r'var ARTICLE_DETAIL\s*=\s*(\{.*?\});', js, re.DOTALL)
        if match:
            j_r = match.group(1)
            js_data = json.loads(j_r)['article']
            mask_id = js_data['mask_id']
            creat_dir(path + mask_id)
            with open('content.json', 'w+', encoding='utf-8') as f:
                f.write(json.dumps(js_data, ensure_ascii=False, indent=4))
            log_txt = f'{time_to_translate(time.time())}\t页面读取成功，转存json数据文件成功！'
            logging.info(log_txt)
            print(log_txt)
            return js_data
        else:
            print("未匹配到 ARTICLE_DETAIL")
    except:
        log_txt = f'{time_to_translate(time.time())}\t读取网页源码失败'
        logging.info(log_txt)
        print(log_txt)
        pass

def get_contents(url):         #从json文件中获取有用数据信息，并转存图片、音乐
    data = GetJson(url)
    mask_id = data['mask_id']
    create_time = time_to_translate(data['create_time'])
    try:        #解决今日无访问错误
        visit_last_update = time_to_translate(data['visit_last_update'])
        visit_today = data['visit_today']
    except:
        visit_today = '0'
        visit_last_update = None
    title = data['title']
    abstract = data['abstract']
    cover_thumb = data['cover_thumb'].split('-')[0]
    music_desc = data['music_desc']
    i_music_url = data['music_url']
    i_music_name = i_music_url.split('/')[-1]
    k_music_id = data['ext']['music_id']
    if i_music_url:
        download(i_music_url, i_music_name)
        log_txt = f'{time_to_translate(time.time())}\t从ivwen.com下载aac音乐文件：{music_desc}\t成功'
        logging.info(log_txt)
        print(log_txt)
        music_url = i_music_url
        music_name = i_music_name
    elif k_music_id:
        k_music_url = get_kugou_music(k_music_id)[0]
        k_music_name = get_kugou_music(k_music_id)[0].split('/')[-1]
        download(k_music_url, k_music_name)
        music_desc = get_kugou_music(k_music_id)[1]
        log_txt = f'{time_to_translate(time.time())}\t从kugou.com下载mp3音乐文件：{music_desc}\t成功'
        logging.info(log_txt)
        print(log_txt)
        music_url = k_music_url
        music_name = k_music_name
    else:
        log_txt = f'{time_to_translate(time.time())}\t本篇没有音乐'
        logging.info(log_txt)
        print(log_txt)
        music_url = None
        music_name = None
    visit_count = data['visit_count']
    praise_count = data['praise_count']
    list_cont = data['content']['content']
    contents = []
    for c in list_cont:
        if 'img_url' in c:
            c_img_url = c['img_url']
            contents.append(c_img_url)
            img_name = c_img_url.split('/')[-1]
            download(c_img_url, img_name)
            log_txt = f'{time_to_translate(time.time())}\t图片:{img_name}\t下载成功'
            logging.info(log_txt)
            print(log_txt)
        else:
            c_img_url = None
        if 'text' in c:
            c_text = c['text']
            contents.append(c_text)
        else:
            c_text = None
    article = {
        'mask_id' : mask_id,
        'create_time' : create_time,
        'visit_last_update' : visit_last_update,
        'visit_today' : visit_today,
        'title' : title,
        'abstract' : abstract,
        'cover_thumb' : cover_thumb,
        'music_desc' : music_desc,
        'music_url' : music_url,
        'music_name' : music_name,
        'visit_count' : visit_count,
        'praise_count' : praise_count,
        'contents' : contents
    }
    return article

def Write_Html(url):        #自动生成网页
    global o_log
    o_log = []
    dic = get_contents(url)
    mask_id = dic['mask_id']
    music = dic['music_name']
    new_contents = []
    for i in dic['contents']:
        for j in i:
            if u'\u4e00' <= j <= u'\u9fff':
                new_contents.append(i)
                break
        img = i.split('/')[-1]
        new_contents.append('<img src="{}" width="800px">'.format(img))
    hh = """
    <!DOCTYPE html>
    <html lang="zh-cn">
        <head>
            <meta charset="UTF-8">
            <title>{}</title>
        </head>
        <body>
            <div style="float:left">
                <audio controls="controls" autoplay="autoplay" loop="loop" preload="preload">
                    <source src="{}" type="audio/aac">
                </audio>
            </div>
            <div style="background-color:lightblue;width:900px;margin:0 auto;">
                <h1 style="padding:10px;text-align:center;">{}</h1>
                <ul style="list-style-type:none;text-align:center;">
                    <li style="display:inline;padding:10px;">发表时间：{}</li>
                    <li style="display:inline;padding:10px;">总浏览量：{}</li>
                    <li style="display:inline;padding:10px;">共获得点赞：{}</li>
                    <li style="display:inline;padding:10px;">今日访问量：{}</li>
                </ul>
                <h3 style="padding:20px;text-align:center;">{}</h3>
                <div style="width:800px;margin:0 auto;">{}</div>
            </div>
        </body>
    </html>
    """.format(dic['title'], music, dic['title'], dic['create_time'], dic['visit_count'],
                dic['praise_count'],dic['visit_today'],dic['abstract'],'\n'.join(new_contents))
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(hh)
    log_txt = f'{time_to_translate(time.time())}\t网页ID：{mask_id}转存成功！'
    logging.info(log_txt)
    print(log_txt)
    with open('log{}.txt'.format(time.time()), 'w', encoding='utf-8') as f:
        f.write('\n'.join(o_log))

def get_all_url(userid):        #通过用户ID获取所有文章地址列表
    post_url = 'https://www.meipian.cn/static/action/load_columns_article.php?userid=' + userid
    url = 'https://www.meipian.cn/'
    maxid = 99999999999999999999
    mask_id = []
    while maxid > 304319682:
        data = {
            'containerid': 0,
            'maxid': maxid,
            'stickmaskid': ''
        }
        response = requests.post(post_url, data=data)
        j_data = json.loads(response.content)
        for i in j_data:
            mask_id.append(i['mask_id'])
            idid = i['id']
        maxid = int(idid)
    all_url = []
    for i in mask_id:
        all_url.append(url + i)
    return all_url

def total(user_id):     #用户所有文章整体转存
    if user_id:
        all_url = get_all_url(user_id)
        log_txt = f'{time_to_translate(time.time())}\t共找到\t{len(all_url)}\t篇文章'
        logging.info(log_txt)
        print(log_txt)
        print('*'*50)
        print('警告：\n\t程序启动后将自动逐篇转存，中间无法停止，转存过程中会产生大量图片、音乐文件，请确认本地磁盘有足够的空间用来转存。')
        Y_or_N = input('是否开始转存（Y/N）：')
        if Y_or_N in ['Y','y']:
            print('*'*50)
            if os.path.exists(path) is False:
                os.makedirs(path)
            dir_child = os.listdir(path)
            ii = 0
            start_time = time.time()
            log_txt = f'{time_to_translate(start_time)}\t程序启动\n' + '*'*50 + '\n'
            logging.info(log_txt)
            print(log_txt)
            for i in all_url:
                if i.split('/')[-1] not in dir_child:
                    try:
                        Write_Html(i)
                        ii += 1
                        log_txt = f'第\t{ii}\t篇文章转存完毕\n'
                        logging.info(log_txt)
                        print(log_txt)
                        time.sleep(1)
                    except Exception as e:
                        print(e)
                        log_txt = f'***\t{i}\t转存出错***\n'
                        logging.info(log_txt)
                        wrong_url.append(i)
                        print(log_txt)
                        pass
                    os.chdir('../..')
                else:
                    log_txt = f'已存在：{i.split("/")[-1]}\t链接：{i}'
                    logging.info(log_txt)
                    print(log_txt)
            end_time = time.time()
            gm_time = time.strftime('%H:%M:%S', time.gmtime(end_time-start_time))
            log_txt = f'{time_to_translate(end_time)}\t全部文章转存完毕!\n\t\t\t{ii}\t篇成功\n\t\t\t{len(wrong_url)}\t篇失败\n\t\t\t耗时：{gm_time}\n\n{"*"*60}'
            logging.info(log_txt)
            print(log_txt)
            os.chdir('./.')
            if len(wrong_url) >= 1:
                with open('wrong_url{}.txt'.format(time.time()), 'w+', encoding='utf-8') as f:
                    f.write('\n'.join(wrong_url))

def main():     #主函数
    print('*'*60)
    t = input('请输入ID编号：')
    if t is not None and t.isdigit():
        print('*'*60+'\nUserID：{}\n\t1：转存所有文章\n\t2：转存单篇文章\n\t按任意键退出……'.format(t))
        YoN = input('请选择：')
        if YoN is not None and YoN.isdigit():
            if int(YoN) == 1:
                print('请稍等，正在查询文章列表……')
                total(t)
            if int(YoN) == 2:
                while True:
                    url = input('\n请输入要下载的美篇文章（内容页）地址：')
                    if url is not None and 'meipian' in url:
                        Write_Html(url)
                    elif url == 'exit':
                        break
                    else:
                        print('您的输入有误，请正确输入！\n退出请输入：exit')

if __name__ == '__main__':
    main()
