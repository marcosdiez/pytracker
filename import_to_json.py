#!/usr/bin/env python3
import settings
from pytracker import Story
import json
import sys

if len(sys.argv) < 2:
    print("usage: {} [inputfile.json]\nexample: {} inputfile.json".format(sys.argv[0],sys.argv[0]))
    sys.exit(1)

filename = sys.argv[1]
with open(filename, 'r') as content_file:
    content = content_file.read()

json_content = json.loads(content)
stories = []
for json_story in json_content:
    story = Story.FromJson(json_story)
    stories.append(story)
    print(story.GetOwnedBy())


print("Loaded {} stories from {}".format(len(stories), filename))
