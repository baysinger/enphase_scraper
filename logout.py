#!/usr/bin/env python3

BASE_URL = 'https://enlighten.enphaseenergy.com'
LOGOUT_URL = BASE_URL + '/logout'
STATE_DIR = '~/.enphase_scraper'

import os
import http.cookiejar
import urllib
import urllib.request
import urllib.error
import argparse

def report_error(msg):
    print(msg)
    return

parser = argparse.ArgumentParser()
parser.add_argument('--statedir', dest='statedir', default=os.path.expanduser(STATE_DIR),
                    metavar='DIR',
                    help='directory to store state (default: %(default)s)')
args = parser.parse_args()
if args.statedir[-1] != '/' :
    args.statedir += '/'

cookies = http.cookiejar.MozillaCookieJar(args.statedir + 'cookiejar.txt')
cookies.load(ignore_discard=True)
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookies),
)

opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),
]

urllib.request.install_opener(opener)

page = opener.open(LOGOUT_URL)
data = page.read()
