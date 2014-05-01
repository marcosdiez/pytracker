#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys

if len(sys.argv) < 2:
	print("usage: {} story_info_to_be_shown".format(sys.argv[0]))
	sys.exit(1)

tracker = Tracker(settings.project_id, settings.token)

for story_id in sys.argv[1:]:
    story = tracker.GetStory(story_id)
    # print("--------------")
    # print(story.__dict__)
    # print("--------------")
    # tasks = story.GetTasks()
    # for task in tasks:
    #     print("--")
    #     print(task)
    #     print("--")
    #     print(task.__dict__)
    #     print("--")
    #     print(task.ToXml())
    #     print("--")
    #     print(task.ToJson())


    # print("--------------")
    print(story.ToJson())
