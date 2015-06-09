#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

def tag_story(story_id, tag=None):
	tracker = Tracker(settings.project_id, settings.token)
	story = tracker.GetStory(story_id)
	if tag != None:
		story.AddLabelsFromString(tag)
		extra_info = " tagged with [{}]".format(tag)
	else:
		extra_info = ""

	zendesk = story.GetZendeskKey()
	if zendesk != None:
		extra_info += " Zendesk: " + zendesk

	tracker.UpdateStory(story)
	print("Story {} - {} - {} - {} marked {}.".format(
		story.GetStoryId(),
		story.GetStoryType(),
		story.GetOwnedBy(),
		story.GetName(), extra_info))
	print("All labels: [{}]".format(story.GetLabelsAsString()))

if len(sys.argv) < 3:
	print("usage: {} TAG story_to_add_tags1 ... story_to_add_tagsN".format(sys.argv[0]))
	sys.exit(1)

tag = sys.argv[1]
for story_id in sys.argv[2:]:
	tag_story(story_id, tag)

