#!/usr/bin/env python
#
# Copyright 2009 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""pytracker is a Python wrapper around the Tracker API."""

__author__ = 'dcoker@google.com (Doug Coker)'

import calendar
import http.cookiejar
import re
import time
import urllib.request, urllib.parse, urllib.error
import xml.dom
from xml.dom import minidom
import xml.parsers.expat
import xml.sax.saxutils
import json

DEFAULT_BASE_API_URL = 'https://www.pivotaltracker.com/services/v3/'
# Some fields specify UTC, some GMT?
_TRACKER_DATETIME_RE = re.compile(r'^\d{4}/\d{2}/\d{2} .*(GMT|UTC)$')


def TrackerDatetimeToYMD(pdt):
    assert _TRACKER_DATETIME_RE.match(pdt)
    pdt = pdt.split()[0]
    pdt = pdt.replace('/', '-')
    return pdt


class Tracker(object):
    """Tracker API."""

    def __init__(self, project_id, token,
                             base_api_url=DEFAULT_BASE_API_URL):
        """Constructor.

        If you are debugging API calls, you may want to use a non-HTTPS API URL:
            base_api_url="http://www.pivotaltracker.com/services/v3/"

        Args:
            project_id: the Tracker ID (integer).
            auth: a TrackerAuth instance.
            base_api_url: the base URL of the HTTP API (with trailing /).
        """
        self.project_id = project_id
        self.base_api_url = base_api_url

        cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))

        self.token = token

    def _Api(self, request, method, body=None):
        url = self.base_api_url + 'projects/%d/%s' % (self.project_id, request)
        headers = {}
        if self.token:
            headers['X-TrackerToken'] = self.token

        if not body and method == 'GET':
            # Do a GET
            req = urllib.request.Request(url, None, headers)
        else:
            headers['Content-Type'] = 'application/xml'
            req = urllib.request.Request(url, body, headers)
            req.get_method = lambda: method

        try:
            res = self.opener.open(req)
        except urllib.error.HTTPError as e:
            message = "HTTP Status Code: %s\nMessage: %s\nURL: %s\nError: %s" % (e.code, e.msg, e.geturl(), e.read())
            raise TrackerApiException(message)

        return res.read()

    def _ApiQueryStories(self, query=None):
        if query:
            output = self._Api('stories?filter=' + urllib.parse.quote_plus(query),
                                                 'GET')
        else:
            output = self._Api('stories', 'GET')

        # Hack: throw an exception if we didn't get valid XML.
        xml.parsers.expat.ParserCreate('utf-8').Parse(output, True)

        return output

    def GetStoriesXml(self):
        return self._ApiQueryStories()

    def GetReleaseStoriesXml(self):
        return self._ApiQueryStories('type:release')


    def GetIterationStories(self, iteration=None, offset=None, limit=None):
        iteration = ('/%s' % iteration) if iteration else ''
        params = []
        if offset:
            params.append('offset=%s' % urllib.quote_plus(str(offset)))
        if limit:
            params.append('limit=%s' % urllib.quote_plus(str(limit)))

        response = self._Api('iterations%s?%s' % (iteration, '&'.join(params)), 'GET')

        # Hack: throw an exception if we didn't get valid XML.
        xml.parsers.expat.ParserCreate('utf-8').Parse(response, True)

        parsed = xml.dom.minidom.parseString(response)
        els = parsed.getElementsByTagName('story')
        lst = []
        for el in els:
            lst.append(Story.FromXml(el.toxml()))
        return lst


    def GetStories(self, filt=None):
        """Fetch all Stories that satisfy the filter.

        Args:
            filt: a Tracker search filter.
        Returns:
            List of Story().
        """
        stories = self._ApiQueryStories(filt)
        parsed = xml.dom.minidom.parseString(stories)
        els = parsed.getElementsByTagName('story')
        lst = []
        for el in els:
            lst.append(Story.FromXml(el.toxml()))
        return lst

    def _parse_story_id(self, story_id):
      #story id can be an integer, an integer disguised as a string or
      # "https://www.pivotaltracker.com/story/show/46440725" or
      # "https://www.pivotaltracker.com/projects/227033#!/stories/44107229"
        if story_id.__class__ == int:
          return story_id
        temp = re.findall("\d+", story_id)
        if temp is not None:
          return int(temp[-1])
        raise ValueError("Can't get story_id from [{}]".format(story_id))

    def GetStory(self, story_id):
        story_id = self._parse_story_id(story_id)
        story_xml = self._Api('stories/%d' % story_id, 'GET')

        return Story.FromXml(story_xml.decode())

    def AddComment(self, story_id, comment):
        if story_id is None:
            return
        comment_post_body = '<note><text>%s</text></note>' % xml.sax.saxutils.escape(comment)
        self._Api('stories/%d/notes' % story_id, 'POST', comment_post_body.encode())

    def GetComments(self, story_id):
        comments_xml = self._Api('stories/%d/notes' % story_id, 'GET')
        return Comment.ExtractAllFromXml(comments_xml)

    def AddNewStory(self, story):
        """Persists a new story to Tracker and returns the new Story."""
        story_xml = story.ToXml()
        res = self._Api('stories', 'POST', story_xml)
        toAddStory = story
        story = Story.FromXml(res)

        if len(toAddStory.GetTasks()) < 1:
            return story

        for task in toAddStory.GetTasks():
            path = 'stories/%d' % story.GetStoryId()
            path += task.GetSubPath()
            res = self._Api(path, task.GetMethod(), task.ToXml())

        return self.GetStory(story.GetStoryId())

    def UpdateStoryById(self, story_id, story):
        """Persist changes to an existing story to Tracker.

        Use this method if you are changing a story without first retreiving the
        story.

        Args:
            story_id: The ID of the story to mutate
            story: The Story containing values to change.
        Returns:
            The updated Story().
        """
        if story_id is None:
            return None
        story_xml = story.ToXml()
        res = self._Api('stories/%d' % story_id, 'PUT', story_xml)
        return Story.FromXml(res)

    def UpdateStory(self, story):
        """Persists changes to an existing story to Tracker.

        Use this method if you have a full Story object created by one of the query
        methods.

        Args:
            story: a Story()
        Returns:
            The updated Story().
        """
        if story.GetStoryId() is None:
            return None
        story_xml = story.ToXml()
        res = self._Api('stories/%d' % story.GetStoryId(), 'PUT', story_xml)

        if len(story.GetTasks()) < 1:
            return Story.FromXml(res.decode())

        for task in story.GetTasks():
            path = 'stories/%d' % story.GetStoryId()
            path += task.GetSubPath()
            res = self._Api(path, task.GetMethod(), task.ToXml())

        return self.GetStory(story.GetStoryId())

    def DeleteStory(self, story_id):
        """Deletes a story by story ID."""
        self._Api('stories/%d' % story_id, 'DELETE', b"")


