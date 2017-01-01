#!/usr/bin/env python
import os
import json
import requests
import datetime
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')
#app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

@app.route('/cat/<catid>')
def listcat(catid=None):
    baseURL = 'https://lihkg.com/api_v1/'
    listURL = 'thread/category'
    listParams = dict()
    listParams['cat_id'] = catid
    listParams['page'] = 1
    listParams['count'] = 50
    resp = requests.get(url=baseURL+listURL, params=listParams)
    data = json.loads(resp.text)
    catlist = []
    items = data['response']['items']
    for i in items:
        title = i['title']
        threadid= i ['thread_id']
        author = i['user']['nickname']
        url = "/thread/%s" % (threadid)
        catitem = dict(id=threadid,title=title,author=author,url=url)
        catlist.append(catitem)
    return render_template('cat.html', catid=catid, catlist=catlist)

@app.route('/thread/<threadid>')
def listthread(threadid=None):
    baseURL = 'https://lihkg.com/api_v1/'
    listURL = 'thread/%s/page/1' % ( threadid )
    resp = requests.get(url=baseURL+listURL)
    data = json.loads(resp.text)
    threadlist = []
    items = data['response']['item_data']
    for i in items:
        postid= i ['post_id']
        author = i['user_nickname']
        postts = i['reply_time']
        posttime = datetime.datetime.fromtimestamp(int(postts)).strftime('%Y-%m-%d %H:%M:%S')
        content = i['msg']
        threaditem = dict(id=postid,author=author,content=content,time=posttime)
        threadlist.append(threaditem)
    return render_template('thread.html', threadid=threadid, threadlist=threadlist)

if __name__ == '__main__':
    app.run()
