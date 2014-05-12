#!/usr/bin/env python3
from __future__ import unicode_literals
import settings
from pytracker import Story
import sys
import csv

if len(sys.argv) < 2:
    print("usage: {} [inputfile.json]\nexample: {} inputfile.json".format(sys.argv[0],sys.argv[0]))
    sys.exit(1)



filename = sys.argv[1]
stories = []
with open(filename, 'r') as content_file:
    reader = csv.reader(content_file, delimiter=',', quotechar='"')
    headerrow = None
    for row in reader:
        if headerrow is None:
            headerrow = row
            continue
        story = Story.FromCsv(row)
        stories.append(story)

print("Loaded {} stories from {}".format(len(stories), filename))


# json_content = json.loads(content)
# stories = []
# for json_story in json_content:
#     story = Story.FromJson(json_story)
#     stories.append(story)
#     print(story.GetOwnedBy())



