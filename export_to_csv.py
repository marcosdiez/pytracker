#!/usr/bin/env python3
import settings
from pytracker import Tracker, Story
import sys

if len(sys.argv) < 2:
    print("usage: {} [label]\nexample: {} ui".format(sys.argv[0],sys.argv[0]))
    sys.exit(1)

file_name = 'the_output.csv'
tracker = Tracker(settings.project_id, settings.token)
num_stories = 0
with open(file_name, 'w', encoding='utf-8') as output:
    output.write(Story.CsvHeader())
    output.write("\n")
    print("Fetching stories...")
    the_stories = tracker.GetStories("label:{} includedone:true".format(sys.argv[1]))
    for a_story in the_stories:
        num_stories+=1
        output.write(a_story.ToCsv())
        output.write("\n")

print("Saved {} stories to {}".format(num_stories, file_name))
