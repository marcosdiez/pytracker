#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

def deliver_story(story_id, tag=None):
	tracker = Tracker(settings.project_id, settings.token)
	#story = tracker.GetStory(story_id)
	tracker.AddComment(int(story_id), "the book is on the table")

if len(sys.argv) < 3:
	print("usage: {} TAG story_to_be_tagged_and_marked_as_delivered ... story_to_be_tagged_and_marked_as_deliveredN".format(sys.argv[0]))
	sys.exit(1)

tag = sys.argv[1]
for story_id in sys.argv[2:]:
	deliver_story(story_id, tag)

