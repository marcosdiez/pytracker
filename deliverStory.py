#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys


if len(sys.argv) < 2:
	print("usage: {} story_to_be_market_as_delivered".format(sys.argv[0]))
	sys.exit(1)

tracker = Tracker(settings.project_id, settings.token)
story = tracker.GetStory(sys.argv[1])
story.SetCurrentState("delivered")
tracker.UpdateStory(story)
print("Story {} - {} marked as delivered.".format(story.GetStoryId(), story.GetName()))

