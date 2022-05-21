#!/usr/bin/env python

import time
from flask import Flask, render_template, redirect
import requests as rq
from pprint import pprint
from pathlib import Path
import feedparser
import re
import datetime as dt
import atexit
import pickle
import subprocess as sp
from dateutil import parser as dtparser

app = Flask(__name__)

SF_WEB_URL = "https://sourceforge.net"
SF_API_URL = f"{SF_WEB_URL}/rest"

PROF_IMAGE_CACHE_FILE = 'prof-image-cache.pkl'
PROF_IMAGE_CACHE_LOCK = 'prof-image-cache.pkl.lock'

@app.context_processor
def injectMetadata():
   git_commit = str(sp.check_output('git rev-list --count main'.split(' ')))[2:-3]
   git_hash = str(sp.check_output('git rev-parse --short HEAD'.split(' ')))[2:-3]
   git_date = str(sp.check_output(['git', 'log', '-n', '1', '--pretty=format:%cd', '--date=format:"%b %d, %Y"']))[3:-2]
   return dict(git_commit=git_commit, git_hash=git_hash, git_date=git_date)

@app.route('/')
def index():
   req = rq.get(f"{SF_WEB_URL}")
   if 200 <= req.status_code < 300:
      content = ''.join(map(chr, req.content))
      search = re.findall(r'href="/projects/([a-zA-Z0-9_-]+)/"', content)
      search = list(set(search))
      search.sort()
      out = []
      for proj in search:
         resp = rq.get(f"{SF_API_URL}/p/{proj}")
         out.append(formatProjJson(resp.json(), skip_images=True))
   else:
      out = []

   return render_template('home.html', projects=out)

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

def formatProjJson(proj, skip_images=False):
   if 'tools' in proj:
      tools = {}
      first_tools = ['summary']#, 'files', 'wiki', 'bugs']
      exclude_tools = ['activity', 'reviews', 'support']

      for f in first_tools:
         for tool in proj['tools']:
            if f == tool['name']:
               tools[f] = [tool]

      # for tool in proj['tools']:
      #    if tool['name'] in tools:
      #       if tool in tools[tool['name']]:
      #          continue
      #       tools[tool['name']].append(tool)
      #    elif tool['name'] in exclude_tools:
      #       continue
      #    else:
      #       tools[tool['name']] = [tool]

      tools['summary'][0]['url'] = tools['summary'][0]['url'].replace('summary/', '')
      proj['tools'] = tools

   if 'developers' in proj:
      proj['developers'].sort(key=lambda item: item.get("username"))
      # Really slow
      if not skip_images:
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
   # act_json = feedparser.parse(f"{SF_WEB_URL}/u/{user}/profile/feed.rss")
   act_json = rq.get(f"{SF_API_URL}/u/{user}/activity/").json()

   return render_template('user.html', user=user_json, recent_activity=act_json)

def getProfileImageUrl(user, cache=True):
   global prof_image_cache
   
   # Keep the profile picture for 7 days
   if user in prof_image_cache and (prof_image_cache[user]['time'] - dt.datetime.now()) < dt.timedelta(days=21) and cache:
      icon_url = prof_image_cache[user]['icon_url']
   else:
      print(f"Getting profile picture for {user}")
      req = rq.get(f"{SF_WEB_URL}/u/{user}/profile")
      icon_url = '/static/icon.png'
      content = ''.join(map(chr, req.content))

      # search for both gravatar and allura profile pictures
      search = re.search(r'https:\/\/secure\.gravatar\.com\/avatar/[a-z0-9]+', content)
      if search:
         icon_url = search.group()
      search = re.search(rf'https:\/\/a\.fsdn\.com\/allura\/u\/{user}/user_icon', content)
      if search:
         icon_url = search.group()

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

      profImageCacheLock()
      with open(PROF_IMAGE_CACHE_FILE, 'rb') as f:
         prof_image_cache_old = pickle.load(f)
      profImageCacheUnlock()

      # Merge the old and new caches
      for key, val in prof_image_cache_old.items():
         if key in prof_image_cache:
            if val['time'] > prof_image_cache[key]['time']:
               prof_image_cache[key] = val
         else:
            prof_image_cache[key] = val

   profImageCacheLock()
   with open(PROF_IMAGE_CACHE_FILE, 'wb') as f:
      pickle.dump(prof_image_cache, f)
   profImageCacheUnlock()

def profImageCacheLock():
   # Lock the file, not a perfect solution but better than nothing
   while True:
      if Path(PROF_IMAGE_CACHE_LOCK).exists():
         time.sleep(0.1)
         continue
      try:
         Path(PROF_IMAGE_CACHE_LOCK).touch(exist_ok=False)
         print('LOCKED')
         return
      except FileExistsError:
         time.sleep(0.1)
         continue

def profImageCacheUnlock():
   # Unlock the file
   Path(PROF_IMAGE_CACHE_LOCK).unlink()
   print('UNLOCKED')

atexit.register(saveProfImageCache)

@app.template_filter()
def formatDate(value, format="%b %d, %Y"):
   return dt.datetime.strftime(dtparser.parse(str(value)), format)

@app.template_filter()
def formatUnixTime(value):
   return dt.datetime.utcfromtimestamp(int(str(value)[:-3])).strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter()
def formatURL(value):
   return value.replace('https://', '').replace('http://', '')

if __name__ == '__main__':
   app.run()
