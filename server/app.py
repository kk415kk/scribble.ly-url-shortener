#!/usr/bin/env python
import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ
import string, random
from functools import wraps, update_wrapper
from flask import Flask, redirect, request, current_app, make_response

app = flask.Flask(__name__)
app.debug = True
app.secret_key = "webarch253"
app.config['APPLICATION_ROOT'] = environ.get("ROOT", "/~kkao/server/")

short_to_long_db = shelve.open("stl.db")
long_to_short_db = shelve.open("lts.db")
BASE_URL = "scribble.ly/"

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
  """Builds a template based on a GET request, with some default
  arguments"""
  return flask.render_template('home.html', title="Home")

@app.route('/shorts', methods=['POST'])
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

@app.route('/short/<name>', methods=['GET'])
def fetch_url_mapping(name):
  if name != None:
    s_url = str(name)
    if s_url in short_to_long_db:
      l_url = 'http://www.' + short_to_long_db[s_url]
      return flask.redirect(l_url)
  flask.flash("Unable to resolve shortcode: " + (str(name) if name != None else ""))
  resp = flask.make_response(flask.render_template('home.html'))
  resp.status_code = 404
  return resp

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
  resp = flask.make_response(flask.render_template('home.html'))
  resp.status_code = 404
  return resp

if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
