#!/usr/bin/env python3

STATE_DIR = '~/.enphase_scraper'
BASE_URL = 'https://enlighten.enphaseenergy.com'
SYSTEM_URL = BASE_URL + '/systems/{system_id}'
STATS_URL = SYSTEM_URL + '/inverter_data_x/time_series.json'
POWER_URL = SYSTEM_URL + '/power_time_series?days=1&date={date}'
INVERTERS_URL = SYSTEM_URL + '/inverter_status_x.json'
INVERTER_STATS_URL = SYSTEM_URL + '/inverters/{inverter_id}/time_series_x'
STATS = 'POWR,DCV,DCA,ACV,ACHZ,TMPI'

import os
import errno
import datetime
import time
import json
import http.cookiejar
import urllib
import urllib.request
from lxml.html import fromstring
from lxml.html import submit_form
import urllib
import datetime
import csv
import sys
from collections import OrderedDict
import argparse

def report_error(msg):
    print(msg)
    return

parser = argparse.ArgumentParser()
parser.add_argument('--statedir', dest='statedir', default=os.path.expanduser(STATE_DIR),
                    metavar='DIR',
                    help='directory to store state (default: %(default)s)')
parser.add_argument('--sys', dest='sys',
                    help='system ID')
parser.add_argument('--date', dest='date',
                    help='start data (YYYY-MM-DD)')
parser.add_argument('-n', dest='n',
                    help='number of days')
args = parser.parse_args()
if args.statedir[-1] != '/' :
    args.statedir += '/'
print(args.statedir)

with open(args.statedir + 'state.json') as file:
    state = json.load(file)

# create the data directory, if it does not exist
try:
    os.makedirs('data')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

cookies = http.cookiejar.MozillaCookieJar(args.statedir + 'cookiejar.txt')
cookies.load(ignore_discard=True)
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookies),
)

opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),
]

urllib.request.install_opener(opener)

if args.sys == None:
    system_id = input("System ID [{system_id}]:".format(system_id = state['system_id']));
    if system_id == '':
        system_id = state['system_id']
else:
    system_id = args.sys

if args.date == None:
    startdatestr = input("Starting date (YYYY-MM-DD): ")
else:
    startdatestr = args.date
startdate = datetime.datetime.strptime(startdatestr, "%Y-%m-%d").date()

if args.n == None:
    days = int(input("Number of days: "))
else:
    days = int(args.n)
delta = datetime.timedelta(1)

print(INVERTERS_URL.format(system_id=system_id))
req = urllib.request.Request(url=INVERTERS_URL.format(system_id=system_id))
with urllib.request.urlopen(req) as f:
    inverters_json = f.read().decode('UTF-8')
inverters = json.loads(inverters_json)
if len(inverters) > 0:
    print('Found %d inverters:' % len(inverters))
else:
    report_error('No inverters found!\nExiting.')
    exit(0)

date = startdate
for i in range(days):
    if i != 0:
        print('Sleeping...')
        time.sleep(10)
    print(date.isoformat())
    
    url = POWER_URL.format(system_id=system_id, date=date.isoformat())
    print(url)

    with urllib.request.urlopen(url) as f:
        data = f.read().decode('UTF-8')
    json_obj = json.loads(data, object_pairs_hook=OrderedDict)

    with open('data/' + date.isoformat() + '-production_consumption.json', 'w') as datafile:
        datafile.write(json.dumps(json_obj, indent=4, separators=(',', ': ')))

    time.sleep(1)

    first = True
    for key in inverters:
        if first:
            first = False
        else:
            time.sleep(1)
        fields = {
            'date': date.isoformat(),
            'stat': STATS
        }
        urldata = urllib.parse.urlencode(fields).encode('ascii')
        url = INVERTER_STATS_URL.format(system_id=system_id, inverter_id=key)
        print(url)
        req = urllib.request.Request(url=url, data=urldata, method='GET')
        with urllib.request.urlopen(req) as f:
            data = f.read().decode('UTF-8')
        json_obj = json.loads(data, object_pairs_hook=OrderedDict)

        with open('data/' + date.isoformat() + '-' + inverters[key]['serialNum'] + '.json', 'w') as datafile:
            datafile.write(json.dumps(json_obj, indent=4, separators=(',', ': ')))

        time.sleep(1)

    date += delta
