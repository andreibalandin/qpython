#qpy:qpyapp

import urllib.request
from bs4 import BeautifulSoup
from io import open
from multiprocessing.dummy import Pool

try:
    import android
    file_name = '/sdcard/alch.html'
    def open_in_browser():
        try:
            android.Android().startActivity(
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
    file_name = '/tmp/alch.htm'
    def open_in_browser():
        webbrowser.open('file://' + file_name)

url = 'http://elderscrollsonline.wiki.fextralife.com/Alchemy'
req = urllib.request.Request(
    url, 
    data=None, 
    headers={
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)
html = urllib.request.urlopen(req).read().decode('utf-8')
s = BeautifulSoup(html, 'html.parser')

rows = s.select('table.wiki_table tr')[1:]
reagents = {
    r.find('h4').text:
    set([t for t in r.select('td')[1].findAll(text=True) if not t.isspace()][1:])
for r in rows}

effects = set([])
for e in reagents.values():
    effects |= e

effects = { e: [r for r, e_ in reagents.items() if e in e_] for e in effects}

h = open(file_name, 'w')
h.write("""
<html>
<head>
    <meta charset="UTF-8">
    <title>ESO Alchemy Effects</title>
    <style>
        h2 { font-family: sans-serif; margin-top: 2em; }
        div { margin-bottom: 1em; font-size: 0.9em; }
        span { font-family: sans-serif; font-size: 0.8em; }
        .anchor { font-weight: bold; }
    </style>
</head>
<body>
<h1>ESO Alchemy</h1>
""")

anchor = lambda name: '<a id="{}" class="anchor">{}</a>'.format(name, name)
link = lambda name: '<a href="#{}">{}</a>'.format(name, name)
listOfLinks = lambda l: ' \u2e31 '.join([link(item) for item in sorted(l)])

h.write('<h2>Effects</h2>\n')
for e, effect_reagents in sorted(effects.items()):
    h.write('<div>{} \u2799 <span>{}</span></div>\n'.format(anchor(e), listOfLinks(effect_reagents)))

h.write('<h2>Reagents</h2>\n')
for r, e in sorted(reagents.items()):
    h.write('<div>{} \u2799 <span>{}</span></div>\n'.format(anchor(r), listOfLinks(e)))

# h.write('<h2>Compatibility</h2>\n')
# for reagent, reagent_effects in sorted(reagents.items()):
#     compatible_reagents = set([r for e, R in effects.items() if e in reagent_effects for r in R if r != reagent])
#     h.write('<div><b>{}</b> \u2799 <span>{}</span></div>\n'
#         .format(reagent, ' \u2e31 '.join(sorted(compatible_reagents))))

h.write('<body>\n</html>\n')
h.close()
open_in_browser()
