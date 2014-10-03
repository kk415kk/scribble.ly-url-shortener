#!/usr/bin/env python
import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ
import string, random

from datetime import timedelta
from flask import make_response, current_app
from functools import update_wrapper


app = flask.Flask(__name__)
app.debug = True
app.secret_key = "webarch253"

short_to_long_db = shelve.open("stl.db")
long_to_short_db = shelve.open("lts.db")
BASE_URL = "scribble.ly/"

# Fix to XMLHTTPRequest bug
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
  if methods is not None:
    methods = ', '.join(sorted(x.upper() for x in methods))
  if headers is not None and not isinstance(headers, basestring):
    headers = ', '.join(x.upper() for x in headers)
  if not isinstance(origin, basestring):
    origin = ', '.join(origin)
  if isinstance(max_age, timedelta):
    max_age = max_age.total_seconds()

  def get_methods():
    if methods is not None:
      return methods

    options_resp = current_app.make_default_options_response()
    return options_resp.headers['allow']

  def decorator(f):
    def wrapped_function(*args, **kwargs):
      if automatic_options and request.method == 'OPTIONS':
        resp = current_app.make_default_options_response()
      else:
        resp = make_response(f(*args, **kwargs))
      if not attach_to_all and request.method != 'OPTIONS':
        return resp

      h = resp.headers
      h['Access-Control-Allow-Origin'] = origin
      h['Access-Control-Allow-Methods'] = get_methods()
      h['Access-Control-Max-Age'] = str(max_age)
      h['Access-Control-Allow-Credentials'] = 'true'
      h['Access-Control-Allow-Headers'] = \
        "Origin, X-Requested-With, Content-Type, Accept, Authorization"
      if headers is not None:
        h['Access-Control-Allow-Headers'] = headers
      return resp

    f.provide_automatic_options = False
    return update_wrapper(wrapped_function, f)
  return decorator
# End Fix


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
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
