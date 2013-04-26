#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

def deliver_story(story_id):
	tracker = Tracker(settings.project_id, settings.token)
	story = tracker.GetStory(story_id)
	story.SetCurrentState("delivered")
	story.RemoveLabel("test_ok")
	tracker.UpdateStory(story)
	print("Story {} - {} marked as delivered.".format(story.GetStoryId(), story.GetName()))

if len(sys.argv) < 2:
	print("usage: {} story_to_be_market_as_delivered".format(sys.argv[0]))
	sys.exit(1)

for story_id in sys.argv[1:]:
	deliver_story(story_id)

