#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

def deliver_story(story_id, tag=None):
	tracker = Tracker(settings.project_id, settings.token)
	story = tracker.GetStory(story_id)
	if story.GetStoryType() in [ "bug" , "feature" ]:
		story.SetCurrentState("delivered")
	story.RemoveLabel("test_ok")
	if tag != None:
		story.AddLabelsFromString(tag)
		extra_info = " and tagged with [{}]".format(tag)
	else:
		extra_info = ""

	zendesk = story.GetZendeskKey()
	if zendesk != None:
		extra_info += " Zendesk: " + zendesk

	tracker.UpdateStory(story)
	print("Story {} - {} - {} marked as delivered{}.".format(story.GetStoryId(), story.GetStoryType(), story.GetName(), extra_info))
	print("All labels: [{}]".format(story.GetLabelsAsString()))

if len(sys.argv) < 3:
	print("usage: {} TAG story_to_be_tagged_and_marked_as_delivered ... story_to_be_tagged_and_marked_as_deliveredN".format(sys.argv[0]))
	sys.exit(1)

tag = sys.argv[1]
for story_id in sys.argv[2:]:
	deliver_story(story_id, tag)

