#!/usr/bin/env python

from flask import Flask, render_template, redirect
import requests as rq
from pprint import pprint
from pathlib import Path

app = Flask(__name__)

SF_API_URL = "https://sourceforge.net/rest"

@app.route('/')
def index():
   return render_template('index.html')

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

   if sub != "summary":
      sub_resp = rq.get(f"{SF_API_URL}/p/{proj}/{sub}")
   else:
      sub_resp = sum_resp

   if sub == "summary":
      act_json = rq.get(f"{SF_API_URL}/p/{proj}/activity/").json()
   else:
      act_json = None

   sum_json = formatProjJson(sum_resp.json())

   if 200 <= sub_resp.status_code < 300:
      sub_json = formatProjJson(sub_resp.json())
   else:
      sub_json = None

   if Path(f'templates/proj_{sub}.html').exists():
      return render_template(f'proj_{sub}.html', proj=sum_json, sub_name=sub, sub=sub_json, recent_activity=act_json)
   elif 400 <= sub_resp.status_code < 500:
      return render_template(f'proj_summary.html', proj=sum_json, sub_name=sub, sub=sub_resp.status_code, recent_activity=act_json)
   else:
      return render_template(f'proj_summary.html', proj=sum_json, sub_name=sub, sub=sub_json, recent_activity=act_json)

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

   if 'short_description' in proj:
      proj['short_description'] = proj['short_description'].splitlines()

   return proj

@app.route('/u/<user>/')
def redirectToUserProf(user):
   return redirect(f'/u/{user}/profile/')

@app.route('/u/<user>/profile/')
def viewUserProfile(user):
   resp = rq.get(f"{SF_API_URL}/u/{user}/profile")
   return render_template('user.html', user=resp.json())

if __name__ == '__main__':
   app.run()
