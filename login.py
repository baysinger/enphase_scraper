#!/usr/bin/env python3

BASE_URL = 'https://enlighten.enphaseenergy.com'
STARTING_URL = BASE_URL + '/login'
LOGIN_URL = BASE_URL + '/login/login'
LOGIN_SUCCESS_URL = BASE_URL + '/systems'
STATE_DIR = '~/.enphase_scraper'

import os
import errno
import http.cookiejar
import urllib
import urllib.request
import urllib.error
from lxml.html import fromstring
from lxml.html import submit_form
from getpass import getpass
import argparse
import re
import json

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
print(args.statedir)

# create the state directory, if it does not exist
try:
    os.makedirs(args.statedir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# prompt for username and password
username = input('Username: ')
password = getpass('Password: ')

cookies = http.cookiejar.MozillaCookieJar(os.path.expanduser(args.statedir) + 'cookiejar.txt')
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookies),
)

opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),
]

urllib.request.install_opener(opener)

page = opener.open(STARTING_URL)
data = page.read()

doc = fromstring(data)

# iterate through the forms on the page, until we find the login form
for form in doc.xpath('//form[@action="/login/login"]'):
    if not 'user[email]' in form.fields.keys():
        #print('Username field does not exist!')
        continue;
    if not 'user[password]' in form.fields.keys():
        #print('Password field does not exist!')
        continue;
    print('Found the login form.')
    form.fields['user[email]'] = username
    form.fields['user[password]'] = password

    doc.make_links_absolute(STARTING_URL)

    #print(form.method)
    #print(form.action)
    fields = {}
    #for key in form.fields:
        #print(key, form.fields[key])

        #fields[key] = form.fields[key].encode('utf-8')

        #print(type(fields[key]))
        #s = form.fields[key].decode('unicode')
        #print(s)
        #form.fields[key] = s.encode('utf-8')
        #print(form.fields[key])

    formdata = urllib.parse.urlencode(form.fields)
    #@@@TODO: GET vs POST
    page2 = urllib.request.urlopen(form.action, bytes(formdata, 'utf-8'))
    data2 = page2.read()

    print(page2.geturl())
    # Check the URL we were sent to, to see if login succeeded
    if not page2.geturl().startswith(LOGIN_SUCCESS_URL):
        print(page2.geturl())
        report_error('Login failed')
        exit()
    else:
        print('Login succeeded!')

        # The login apparently succeeded, so try to extract the system ID
        # from the URL.
        m = re.search('^' + LOGIN_SUCCESS_URL + '/(\d+)(/.*)?$', page2.geturl())
        try:
            system_id = m.group(1)
        except IndexError:
            system_id = None
        except AttributeError:
            system_id = None

        # Put the system ID in an object and save it to the state file
        state_obj = {'system_id': system_id}
        with open(os.path.expanduser(args.statedir) + 'state.json', 'w') as statefile:
            statefile.write(json.dumps(state_obj, indent=4, separators=(',', ': ')))

        # Save the session
        cookies.save(ignore_discard=True)
    break
