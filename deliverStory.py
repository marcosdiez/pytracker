#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

def get_state(story_id):
    tracker = Tracker(settings.project_id, settings.token)
    story = tracker.GetStory(story_id)
    print(story.GetCurrentState())

if len(sys.argv) < 2:
    print("usage: {} story_to_be_market_as_delivered".format(sys.argv[0]))
    sys.exit(1)

for story_id in sys.argv[1:]:
    get_state(story_id)

