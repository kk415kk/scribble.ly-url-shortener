#!/usr/bin/env python
from flask_cors import *
import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ
import string, random

import json
from functools import wraps
from flask import redirect, request, current_app

app = flask.Flask(__name__)
app.debug = True
app.secret_key = "webarch253"

short_to_long_db = shelve.open("stl.db")
long_to_short_db = shelve.open("lts.db")
BASE_URL = "scribble.ly/"

def support_jsonp(f): 
"""Wraps JSONified output for JSONP"""
  @wraps(f)
  def decorated_function(*args, **kwargs):
    callback = request.args.get('callback', False)
  if callback:
    content = str(callback) + '(' + str(f().data) + ')'
    return current_app.response_class(content, mimetype='application/json')
  else:
    return f(*args, **kwargs)
  return decorated_function

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
  """Builds a template based on a GET request, with some default
  arguments"""
  return flask.render_template('home.html', title="Home")


@app.route('/shorts', methods=['POST'])
@support_jsonp
def shorten_submission():
  l_url = str(request.form['url'])
  s_url = shorten_url(l_url)
  return flask.jsonify(s_url=s_url)

def shorten_url(l_url):
  if l_url in long_to_short_db:
    return long_to_short_db[l_url]
  r_shortcode = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase \
                        + string.digits) for _ in range(6))
  s_url = r_shortcode
  long_to_short_db[l_url] = s_url
  short_to_long_db[s_url] = l_url
  return s_url

@app.route('/shorts', methods=['GET'])
def fetch_all_url_mappings():
  return flask.render_template('home.html', title="Shorts")

@app.route('/short/<name>', methods=['GET'])
def fetch_url_mapping(name):
  if name != None:
    s_url = str(name)
    if s_url in short_to_long_db:
      l_url = 'http://www.' + short_to_long_db[s_url]
      return flask.redirect(l_url)
  flask.flash("Unable to resolve shortcode: " + (str(name) if name != None else ""))
  return flask.render_template('home.html', code=404)

def clean_url(url):
  if url.startswith('http://'):
    url = url[len('http://'):]
  if url.startswith('https://'):
    url = url[len('https://')]
  if url.startswith('www.'):
    url = url[len('www.'):]
  return url

@app.errorhandler(404)
def page_not_found(e):
  flask.flash("Page does not exist")
  return flask.render_template('home.html', code=404)

if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
