#!/usr/bin/env python
import os
import json
import requests
import flask

app = flask.Flask(__name__)
app.config.from_pyfile('flask.cfg')

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return flask.send_from_directory('static/', resource)

@app.route('/cat')
def listcat():
    baseURL = 'https://lihkg.com/api_v1/'
    listURL = 'thread/category'
    listParams = dict(
        cat_id = 12,
        page = 1,
        count = 50
    )
    resp = requests.get(url=baseURL+listURL, params=listParams)
    data = json.loads(resp.text)
    return data

if __name__ == '__main__':
    app.run()
