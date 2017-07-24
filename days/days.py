#qpy:qpyapp

from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from datetime import date, timedelta
from io import open
from multiprocessing.dummy import Pool
import multiprocessing
import time

droid = None
try:
    import android
    droid = android.Android()
    file_name = '/sdcard/days.htm'

    droid.dialogCreateHorizontalProgress('days.pravoslavie.ru', 'Downloading daily reading', 1)
    droid.dialogShow()

    def open_in_browser():
        try:
            droid.startActivity(
                'android.intent.action.VIEW',
                'file://' + file_name,
                'text/html',
                None,
                False,
                'com.android.chrome',
                'com.google.android.apps.chrome.Main')
        except:
            print('error')
except ImportError:
    import webbrowser
    file_name = '/tmp/days.htm'
    def open_in_browser():
        webbrowser.open('file://' + file_name)

def get_urls(s, selector):
    l = s.select(selector)
    return sorted(set([a.get('href') for a in l]))

def get_soup(url):
    html = urlopen(url)
    return BeautifulSoup(html, 'html.parser')

lives = set([])
def get_life(url):
    s = get_soup(url)
    l = s.select('td.main ul a[href*="/Life/"]')
    if len(l) >= 1:
        print('get_life', url)
        u = l[0].get('href').split('/')[-1]
        u = 'https://days.pravoslavie.ru/Life/' + u
        return get_life(u)
    else:
        if not url in lives:
            lives.add(url)
            return str(s.select('td.main')[0])
        else:
            return ''

def get_reading(url):
    print('get_reading', url)
    s = get_soup(url)
    h2 = str(s.select('h2')[0])
    h3 = str(s.select('h3')[0])
    a = s.select('a[name="z"]')[0]
    p1 = a.parent
    P = [str(p) for p in p1.next_siblings if (p.name == 'p') & (not p.find('b') is None)]
    return '\n'.join([h2, h3, str(p1)] + P)

d = (date.today() - timedelta(days = 13))
s = get_soup("http://days.pravoslavie.ru/Days/{}.html".format(d.strftime('%Y%m%d')))

# Lives
l = get_urls(s, 'a[href*="/Life/"]')

# Readings
[sn.extract() for sn in s.select('div.DAYS_snoska')]
r = get_urls(s, 'a[href*="/bible/"]')

if not droid is None:
    droid.dialogSetMaxProgress(len(l) + len(r) + 1)

# Theophan
f = s.select('p.DP_FEOF')

h = open(file_name, 'w')
h.write("""
<html>
<head>
    <meta charset="UTF-8">
    <title>Православный Календарь</title>
    <style type="text/css">
        body {font-size: 1.1em;}
        h1 {font-size: 1.3em; margin-top: 1em;}
        h2 {font-size: 1.2em; margin-top: 1.5em;}
        img, .pic_left {display:none;}
        p.bquote b {font-weight: normal; color: black;}
        p.bquote sup {font-family: sans-serif; font-size: 0.5em; margin-right: 0.2em;}
        p.bquote {color: gray;}
    </style>
</head>
<body>\n""")
h.write('<h1>{}</h1>\n'.format(d.strftime('%b %d, %Y')))

def load_async(download, urls, progress_base):
    p = Pool(4)
    rs = p.map_async(download, urls)
    p.close()
    while (True):
        if rs.ready():
            break
        if not droid is None:
            droid.dialogSetCurrentProgress(progress_base - rs._number_left + 1)
        time.sleep(0.5)
    data = rs.get()
    for D in data:
        h.write(D)

load_async(get_life, l, len(l))
load_async(get_reading, r, len(l) + len(r))

if len(f) > 0:
    h.write('<h2>Святитель Феофан</h2>\n')
    h.write(str(f[0]))

h.write('</body>\n</html>\n')
h.close()
if not droid is None:
    droid.dialogDismiss()

open_in_browser()
