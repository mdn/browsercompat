#!/usr/bin/env python

from __future__ import print_function
import re
import os.path
import random
import urllib
import webbrowser

re_url = re.compile(r'\s*"url":\s"([^"]*)"')
count = 0

print("Go through data-human.json, and open each in the browser")

# Fetch the file from github
filename = "data-human.json"
if not os.path.exists(filename):
    print("Downloading data-human.json")
    url = (
        "https://raw.githubusercontent.com/webplatform/compatibility-data"
        "/master/data-human.json")
    urllib.urlretrieve(url, filename)

# Extract the URLs
urls = []
with open(filename, 'r') as f:
    for raw_line in f:
        line = raw_line.strip()
        match = re_url.match(line)
        if match:
            url = match.group(1)
            urls.append(url)

# Open them
count = 0
while True:
    print("%d: %s" % (count, url))
    count += 1
    url = random.choice(urls)
    webbrowser.open(url + '#Specifications')
    try:
        input = raw_input  # Py2?
    except NameError:
        pass  # Nope Py3
    x = input("Enter to continue, or q+Enter to quit: ")

    if x == 'q':
        break

print("%d URLs visited" % count)
