#!/usr/bin/env python3
import settings
from pytracker import Tracker, PivotalStatistics
import sys

if len(sys.argv) < 2:
	print("usage: {} [label_for_stocores_to_be_calculated]\nexample: {} week106".format(sys.argv[0],sys.argv[0]))
	sys.exit(1)

tracker = Tracker(settings.project_id, settings.token)
print("Grabbing data from label [{}]...".format(sys.argv[1]))
the_stories = tracker.GetStories("label:{} includedone:true".format(sys.argv[1]))

print("Got {} stories".format(len(the_stories)))

stats = PivotalStatistics()
for story in the_stories:
	stats.CalculateStatistics(story)

print(stats.RenderStatistics())


