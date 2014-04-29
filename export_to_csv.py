#!/usr/bin/env python3
import settings
from pytracker import Tracker, Story
import sys

if len(sys.argv) < 2:
    print("usage: {} [label]\nexample: {} ui".format(sys.argv[0],sys.argv[0]))
    sys.exit(1)


tracker = Tracker(settings.project_id, settings.token)

print(Story.CsvHeader())
the_stories = tracker.GetStories("label:{} includedone:true".format(sys.argv[1]))
for a_story in the_stories:
    print(a_story.ToCsv())
