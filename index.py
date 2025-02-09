import os
import json
import time
import base64
from face_png import face_png

path = 'meipian/'
list_content = []

def py_to_pic():
    bs4 = base64.b64decode(face_png)
    with open('face.png', 'wb+') as f:
        f.write(bs4)

def time_to_translate(time_stamp):  # 时间戳转换
    if time_stamp:
        time_local = time.localtime(int(time_stamp))
        d_time = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
        return d_time

def get_list_content(path):
    def article_sort(k):
        return int(k['article_time'])
    dir_child = os.listdir(path)
    for mask_id in dir_child:
        dic_article = {}
        j_path = path + mask_id + '/content.json'
        with open(j_path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            article_title = data['title']
            article_time = data['create_time']
            article_born = time_to_translate(article_time)
            cover_img = data['content']['content']
            for i in cover_img:
                if 'img_url' in i:
                    cover_thumb = i['img_url'].split('/')[-1]
            visit_count = data['visit_count']
            praise_count = data['praise_count']
            comment_count = data['comment_count']
            article_list = [article_title, article_born,cover_thumb,visit_count,praise_count,comment_count]
            dic_article['article_time'] = article_time
            dic_article['mask_id'] = mask_id
            dic_article['article_list'] = article_list
        list_content.append(dic_article)
    list_content.sort(key=article_sort,reverse=True)
    return list_content

def write_list_page():
    py_to_pic()
    list_content = get_list_content(path)
    total_visit_count = 0
    total_praise_count = 0
    total_comment_count = 0
    box_1 =[]
    box_2 =[]
    i = 0
    for content in list_content:
        mask_id = content['mask_id']
        visit_count = int(content['article_list'][3])
        praise_count = int(content['article_list'][-2])
        comment_count = int(content['article_list'][-1])
        total_visit_count += visit_count
        total_praise_count += praise_count
        total_comment_count += comment_count
        i += 1
        a_c = content['article_list']
        id_path = path + mask_id + '/index.html'
        img_path = path + mask_id + '/' + a_c[2]
        hh_box = """<div style="width: 600px;float:left;margin-left:3px;">
                <div style="width: 180px;float:left;margin-right:5px;">
                    <img src="{}" width="150px">
                </div>
                <div style="width: 400px;float:left;">
                    <h3 style="color:#333333;font-weight:normal;font-size:18px;"><a style="text-decoration:none" href="{}">{}</a></h3>
                    <p style="color:#AAAAAA;font-size: 14px;">{}</p>
                    <ul style="list-style-type:none;text-align:right;color:#aaa;font-size: 14px;">
                        <li style="display:inline;padding:10px;">浏览量：{}</li>
                        <li style="display:inline;padding:10px;">点赞量：{}</li>
                        <li style="display:inline;padding:10px;">评论量：{}</li>
                    </ul>
                </div>
            </div>""".format(img_path,id_path,a_c[0],a_c[1],str(a_c[3]),str(a_c[4]),str(a_c[5]))
        if i % 2 == 0:
            box_2.append(hh_box)
        else:
            box_1.append(hh_box)
    hh = """
<!DOCTYPE html>
<html lang="zh-cn">

<head>
    <meta charset="UTF-8">
    <title>兔子和狼的专栏-美篇</title>
</head>

<body>
    <div style="background-color:lightblue;width:1200px;margin:0 auto;">
        <div style="height:180px;">
            <div style="width: 200px;float: left;margin: 10px 20px 10px 100px;"><img src="face.png" width="140px" height="150px"></div>
            <p style="margin-left: 280px;"><br><br><br>兔子和狼<br>美篇号 246038462<br></p>
            <ul style="list-style-type:none;margin-left: 200px;">
                <li style="display:inline;padding:10px;">文章总数：{}</li>
                <li style="display:inline;padding:10px;">总浏览量：{}</li>
                <li style="display:inline;padding:10px;">总点赞量：{}</li>
                <li style="display:inline;padding:10px;">总评论量：{}</li>
            </ul>
            <div style="padding:0 30px;text-align:right;color:#aaa;font-size: 14px;background-image:url('https://tva1.sinaimg.cn/crop.0.0.180.180.180/7b570c94jw1e8qgp5bmzyj2050050aa8.jpg');background-position:right top;background-size:20px 20px;background-repeat:no-repeat;">技术支持：飞戈</div>
        </div>
        <div style="width:600px;margin:0 auto;float:left;">{}</div>
        <div style="width:600px;margin:0 auto;float:left;">{}</div>
    </div>
</body>

</html>
    """.format(len(list_content),total_visit_count,total_praise_count,total_comment_count,''.join(box_1),''.join(box_2))
    with open('index.html', 'w+', encoding='utf-8') as f:
        f.write(hh)

def main():
    write_list_page()

if __name__ == '__main__':
    main()
