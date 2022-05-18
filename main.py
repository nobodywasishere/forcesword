#!/usr/bin/env python

from flask import Flask, render_template, redirect
import requests as rq
from pprint import pprint
from pathlib import Path
import feedparser
from urlextract import URLExtract
import datetime as dt
import atexit
import pickle

app = Flask(__name__)

SF_WEB_URL = "https://sourceforge.net"
SF_API_URL = f"{SF_WEB_URL}/rest"

PROF_IMAGE_CACHE_FILE = 'prof-image-cache.pkl'

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/about/')
def about():
   return render_template('about.html')

@app.route('/favicon.ico/')
def favicon():
   return ''

@app.route('/projects/<proj>/')
@app.route('/projects/<proj>/<sub>/')
def redirectLongProj(proj, sub='summary'):
   return redirect(f'/p/{proj}/{sub}/')

@app.route('/p/<proj>/summary/')
def redirectProjSummary(proj):
   return redirect(f'/p/{proj}/')

@app.route('/p/<proj>/')
@app.route('/p/<proj>/<sub>/')
def viewProject(proj, sub='summary'):

   sum_resp = rq.get(f"{SF_API_URL}/p/{proj}")
   if 400 <= sum_resp.status_code < 500:
      return f'Error {sum_resp.status_code}'
   else:
      sum_json = formatProjJson(sum_resp.json())

   if sub != "summary":
      sub_resp = rq.get(f"{SF_API_URL}/p/{proj}/{sub}")
   else:
      sub_resp = sum_resp
   if 200 <= sub_resp.status_code < 300:
      sub_json = formatProjJson(sub_resp.json())
   else:
      sub_json = None

   if sub == "summary":
      act_json = rq.get(f"{SF_API_URL}/p/{proj}/activity/").json()
   else:
      act_json = None

   if Path(f'templates/proj_{sub}.html').exists():
      return render_template(f'proj_{sub}.html', proj=sum_json, sub_name=sub, sub=sub_json, recent_activity=act_json)
   else:
      return render_template(f'proj.html', proj=sum_json, sub_name=sub, sub=sub_json, recent_activity=act_json)

def formatProjJson(proj):
   if 'tools' in proj:
      tools = {}
      first_tools = ['summary', 'files', 'wiki', 'bugs']
      exclude_tools = ['activity', 'reviews', 'support']

      for f in first_tools:
         for tool in proj['tools']:
            if f == tool['name']:
               tools[f] = [tool]

      for tool in proj['tools']:
         if tool['name'] in tools:
            if tool in tools[tool['name']]:
               continue
            tools[tool['name']].append(tool)
         elif tool['name'] in exclude_tools:
            continue
         else:
            tools[tool['name']] = [tool]

      tools['summary'][0]['url'] = tools['summary'][0]['url'].replace('summary/', '')
      proj['tools'] = tools

   if 'developers' in proj:
      proj['developers'].sort(key=lambda item: item.get("username"))
      # Really slow
      for dev_i in range(len(proj['developers'])):
         proj['developers'][dev_i]['icon_url'] = getProfileImageUrl(proj['developers'][dev_i]['username'])

   if 'short_description' in proj:
      proj['short_description'] = proj['short_description'].splitlines()

   return proj

@app.route('/u/<user>/')
def redirectToUserProf(user):
   return redirect(f'/u/{user}/profile/')

@app.route('/u/<user>/profile/')
def viewUserProfile(user):
   resp = rq.get(f"{SF_API_URL}/u/{user}/profile")
   user_json = resp.json()
   user_json['icon_url'] = getProfileImageUrl(user, cache=False)
   act = feedparser.parse(f"{SF_WEB_URL}/u/{user}/profile/feed.rss")
   return render_template('user.html', user=user_json, user_activity=act)

def getProfileImageUrl(user, cache=True):
   global prof_image_cache
   
   # Keep the profile picture for 7 days
   if user in prof_image_cache and (prof_image_cache[user]['time'] - dt.datetime.now()) < dt.timedelta(days=21) and cache:
      icon_url = prof_image_cache[user]['icon_url']
   else:
      print(f"Getting profile picture for {user}")
      req = rq.get(f"{SF_WEB_URL}/u/{user}/profile")
      icon_url = None
      for url in URLExtract().find_urls(''.join(map(chr, req.content))):
         if 'gravatar' in url or 'user_icon' in url:
            icon_url = url
            break
      prof_image_cache[user] = {
         'icon_url': icon_url,
         'time': dt.datetime.now()
      }
   
   return icon_url

if Path(PROF_IMAGE_CACHE_FILE).exists():
   with open(PROF_IMAGE_CACHE_FILE, 'rb') as f:
      prof_image_cache = pickle.load(f)
   # print(f"Loaded prof-image-cache: {prof_image_cache}")
else:
   prof_image_cache = {}

def saveProfImageCache():
   global prof_image_cache
   # print(f"Saving prof-image-cache: {prof_image_cache}")

   if Path(PROF_IMAGE_CACHE_FILE).exists():

      with open(PROF_IMAGE_CACHE_FILE, 'rb') as f:
         prof_image_cache_old = pickle.load(f)

      # Merge the old and new caches
      for key, val in prof_image_cache_old.items():
         if key in prof_image_cache:
            if val['time'] > prof_image_cache[key]['time']:
               prof_image_cache[key] = val
         else:
            prof_image_cache[key] = val

   with open(PROF_IMAGE_CACHE_FILE, 'wb') as f:
      pickle.dump(prof_image_cache, f)

atexit.register(saveProfImageCache)

if __name__ == '__main__':
   app.run()
