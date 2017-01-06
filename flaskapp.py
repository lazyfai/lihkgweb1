#!/usr/bin/env python
import os
import json
import requests
import datetime
import pytz
import arrow
import time
from pymongo import MongoClient
from flask import Flask, render_template, send_from_directory, redirect

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')
#app.debug = True
client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
db = client['lihkgweb']
collection = db['cache']

@app.route('/')
def index():
    baseURL = 'https://lihkg.com/api_v1_1/'
    listURL = 'system/property'
    #client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    #db = client['lihkgweb']
    #collection = db['cache']
    #collection.ensure_index("cachetime", expireAfterSeconds=600)
    cacheitem = { "cat" : 0, "page" : 0 }
    resp = collection.find_one(cacheitem)
    if resp is not None and 'data' in resp.keys():
        data = resp['data']
    else:
        resp = requests.get(url=baseURL+listURL)
        data = json.loads(resp.text)
        cacheitem['data'] = data
        cacheitem['cachetime'] = datetime.datetime.utcnow()
        cacheid = collection.insert(cacheitem)
    channellist = []
    items = data['response']['category_list']
    for i in items:
        if i['postable']:
            name = i['name']
            catid= i ['cat_id']
            url = "/cat/%s/page/1" % (catid)
            channelitem = dict(catid=catid,name=name,url=url)
            channellist.append(channelitem)
    return render_template('channel.html', channellist=channellist)

@app.route('/healthcheck')
def healthcheck():
    env = []
    for k, v in os.environ.items():
        env.append(dict(name=k, value=v))
    return render_template('env.html', env=env)

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

@app.route('/assets/<path:resource>')
def serveAsset(resource):
    return redirect('https://lihkg.com/assets/'+resource, 301)

@app.route('/cat/<int:catid>/page/<int:pageid>')
def listcat(catid=None,pageid=None):
    baseURL = 'https://lihkg.com/api_v1_1/'
    listURL = 'thread/category'
    listParams = dict()
    listParams['cat_id'] = catid
    listParams['page'] = pageid
    listParams['count'] = 50
    #client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    #db = client['lihkgweb']
    #collection = db['cache']
    #collection.ensure_index("cachetime", expireAfterSeconds=600)
    cacheitem = { "cat" : catid, "page" : pageid }
    resp = collection.find_one(cacheitem)
    if resp is not None and 'data' in resp.keys():
        data = resp['data']
        cache_miss = False
    else:
        resp = requests.get(url=baseURL+listURL, params=listParams)
        data = json.loads(resp.text)
        cache_miss = True
    catlist = []
    catname = data['response']['category']['name']
    items = data['response']['items']
    if len(items) < 50:
        nextpage = None
    else:
        # If it is not last page, it should be finalized, save to cache
        if cache_miss:
            cacheitem['data'] = data
            cacheitem['cachetime'] = datetime.datetime.utcnow()
            cacheid = collection.insert(cacheitem)
        nextpage = pageid + 1
    if pageid == 1:
        prevpage = None
    else:
        prevpage = pageid - 1
    for i in items:
        title = i['title']
        threadid= i ['thread_id']
        author = i['user']['nickname']
        like = i['like_count']
        dislike = i['dislike_count']
        replies = i['no_of_reply']
        lastreplyts = i['last_reply_time']
        tz = pytz.timezone('Asia/Hong_Kong')
        lastreply = arrow.get(lastreplyts).humanize(locale='zh_tw')
        url = "/thread/%s/page/1" % (threadid)
        catitem = dict(id=threadid,title=title,author=author,url=url,like=like,dislike=dislike,replies=replies,lastreply=lastreply)
        catlist.append(catitem)
    return render_template('cat.html', catid=catid, catname=catname, catlist=catlist, nextpage=nextpage, prevpage=prevpage)

@app.route('/thread/<int:threadid>/page/<int:pageid>')
def listthread(threadid=None,pageid=None):
    baseURL = 'https://lihkg.com/api_v1_1/'
    listURL = 'thread/%s/page/%s' % ( threadid, pageid )
    #client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    #db = client['lihkgweb']
    #collection = db['cache']
    #collection.ensure_index("cachetime", expireAfterSeconds=600)
    cacheitem = { "thread" : threadid , "page" : pageid }
    resp = collection.find_one(cacheitem)
    if resp is not None and 'data' in resp.keys():
        data = resp['data']
        cache_miss = False
    else:
        resp = requests.get(url=baseURL+listURL)
        data = json.loads(resp.text)
        cache_miss = True
    threadlist = []
    items = data['response']['item_data']
    threadname = data['response']['title']
    catid = data['response']['category']['cat_id']
    catname = data['response']['category']['name']
    threadauthor = data['response']['user_nickname']
    lastpage = int(data['response']['total_page'])
    if pageid == lastpage:
        nextpage = None
    else:
        nextpage = pageid + 1
        if cache_miss:
        # If it is not last page, it should be finalized, save to cache
            cacheitem['data'] = data
            cacheitem['cachetime'] = datetime.datetime.utcnow()
            cacheid = collection.insert(cacheitem)
    if pageid == 1:
        prevpage = None
    else:
        prevpage = pageid - 1
    for i in items:
        postid= i ['post_id']
        author = i['user_nickname']
        postts = i['reply_time']
        tz = pytz.timezone('Asia/Hong_Kong')
        posttime = arrow.get(postts).humanize(locale='zh_tw')
        content = i['msg']
        threaditem = dict(id=postid,author=author,content=content,time=posttime)
        threadlist.append(threaditem)
    return render_template('thread.html', author=threadauthor, catid=catid, catname=catname, threadid=threadid, threadname=threadname, threadlist=threadlist, nextpage=nextpage, prevpage=prevpage, lastpage=lastpage)

if __name__ == '__main__':
    app.run()
