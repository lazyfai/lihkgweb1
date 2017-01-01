#!/usr/bin/env python
import os
import json
import requests
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
    print ("Category [%s] = %s" % (data['response']['category']['cat_id'],data['response']['category']['name']))
    catlist = []
    items = data['response']['items']
    for i in items:
        title = i['title']
        threadid= i ['thread_id']
        author = i['user']['nickname']
        url = "%sthread/%s/page/1" % (baseURL, threadid)
        catitem = dict(id=threadid,title=title,author=author,url=url)
        catlist.append(catitem)
    return render_template('cat.html', catid=catid, catlist=catlist)

if __name__ == '__main__':
    app.run()
