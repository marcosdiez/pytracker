#!/usr/bin/env python3
import settings
from pytracker import Tracker
import sys


def deliver_story(story_id, tag=None):
    tracker = Tracker(settings.project_id, settings.token)
    story = tracker.GetStory(story_id)
    if story.GetStoryType() in ["bug", "feature"]:
        story.SetCurrentState("delivered")
    if tag is not None:
        story.AddLabelsFromString(tag)
        extra_info = " and tagged with [{}]".format(tag)
    else:
        extra_info = ""

    zendesk = story.GetZendeskKey()
    if zendesk is not None:
        extra_info += " Zendesk: " + zendesk

    tracker.UpdateStory(story)
    print("Story {} - {} - {} - {} marked as delivered{}.".format(
        story.GetStoryId(),
        story.GetStoryType(),
        story.GetOwnedBy(),
        story.GetName(), extra_info))

    all_labels = story.GetLabelsAsString()
    print("All labels: [{}]".format(all_labels))

    if all_labels.find("no_test") < 0 and all_labels.find("test_ok") < 0:
        print("----------------------------------------------------")
        print("Warning: this story does not have neither a NO_TEST nor TEST_OK tag")
        print("----------------------------------------------------")


if len(sys.argv) < 3:
    print(
    "usage: {} TAG story_to_be_tagged_and_marked_as_delivered ... story_to_be_tagged_and_marked_as_deliveredN".format(
        sys.argv[0]))
    sys.exit(1)

tag = sys.argv[1]
for story_id in sys.argv[2:]:
    deliver_story(story_id, tag)

