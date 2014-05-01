#!/usr/bin/env python3
import settings
from pytracker import Story
import sys

if len(sys.argv) < 2:
	print("usage: {} story.json".format(sys.argv[0]))
	sys.exit(1)

filename = sys.argv[1]

with open(filename, 'r') as content_file:
    content = content_file.read()

mystory = Story.FromJson(content)
print(mystory.ToJson())
