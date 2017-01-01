#!/usr/bin/env python
import os
import json
import requests

def application(environ, start_response):

    ctype = 'text/plain'
    if environ['PATH_INFO'] == '/health':
        response_body = "1"
    elif environ['PATH_INFO'] == '/env':
        response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
        response_body = '\n'.join(response_body)
    elif environ['PATH_INFO'] == '/cat':
        baseURL = 'https://lihkg.com/api_v1/'
        listURL = 'thread/category'
        listParams = dict(
            cat_id = 12,
            page = 1,
            count = 50
        )
        resp = requests.get(url=baseURL+listURL, params=listParams)
        data = json.loads(resp.text)
        ctype = 'text/html'
        response_template = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <title>Welcome to OpenShift</title>
<body>
<pre>
%s
</pre>
</body>
</html>'''
        response_body = response_template % (data)
        response_body = response_body.encode('utf-8')

        status = '200 OK'
        response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
        #
        start_response(status, response_headers)
        return [response_body ]
    else:
        ctype = 'text/html'
        response_body = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <title>Welcome to OpenShift</title>
<body>
Nothing here.
</body>
</html>'''
    response_body = response_body.encode('utf-8')

    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    #
    start_response(status, response_headers)
    return [response_body ]

#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
