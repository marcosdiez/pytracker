#!/usr/bin/env python3
import settings
from pytracker import Tracker, Story
import sys

if len(sys.argv) < 2:
	print("usage: {} story_info_to_be_shown".format(sys.argv[0]))
	sys.exit(1)

tracker = Tracker(settings.project_id, settings.token)

print(Story.CsvHeader())
for story_id in sys.argv[1:]:
    story = tracker.GetStory(story_id)
    print(story.ToCsv())
