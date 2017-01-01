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

@app.route('/cat')
def listcat():
    baseURL = 'https://lihkg.com/api_v1/'
    listURL = 'thread/category'
    listParams = dict()
    listParams['cat_id'] = 12
    listParams['page'] = 1
    listParams['count'] = 50
    resp = requests.get(url=baseURL+listURL, params=listParams)
    data = json.loads(resp.text)
    return render_template('cat.html', content=data)

if __name__ == '__main__':
    app.run()