class TrackerAuth(object):
    """Abstract base class for establishing credentials for pytracker."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def EstablishAuthToken(self, opener):
        """Returns the value for use as the X-TrackerToken HTTP header, or None.

        This method may mutate the cookie jar via opener.

        Args:
            opener: a urllib2.OpenerDirector instance that will be used for
                            subsequent HTTP API calls.
        """
        raise NotImplementedError()


class TrackerAuthException(Exception):
    """Raised when something goes wrong with authentication."""


class NoTokensAvailableException(Exception):
    """Raised when HostedTrackerAuth can't find any tokens for this user."""


class TrackerApiException(Exception):
    """Raised when Tracker returns an error."""


class HostedTrackerAuth(TrackerAuth):
    """Authentication rules for hosted Tracker instances."""

    def EstablishAuthToken(self, opener):
        """Returns the first auth token returned by /services/tokens/active."""
        url = 'https://www.pivotaltracker.com/services/v3/tokens/active'
        data = urllib.parse.urlencode((('username', self.username),
                                                         ('password', self.password)))
        try:
            req = opener.open(url, data.encode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise NoTokensAvailableException(
                        'Did you create any?    Check https://www.pivotaltracker.com/profile')
            else:
                raise

        res = req.read()

        dom = minidom.parseString(res)
        token = dom.getElementsByTagName('guid')[0].firstChild.data

        return token

class XmlDocument(object):
    @staticmethod
    def GetTagListForTag(dom, tag):
        """Retrieve value associated with the tag, if any.

        Args:
            dom: XML DOM object
            parentTag: name of parent for the desired tag

        Returns:
            None (if tag doesn't exist), empty string (if tag exists, but body is
            empty), or array of data.
        """
        tags = dom.getElementsByTagName(tag)
        if not tags:
            return None
        return tags

    @staticmethod
    def GetDataFromTag(dom, tag):
        """Retrieve value associated with the tag, if any.

        Args:
            dom: XML DOM object
            tag: name of the desired tag

        Returns:
            None (if tag doesn't exist), empty string (if tag exists, but body is
            empty), or the tag body.
        """
        tags = dom.getElementsByTagName(tag)
        if not tags:
            return None
        elif tags[0].hasChildNodes():
            return tags[0].firstChild.data
        else:
            return ''

    @staticmethod
    def ParseDatetimeIntoSecs(dom, tag):
        """Returns the tag body parsed into seconds-since-epoch."""
        el = dom.getElementsByTagName(tag)
        if not el:
            return None
        assert el[0].getAttribute('type') == 'datetime'
        data = el[0].firstChild.data

        # Tracker emits datetime strings in UTC or GMT.
        # The [:-4] strips the timezone indicator
        parsable_date=("{}".format(data[:-4])).strip()
        when = time.strptime(parsable_date, '%Y/%m/%d %H:%M:%S')
        # calendar.timegm treats the tuple as GMT
        return calendar.timegm(when)

class XmlNodeList(object):
    @staticmethod
    def toInt(nodelist):
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                return int(node.data)
            if node.nodeType == node.ELEMENT_NODE:
                return XmlNodeList.toInt(node.childNodes)
        return None

    @staticmethod
    def toBool(nodelist):
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                if node.data == "true":
                    return True
            if node.nodeType == node.ELEMENT_NODE:
                return XmlNodeList.toBool(node.childNodes)
        return False

    @staticmethod
    def toText(nodelist):
        strings = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                strings.append(node.data)
            if node.nodeType == node.ELEMENT_NODE:
                strings.append(XmlNodeList.toText(node.childNodes))
        return ''.join(strings)

    @staticmethod
    def toSeconds(nodelist):
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                when = time.strptime(node.data[:-4], '%Y/%m/%d %H:%M:%S')
                return calendar.timegm(when)
            if node.nodeType == node.ELEMENT_NODE:
                return XmlNodeList.toSeconds(node.childNodes)
        return None


class Story(object):
    """Represents a Story.

    This class can be used to represent a complete Story (generally queried from
    the Tracker class), or can contain partial information for update or create
    operations (constructed with default constructor).

    Internally, Story uses None to indicate that the client has not specified a
    value for the field or that it has not been parsed from XML.    This enables us
    to use the same Story object to define an update to multiple stories, without
    requiring that the client first fetch, parse, and update an existing story.
    This is supported by all mutable fields except for labels, which are
    represented by Tracker as a comma-separated list of strings in a single tag
    body.    For label operations on existing stories to be performed correctly,
    the Story must first be fetched from the server so that the existing labels
    are not lost.

    This method has the problem of setting unecessary triggers. Every time we add
    a label to a story, the person on 'owned_by' receives an email.
    So we must use updated_fields as well.

    """
    # Fields that can be treated as strings when embedding in XML.
    UPDATE_FIELDS = ('story_type', 'current_state', 'name',
                                     'description', 'estimate', 'requested_by', 'owned_by')

    CSV_FIELDS = ["story_id" , "labels", "story_type", "estimate", "zendesk_id", "name", "description"]

    updated_fields = []

    # Type: immutable ints.
    story_id = None
    iteration_number = None

    # Type: immutable times (secs since epoch)
    created_at = None
    updated_at = None

    # Type: mutable time (secs since epoch)
    deadline = None

    # Type: mutable set (API methods expose as string)
    labels = None

    # Type: immutable strings
    url = None

    # Type: mutable strings
    requested_by = None
    owned_by = None
    story_type = None
    current_state = None
    description = None
    name = None
    estimate = None
    jira_url = None
    jira_id = None
    zendesk_url = None
    zendesk_id = None

    # tasks are not mutable
    tasks = []

    def __str__(self):
        return "Story(%r)" % self.__dict__

    def _add_to_updated_fields(self, field_name):
        if field_name not in self.updated_fields:
            self.updated_fields.append(field_name)


    @staticmethod
    def FromJson(as_json):
        """Parses an JSON string into a Story.

        Args:
            as_json: a full JSON document from Story.ToJSon().
        Returns:
            Story()
        """
        parsed = json.loads(as_json)
        parsed["labels"] = set(parsed["labels"]) # it comes as list in JSON
        story = Story()
        story.__dict__ = parsed
        return story




    @staticmethod
    def FromXml(as_xml):
        """Parses an XML string into a Story.

        Args:
            as_xml: a full XML document from the Tracker API.
        Returns:
            Story()
        """
        parsed = minidom.parseString(as_xml)
        story = Story()
        story.story_id = int(parsed.getElementsByTagName('id')[0].firstChild.data)
        story.url = parsed.getElementsByTagName('url')[0].firstChild.data
        story.owned_by = XmlDocument.GetDataFromTag(parsed, 'owned_by')
        story.created_at = XmlDocument.ParseDatetimeIntoSecs(parsed, 'created_at')
        story.updated_at = XmlDocument.ParseDatetimeIntoSecs(parsed, 'updated_at')
        story.requested_by = XmlDocument.GetDataFromTag(parsed, 'requested_by')
        iteration = XmlDocument.GetDataFromTag(parsed, 'number')
        story.jira_url = XmlDocument.GetDataFromTag(parsed, 'jira_url')
        story.jira_id = XmlDocument.GetDataFromTag(parsed, 'jira_id')
        story.zendesk_url = XmlDocument.GetDataFromTag(parsed, 'zendesk_url')
        story.zendesk_id = XmlDocument.GetDataFromTag(parsed, 'zendesk_id')

        if iteration:
            story.iteration_number = int(iteration)

        tasks = XmlDocument.GetTagListForTag(parsed, "task")
        if tasks is not None:
            story.tasks = []
            for task in tasks:
                storyTaskDictionary = dict(description=None, complete=False, id=None)
                storyTaskDictionary['description'] = XmlNodeList.toText(task.getElementsByTagName("description"))
                storyTaskDictionary['complete'] = XmlNodeList.toBool(task.getElementsByTagName('complete'))
                storyTaskDictionary['id'] = XmlNodeList.toText(task.getElementsByTagName("id"))
                story.tasks.append(Task.FromDictionary(storyTaskDictionary))

        story.SetStoryType(
                parsed.getElementsByTagName('story_type')[0].firstChild.data)
        story.SetCurrentState(
                parsed.getElementsByTagName('current_state')[0].firstChild.data)
        story.SetName(XmlDocument.GetDataFromTag(parsed, 'name'))
        story.SetDescription(XmlDocument.GetDataFromTag(parsed, 'description'))
        story.SetDeadline(XmlDocument.ParseDatetimeIntoSecs(parsed, 'deadline'))

        estimate = XmlDocument.GetDataFromTag(parsed, 'estimate')
        if estimate is not None:
                story.estimate = estimate
        labels = XmlDocument.GetDataFromTag(parsed, 'labels')
        if labels is not None:
            story.AddLabelsFromString(labels)

        story.ClearUpdatedFields()
        return story

    def ClearUpdatedFields(self):
        self.updated_fields = []

    # Immutable fields
    def GetStoryId(self):
        return self.story_id

    def GetIteration(self):
        return self.iteration_number

    def GetUrl(self):
        return self.url

    # Mutable fields
    def GetRequestedBy(self):
        return self.requested_by

    def SetRequestedBy(self, requested_by):
        self._add_to_updated_fields("requested_by")
        self.requested_by = requested_by

    def GetOwnedBy(self):
        return self.owned_by

    def GetTask(self, which=0):
        return self.tasks[which].GetDictionary()

    def GetTasks(self):
        return self.tasks

    def AddTask(self, task):
        self.tasks = self.tasks or [] # tasks can be None so use existing array or create one
        if not isinstance(task, Task):
            task = Task.FromDictionary(task)
        self.tasks.append(task)

    def SetOwnedBy(self, owned_by):
        self._add_to_updated_fields("owned_by")
        self.owned_by = owned_by

    def GetStoryType(self):
        return self.story_type

    def SetStoryType(self, story_type):
        assert story_type in ['bug', 'chore', 'release', 'feature']
        self._add_to_updated_fields("story_type")
        self.story_type = story_type

    def GetCurrentState(self):
        return self.current_state

    def SetCurrentState(self, current_state):
        self._add_to_updated_fields("current_state")
        self.current_state = current_state

    def GetName(self):
        return self.name

    def SetName(self, name):
        self._add_to_updated_fields("name")
        self.name = name

    def GetEstimate(self):
        return self.estimate

    def SetEstimate(self, estimate):
        self._add_to_updated_fields("estimate")
        self.estimate = estimate

    def GetDescription(self):
        return self.description

    def SetDescription(self, description):
        self._add_to_updated_fields("description")
        self.description = description

    def GetDeadline(self):
        return self.deadline

    def SetDeadline(self, secs_since_epoch):
        self.deadline = secs_since_epoch

    def GetCreatedAt(self):
        return self.created_at

    def SetCreatedAt(self, secs_since_epoch):
        self._add_to_updated_fields("created_at")
        self.created_at = secs_since_epoch

    def GetUpdatedAt(self):
        return self.updated_at

    def SetUpdatedAt(self, secs_since_epoch):
        self.updated_at = secs_since_epoch

    def SetJiraUrl(self, url):
        self.jira_url = url

    def GetJiraUrl(self):
        return self.jira_url

    def SetJiraKey(self, key):
        self.jira_id = key

    def GetJiraKey(self):
        return self.jira_id

    def SetZendeskUrl(self, url):
        self.zendesk_url = url

    def GetZendeskUrl(self):
        return self.zendesk_url

    def SetZendeskKey(self, key):
        self.zendesk_id = key

    def GetZendeskKey(self):
        return self.zendesk_id

    def AddLabel(self, label):
        """Adds a label (see caveat in class comment)."""
        if self.labels is None:
            self.labels = set()
        self.labels.add(label)

    def RemoveLabel(self, label):
        """Removes a label (see caveat in class comment)."""
        if self.labels is None:
            self.labels = set()
        else:
            try:
                self.labels.remove(label)
            except KeyError:
                pass

    def AddLabelsFromString(self, labels):
        """Adds a set of labels from a comma-delimited string (see class caveat)."""
        if self.labels is None:
            self.labels = set()

        self.labels = self.labels.union([x.strip() for x in labels.split(',')])

    def GetLabelsAsString(self):
        """Returns the labels as a comma delimited list of strings."""
        if self.labels is None:
            return None
        lst = list(self.labels)
        lst.sort()
        return ','.join(lst)


    @staticmethod
    def CsvHeader():
        output = "{}".format(Story.CSV_FIELDS).replace("[","").replace("]","").replace(" ","").replace("'","")
        return output

    def ToCsv(self):
        """Converts this Story to a CSV string."""

        def csv_helper(the_dict, the_field):
            if the_field not in the_dict:
                return ""
            value = the_dict[the_field]
            if value is None:
                return ""
            if isinstance(value, set):
                value = "{}".format(value)
                #yes, I want to fallback to the previous case


            if isinstance(value, str):
                value = value.replace("\"","\"\"")
                value = value.replace("\r","")
                #value = value.replace("\n","\\n")
                return "\"{}\"".format(value)
            return value

        output = ""
        first = True
        for one_field in self.CSV_FIELDS:
            if first:
                first = False
                template = "{}{}"
            else:
                template = "{},{}"
            output = template.format(output, csv_helper(self.__dict__, one_field))
        return output

    def ToJson(self):
        """Converts this Story to a JSON string."""
        labels_backup = self.labels
        self.labels = list(self.labels)
        output =  json.dumps(self.__dict__, sort_keys=True, indent=4)
        self.labels = labels_backup
        return output


    def ToXml(self):
        """Converts this Story to an XML string."""
        doc = xml.dom.getDOMImplementation().createDocument(None, 'story', None)
        story = doc.getElementsByTagName('story')[0]

        # Most fields are just simple strings or ints, so we treat them all in the
        # same way.
        for field_name in self.UPDATE_FIELDS:
            if field_name not in self.updated_fields:
                continue
            v = getattr(self, field_name)
            if v is not None:
                new_tag = doc.createElement(field_name)
                new_tag.appendChild(doc.createTextNode(str(v)))
                story.appendChild(new_tag)

        # Labels are represented internally as sets.
        if self.labels is not None:
            labels_tag = doc.createElement('labels')
            labels_tag.appendChild(doc.createTextNode(self.GetLabelsAsString()))
            story.appendChild(labels_tag)

        # Dates are special
        DATE_FORMAT = '%Y/%m/%d %H:%M:%S UTC'

        if self.deadline:
            formatted = time.strftime(DATE_FORMAT, time.gmtime(self.deadline))
            deadline_tag = doc.createElement('deadline')
            deadline_tag.setAttribute('type', 'datetime')
            deadline_tag.appendChild(doc.createTextNode(formatted))
            story.appendChild(deadline_tag)

        if self.created_at and "created_at" in self.updated_fields:
            formatted = time.strftime(DATE_FORMAT, time.gmtime(self.created_at))
            created_at_tag = doc.createElement('created_at')
            created_at_tag.setAttribute('type', 'datetime')
            created_at_tag.appendChild(doc.createTextNode(formatted))
            story.appendChild(created_at_tag)

        #don't update updated_at field as it will autoupdate
        return doc.toxml('utf-8')

class Task(object):
    """Represents a Story Task.

    This class can be used to represent a complete Task as entered inside
    as Story.

    Internally, Task uses None to indicate that the client has not specified a
    value for the field or that it has not been parsed from XML.    This enables us
    to use the same Task object to define an update to multiple Tasks, without
    requiring that the client first fetch, parse, and update an existing task.
    """
    NEW_TASK_METHOD = "POST"
    TASK_PATH = "/tasks"
    UPDATE_TASK_METHOD = "PUT"

    def __init__(self):
        self.descriptor = dict(description='', complete=False, id=None)

    @staticmethod
    def FromDictionary(dictionary):
        task = Task()
        task.descriptor['description'] = dictionary['description']
        task.descriptor['complete'] = dictionary['complete']
        task.descriptor['id'] = dictionary['id']
        return task

    def ToXml(self):
        doc = xml.dom.getDOMImplementation().createDocument(None, 'task', None)
        task = doc.getElementsByTagName('task')[0]
        task_description = doc.createElement('description')
        task_description.appendChild(doc.createTextNode(self.descriptor['description']))
        task.appendChild(task_description)
        task_complete = doc.createElement('complete')
        task_complete.setAttribute('type', 'boolean')
        if self.descriptor['complete']:
            task_complete.appendChild(doc.createTextNode('true'))
        else:
            task_complete.appendChild(doc.createTextNode('false'))
        task.appendChild(task_complete)
        return doc.toxml('utf-8')

    def GetSubPath(self):
        path = self.TASK_PATH
        if self.descriptor['id'] is None:
            return path
        else:
            return path + "/" + str(self.descriptor['id'])

    def GetMethod(self):
        if self.descriptor['id'] is None:
            return self.NEW_TASK_METHOD
        else:
            return self.UPDATE_TASK_METHOD

    def SetComplete(self, complete=True):
        self.descriptor['complete'] = complete

    def SetDescription(self, description):
        self.descriptor['description'] = description

    def GetDictionary(self):
        return self.descriptor

class Comment(object):
    """Represents a comment.

    This class can be used to represent a comment for a Story.

    Internally, Comment uses None to indicate that the client has not specified a
    value for the field or that it has not been parsed from XML.  Comment updating
    not supported yet.
    """
    id = None
    text = ""
    author = ""
    noted_at = None

    def GetId(self):
        return self.id

    def GetText(self):
        return self.text

    def GetAuthor(self):
        return self.author

    def GetTime(self):
        return self.noted_at
    @staticmethod
    def ExtractAllFromXml(as_xml):
        """Parses an XML string into a Comment(s).

        Args:
            as_xml: a full XML document from the Tracker API.
        Returns:
            list of Comment()
        """
        parsed = minidom.parseString(as_xml)
        comments = []
        commentsXml = XmlDocument.GetTagListForTag(parsed, "note")

        if commentsXml is not None:
            for commentXml in commentsXml:
                comment = Comment()
                comment.id = XmlNodeList.toInt(commentXml.getElementsByTagName("id"))
                comment.author = XmlNodeList.toText(commentXml.getElementsByTagName("author"))
                comment.text = XmlNodeList.toText(commentXml.getElementsByTagName("text"))
                comment.noted_at = XmlNodeList.toSeconds(commentXml.getElementsByTagName('noted_at'))
                comments.append(comment)

        return comments
