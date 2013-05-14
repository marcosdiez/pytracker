pytracker - Pivotal Tracker Python v3 API
=========================================

This is a clone of http://code.google.com/r/lwoydziak-python3/
which is a clone of http://code.google.com/p/pytracker/

I just added bugfixes :)

marcos AT unitron DOT com DOT br

Examples
--------

### Authenticate

```python
from pytracker import Tracker
from pytracker import Story
from pytracker import HostedTrackerAuth

def main(argv):
  auth = HostedTrackerAuth('username', 'password')
  tracker = Tracker(10101, auth)
```

### Fetch a story

```python
  story = tracker.GetStory(684566)
```

### Create a story

```python
story = Story()
story.SetName('wake up')
story.SetEstimate(1)
tracker.AddNewStory(story)
```
### Update an existing story

```python
story = tracker.GetStory(684566)
story.SetCurrentState('delivered')
tracker.UpdateStory(story)
```
### Add a comment

```python
tracker.AddComment(story_id, 'The customer is always right.')
```

### Add a label

```python
story = tracker.GetStory(44)
story.AddLabel("api")
tracker.UpdateStory(story)
```

### Query with filter

```python
stories = tracker.GetStories('type:release')
```

See Tracker Search Help for query language.
### Apply an update to multiple stories

```python
stories = tracker.GetStories('owner:"party cat"')
changes = Story()
changes.SetOwnedBy('bro')
changes.SetEstimate(8)
for story in stories:
  tracker.UpdateStoryById(story.GetStoryId(), changes)
```

### Delete a story

```python
tracker.DeleteStory(44)
```
