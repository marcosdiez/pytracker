#!/usr/bin/env python3
from __future__ import unicode_literals
import settings
from pytracker import Tracker, Story
import sys
import codecs

if len(sys.argv) < 3:
    print("usage: {} [label] [outputfile.json]\nexample: {} ui outputfile.json".format(sys.argv[0],sys.argv[0]))
    sys.exit(1)

label = sys.argv[1]
file_name = sys.argv[2]

tracker = Tracker(settings.project_id, settings.token)
num_stories = 0

with codecs.open(file_name, "w", "utf-8") as output:
    print("Fetching stories...")
    the_stories = tracker.GetStories("includedone:true".format(label))
    output.write("[\n")
    first_time = True
    for a_story in the_stories:
        if first_time:
            first_time = False
        else:
            output.write(",")
        num_stories+=1
        #print(a_story.GetStoryId())
        output.write(a_story.ToJson())
        output.write("\n")
    output.write("]")

print("Saved {} stories to {}".format(num_stories, file_name))
