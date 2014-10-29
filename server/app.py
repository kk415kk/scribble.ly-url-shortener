#!/usr/bin/env python
import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ
import string, random
import time
from functools import wraps, update_wrapper
from flask import Flask, redirect, request, current_app, make_response

app = flask.Flask(__name__)
app.debug = True
app.secret_key = "webarch253"
app.config['APPLICATION_ROOT'] = environ.get("ROOT", "/~kkao/server/")

short_to_long_db = shelve.open("db/stl.db")
long_to_short_db = shelve.open("db/lts.db")
usage_db = shelve.open("db/usage.db", writeback=True)
BASE_URL = "scribble.ly/"

##############
#### HOME ####
##############
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
  """Builds a template based on a GET request, with some default
  arguments"""
  return flask.render_template('home.html', title="Home")

##############################
####  SHORTEN URL ROUTES  ####
##############################
@app.route('/shorts', methods=['POST'])
def shorten_submission():
  l_url = clean_url(str(request.form['url']))
  input_s_url = str(request.form.get('s_input', None))

  errors = []
  if input_s_url in short_to_long_db and not input_s_url == "":
    errors.append("Your short code is already taken - generating a new one for you!")
  elif l_url in long_to_short_db and not input_s_url == "":
    errors.append("This URL already has a short code. Please use the one below.")
  s_url = shorten_url(l_url, input_s_url)
  return flask.jsonify(s_url=s_url, errors=errors)

def shorten_url(l_url, input_s_url=""):
  if l_url in long_to_short_db:
    return long_to_short_db[l_url]
  r_shortcode = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase \
                        + string.digits) for _ in range(6)) if input_s_url == "" else \
                        input_s_url
  while r_shortcode in short_to_long_db:
    r_shortcode = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase \
                        + string.digits) for _ in range(6))
  s_url = r_shortcode
  insert_tracker(s_url) # Start tracking this URL
  long_to_short_db[l_url] = s_url
  short_to_long_db[s_url] = l_url
  return s_url

############################
####  FETCH URL ROUTES  ####
############################
@app.route('/short/<name>', methods=['GET'])
def fetch_url_mapping(name):
  if name != None:
    s_url = str(name)
    if s_url in short_to_long_db:
      update_tracker(s_url)
      mapped = short_to_long_db[s_url]
      l_url = ('http://' +  mapped) if not mapped.startswith('https://') \
              else ('https://' + mapped[len('https://'):])
      return flask.redirect(l_url)
  flask.flash("Unable to resolve shortcode: " + (str(name) if name != None else ""))
  resp = flask.make_response(flask.render_template('home.html'))
  resp.status_code = 404
  return resp

############################
####  ANALYTICS ROUTES  ####
############################
@app.route('/analytics', methods=['GET'])
def display_analytics():
  return flask.render_template('analytics.html', title="Analytics")

@app.route('/analytics_data', methods=['GET'])
def update_graph():
  return flask.jsonify(new_data=[1,2,3,4])

@app.route('/analyze', methods=['GET'])
def analyze_url():
  s_url = str(request.args['s_url'])
  data = get_tracker(s_url)
  return flask.jsonify(data)

############################
#### ANALYTICS TRACKING ####
############################
def insert_tracker(s_url):
  curr_time = time.strftime("%H")
  curr_date = time.strftime("%Y-%m-%d")
  if s_url not in usage_db:
    usage_db[s_url] = { curr_date: { curr_time: 0 } }

def update_tracker(s_url):
  curr_time = time.strftime("%H")
  curr_date = time.strftime("%Y-%m-%d")
  if curr_date in usage_db[s_url]:
    if curr_time in usage_db[s_url][curr_date]:
      print 'got here'
      print usage_db[s_url][curr_date][curr_time]
      print usage_db[s_url][curr_date][curr_time] + 1
      usage_db[s_url][curr_date][curr_time] = 5 #usage_db[s_url][curr_date][curr_time] + 1
    else:
      usage_db[s_url][curr_date][curr_time] = 1
    print usage_db
  else:
    usage_db[s_url][curr_date] = { curr_time: 1 }
  print usage_db

def get_tracker(s_url, hourly=False):
  if s_url == "" or s_url == None or s_url not in usage_db:
    return {}
  usage = dict((day, sum([usage_db[s_url][day][hour] for hour in usage_db[s_url][day]])) for day in usage_db[s_url])
  return usage

########################
#### ERROR HANDLING ####
########################
@app.errorhandler(404)
def page_not_found(e):
  flask.flash("Page does not exist")
  resp = flask.make_response(flask.render_template('home.html'))
  resp.status_code = 404
  return resp

########################
#### HELPER METHODS ####
########################
def clean_url(url):
  if url.startswith('http%3A%2F%2F'):
    url = url[len('http%3A%2F%2F'):]
  elif url.startswith('http://'):
    url = url[len('http://'):]
  if url.startswith('www.'):
    url = url[len('www.'):]
  return url

# To run the application
if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
