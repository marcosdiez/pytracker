#!/usr/bin/env python3
import sys
from pytracker import Tracker

import settings

def main():
	if len(sys.argv) < 3:
		print("usage {} label story1 [story2] [story N]".format(sys.argv[0]))
		return

	label = sys.argv[1]
	stories = sys.argv[2:]

	tracker = Tracker(settings.project_id, settings.token)
	for story_id in stories:
		story = tracker.GetStory(story_id)
		story.AddLabel(label)
		tracker.UpdateStory(story)
		print("{}-{}", story.GetStoryId(), story.GetName())

if __name__ == "__main__":
	main()

