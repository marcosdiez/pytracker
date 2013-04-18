#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys


if len(sys.argv) < 2:
	print("usage: {} [label_for_stocores_to_be_calculated]\nexample: {} week106".format(sys.argv[0],sys.argv[0]))
	sys.exit(1)

tracker = Tracker(settings.project_id, settings.token)
print("Grabbing data from label [{}]...".format(sys.argv[1]))
the_stories = tracker.GetStories("label:{} includedone:true".format(sys.argv[1]))

print("Got {} stories".format(len(the_stories)))

stories = {}

def add_story(stories, story):
	owner = story.GetOwnedBy()
	story_type = story.GetStoryType()
	story_points = 1
	if story_type == "feature":
		story_points = int(story.GetEstimate())

	#print( "Story: {} - owner: {} type: {} points: {}".format(story.GetStoryId(),owner,story_type,story_points))

	if owner not in stories:
		stories[owner] = {}

	if story_type not in stories[owner]:
		stories[owner][story_type] = 0

	stories[owner][story_type] += story_points


for story in the_stories:
	add_story(stories,story)

print("Printing Scores...\n")
for programmer in sorted(stories.keys()):
	the_keys = sorted(stories[programmer].keys())


	story_type = "feature"
	if story_type in the_keys:
		print("{}\t{}\t{}".format(programmer,story_type,stories[programmer][story_type]))
		the_keys.remove(story_type)

	for story_type in the_keys:
		print("{}\t{}\t{}".format(programmer,story_type,stories[programmer][story_type]))
	print("")
