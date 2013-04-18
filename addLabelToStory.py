#!/usr/bin/env python3
import sys
from pytracker import Tracker

import settings

class TheTracker(object):

	def __init__(self):
		self.tracker = Tracker(settings.project_id, settings.token)

	def add_labels_to_story(self, story_id, labels):
		if labels.__class__ == str:
			labels = [ labels ]

		update = 0
		story = self.tracker.GetStory(story_id)
		for label in labels:
			if label is not None and len(label) > 0:
				story.AddLabel(label)
				update += 1
		if update > 0:
			self.tracker.UpdateStory(story)
			print("Story {} updated".format(story_id))

	def remove_labels_to_story(self, story_id, labels):
		if labels.__class__ == str:
			labels = [ labels ]

		story = self.tracker.GetStory(story_id)
		for label in labels:
			story.RemoveLabel(label)
		self.tracker.UpdateStory(story)
		print("Story {} updated".format(story_id))


def main():
	if len(sys.argv) < 3:
		print("usage {} story_id label1 [label2] [label3] ... [label N]".format(sys.argv[0]))
		return

	story_id=sys.argv[1]
	labels = sys.argv[2:]
	x = TheTracker()
	x.add_labels_to_story(story_id, labels)


if __name__ == "__main__":
	main()

