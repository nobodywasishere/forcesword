#!/usr/bin/env python

from flask import Flask, render_template
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
@app.route('/p/<proj>/')
@app.route('/p/<proj>/<sub>/')
def viewProject(proj, sub='summary'):

   sum_resp = rq.get(f"{SF_API_URL}/p/{proj}")
   if sub != "summary":
      sub_resp = rq.get(f"{SF_API_URL}/p/{proj}/{sub}")
   else:
      sub_resp = sum_resp

   sum_json = sum_resp.json()
   sum_json = formatProjSummaryJson(sum_json)

   if Path(f'templates/proj_{sub}.html').exists() and 200 <= sub_resp.status_code < 500:
      return render_template(f'proj_{sub}.html', proj=sum_json, sub_name=sub, sub=sub_resp.json())
   elif 400 <= sub_resp.status_code < 500:
      return render_template(f'proj_summary.html', proj=sum_json, sub_name=sub, sub=sub_resp.status_code)
   else:
      return render_template(f'proj_summary.html', proj=sum_json, sub_name=sub, sub=sub_resp.json())

def formatProjSummaryJson(proj):
   tools = {}
   first_tools = ['summary', 'files', 'reviews', 'support', 'wiki', 'bugs']

   for f in first_tools:
      for tool in proj['tools']:
         if f == tool['name']:
            tools[f] = [tool]

   for tool in proj['tools']:
      if tool['name'] in tools:
         if tool in tools[tool['name']]:
            continue
         tools[tool['name']].append(tool)
      else:
         tools[tool['name']] = [tool]

   tools['summary'][0]['url'] = tools['summary'][0]['url'].replace('summary/', '')
   proj['tools'] = tools
   return proj

@app.route('/u/<user>/')
@app.route('/u/<user>/profile')
def viewUserProfile(user):
   resp = rq.get(f"{SF_API_URL}/u/{user}/profile")
   return render_template('user.html', user=resp.json())

if __name__ == '__main__':
   app.run()
