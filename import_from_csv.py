#!/usr/bin/env python3
from __future__ import unicode_literals
from pytracker import StoryList
import sys

if len(sys.argv) < 2:
    print("usage: {} [inputfile.json]\nexample: {} inputfile.json".format(sys.argv[0],sys.argv[0]))
    sys.exit(1)

filename = sys.argv[1]
story_list = StoryList()
story_list.ImportFromCsvFile(filename)
stories = story_list.stories

print("Loaded {} stories from {}".format(len(stories), filename))
print(story_list.RenderStatistics())
