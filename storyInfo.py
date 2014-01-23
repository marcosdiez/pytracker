#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

def story_info(story_id):
    tracker = Tracker(settings.project_id, settings.token)
    story = tracker.GetStory(story_id)

    extra_info = ""
    zendesk = story.GetZendeskKey()
    if zendesk != None:
        extra_info += "- Zendesk: " + zendesk

    print("Story {} - {} - {} - {} {}.".format(
        story.GetStoryId(),
        story.GetStoryType(),
        story.GetOwnedBy(),
        story.GetName(), extra_info))
    print("All labels: [{}]".format(story.GetLabelsAsString()))
    print(story.GetCurrentState())
    print(story.GetDescription())




if len(sys.argv) < 2:
	print("usage: {} story_info_to_be_shown".format(sys.argv[0]))
	sys.exit(1)

for story_id in sys.argv[1:]:
	story_info(story_id)
