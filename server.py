#!/usr/bin/env python3

import datetime
import flask
import functools
import json

import pungen

app = flask.Flask(__name__, static_folder = None) # we want to serve static files ourselves

# http://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):
    print('nocache')
    @functools.wraps(view)
    def no_cache(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return functools.update_wrapper(no_cache, view)

@app.route('/')
def index():
    return flask.send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
@nocache
def serve_static(path):
    return flask.send_from_directory('static', path)

def _stream_results(pun_iter):
    yield 'retry: {}\n\n'.format(10**10)
    print('sent retry')
    for obj in pun_iter:
        if isinstance(obj, float): # progress
            print('sending progress', obj)
            yield 'event: progress\ndata: {:.5f}\n\n'.format(obj)
        else: # final result
            yield 'event: result\ndata: {}\n\n'.format(json.dumps(obj))

@app.route('/pun/<word1>/<word2>')
@nocache
def pun(word1, word2):
    stream = _stream_results(pungen.total_punhilliation(word1, word2))
    return flask.Response(stream, mimetype = 'text/event-stream')

if __name__ == '__main__':
    app.run(debug = True)