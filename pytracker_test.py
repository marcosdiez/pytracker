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
 
"""Tests for pytracker.""" 
 
__author__ = 'dcoker@google.com (Doug Coker)' 
 
import unittest 
import pytracker 
 
class StoryTest(unittest.TestCase): 
    STORY_A = """ 
        <story> 
            <id type="integer">129150</id> 
            <story_type>release</story_type> 
            <url>http://tracker/story/show/129150</url> 
            <current_state>unstarted</current_state> 
            <description></description> 
            <name>last frontend push before Google IO</name> 
            <requested_by>Gorbachev</requested_by> 
            <owned_by>Stalin</owned_by> 
            <created_at type="datetime">2009/04/17 00:47:50 GMT</created_at>
            <updated_at type="datetime">2009/04/22 20:46:56 UTC</updated_at> 
            <deadline type="datetime">2009/05/21 19:00:00 GMT</deadline>
            <iteration> 
                <number>5</number> 
                <start type="datetime">2009/05/26 00:00:04 GMT</start> 
                <finish type="datetime">2009/06/09 00:00:04 GMT</finish> 
            </iteration> 
        </story> 
    """ 
 
    def testFromXmlA(self): 
        s = pytracker.Story.FromXml(self.STORY_A) 
        self.assertEquals(129150, s.GetStoryId()) 
        self.assertEquals('release', s.GetStoryType()) 
        self.assertEquals('http://tracker/story/show/129150', s.GetUrl()) 
        self.assertEquals('unstarted', s.GetCurrentState()) 
        self.assertEquals('', s.GetDescription()) 
        self.assertEquals('Gorbachev', s.GetRequestedBy()) 
        self.assertEquals('Stalin', s.GetOwnedBy()) 
        self.assertEquals(1239929270, s.GetCreatedAt()) 
        self.assertEquals(1242932400, s.GetDeadline()) 
        self.assertEquals(5, s.GetIteration()) 
 
    STORY_B = """ 
        <story> 
            <id type="integer">129150</id> 
            <story_type>release</story_type> 
            <url>http://tracker/story/show/129150</url> 
            <current_state>unstarted</current_state> 
            <name>last frontend push before Google IO</name> 
            <requested_by>Gorbachev</requested_by> 
            <created_at type="datetime">2009/04/17 00:47:50 GMT</created_at> 
            <deadline type="datetime">2009/05/21 19:00:00 GMT</deadline> 
            <iteration> 
                <number>5</number> 
                <start type="datetime">2009/05/26 00:00:04 GMT</start> 
                <finish type="datetime">2009/06/09 00:00:04 GMT</finish> 
            </iteration> 
        </story> 
    """ 
 
    def testFromXmlB(self): 
        s = pytracker.Story.FromXml(self.STORY_B) 
        self.assertEquals(129150, s.GetStoryId()) 
        self.assertEquals('release', s.GetStoryType()) 
        self.assertEquals('http://tracker/story/show/129150', s.GetUrl()) 
        self.assertEquals('unstarted', s.GetCurrentState()) 
        # missing fields default to None, but distinguished from empty string! 
        self.assertEquals(None, s.GetDescription()) 
        self.assertEquals('Gorbachev', s.GetRequestedBy()) 
        self.assertEquals(None, s.GetOwnedBy()) 
        self.assertEquals(1239929270, s.GetCreatedAt()) 
        self.assertEquals(1242932400, s.GetDeadline()) 
        self.assertEquals(5, s.GetIteration()) 
 
    STORY_C = """ 
            <story> 
                <id type="integer">1234</id> 
                <story_type>bug</story_type> 
                <url>http://www.pivotaltracker.com/story/show/1234</url> 
                <estimate type="integer">-1</estimate> 
                <current_state>started</current_state> 
                <description>Now, Scotty!</description> 
                <name>More power to shields</name> 
                <requested_by>James Kirk</requested_by> 
                <owned_by>Montgomery Scott</owned_by> 
                <created_at type="datetime">2008/12/10 00:00:00 UTC</created_at> 
                <accepted_at type="datetime">2008/12/10 00:00:00 UTC</accepted_at> 
                <iteration> 
                    <number>3</number> 
                    <start type="datetime">2009/01/05 00:00:02 UTC</start> 
                    <finish type="datetime">2009/01/19 00:00:02 UTC</finish> 
                </iteration> 
                <labels>label 1,label 2,label 3</labels> 
            </story> 
     """ 
 
    def testFromXmlC(self): 
        s = pytracker.Story.FromXml(self.STORY_C) 
        self.assertEquals(1234, s.GetStoryId()) 
        self.assertEquals('bug', s.GetStoryType()) 
        self.assertEquals('http://www.pivotaltracker.com/story/show/1234', 
                                            s.GetUrl()) 
        self.assertEquals('started', s.GetCurrentState()) 
        self.assertEquals('Now, Scotty!', s.GetDescription()) 
        self.assertEquals('More power to shields', s.GetName()) 
        self.assertEquals('James Kirk', s.GetRequestedBy()) 
        self.assertEquals('Montgomery Scott', s.GetOwnedBy()) 
        self.assertEquals(1228867200, s.GetCreatedAt()) 
        self.assertEquals(None, s.GetDeadline()) 
        self.assertEquals(3, s.GetIteration()) 
        self.assertEquals('label 1,label 2,label 3', s.GetLabelsAsString()) 
 
    def testAddLabels(self): 
        s = pytracker.Story.FromXml(self.STORY_A) 
        self.assertEquals(None, s.GetLabelsAsString())    # no labels initially 
        s.AddLabel('bbq') 
        self.assertEquals('bbq', s.GetLabelsAsString()) 
        s.AddLabel('alpha') 
        self.assertEquals('alpha,bbq', s.GetLabelsAsString()) 
 
    def testAddRemoveLabels(self): 
        s = pytracker.Story.FromXml(self.STORY_C) 
        self.assertEquals('label 1,label 2,label 3', s.GetLabelsAsString()) 
        s.RemoveLabel('label 1') 
        self.assertEquals('label 2,label 3', s.GetLabelsAsString()) 
        s.AddLabel('label 1') 
        self.assertEquals('label 1,label 2,label 3', s.GetLabelsAsString()) 
        s.RemoveLabel('label 1') 
        self.assertEquals('label 2,label 3', s.GetLabelsAsString()) 
        s.RemoveLabel('label 2') 
        self.assertEquals('label 3', s.GetLabelsAsString()) 
        s.RemoveLabel('label 3') 
        self.assertEquals('', s.GetLabelsAsString()) 
        s.RemoveLabel('label 4')    # removing nonexistant labels is OK! 
        self.assertEquals('', s.GetLabelsAsString()) 
 
    EMPTY_STORY = b"""<?xml version="1.0" encoding="utf-8"?><story/>""" 
 
    def testNewStory(self): 
        s = pytracker.Story() 
        self.assertEquals(self.EMPTY_STORY, s.ToXml()) 
 
        s.AddLabel('red') 
        self.assertEquals( 
                b"""<?xml version="1.0" encoding="utf-8"?><story>""" 
                b"""<labels>red</labels></story>""", s.ToXml()) 
 
        s.AddLabel('green') 
        self.assertEquals( 
                b"""<?xml version="1.0" encoding="utf-8"?><story>""" 
                b"""<labels>green,red</labels></story>""", s.ToXml()) 
 
        s.SetEstimate(3) 
        self.assertEquals( 
                b"""<?xml version="1.0" encoding="utf-8"?><story>""" 
                b"""<estimate>3</estimate><labels>green,red</labels></story>""", 
                s.ToXml()) 
 
    def testSetDescription(self): 
        story = pytracker.Story() 
        story.SetDescription('day after day the sun') 
        self.assertEquals('day after day the sun', story.GetDescription()) 
        story.SetDescription('') 
        self.assertEquals('', story.GetDescription()) 
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><story><description></description></story>', 
                                            story.ToXml()) 
 
    def testSetOwnedBy(self): 
        story = pytracker.Story() 
        story.SetOwnedBy('dcoker') 
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><story><owned_by>dcoker</owned_by></story>', 
                                            story.ToXml()) 
 
    def testSetReportedBy(self): 
        story = pytracker.Story() 
        story.SetRequestedBy('dcoker') 
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><story><requested_by>dcoker</requested_by></story>', 
                                            story.ToXml()) 
 
    def testSetDeadline(self): 
        story = pytracker.Story() 
        story.SetDeadline(1290153802.0) 
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><story><deadline type="datetime">2010/11/19 08:03:22 UTC</deadline></story>', 
                                            story.ToXml()) 
 
    def testSetCreatedAt(self): 
        story = pytracker.Story() 
        story.SetCreatedAt(1290153802.0) 
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><story><created_at type="datetime">2010/11/19 08:03:22 UTC</created_at></story>', 
                                            story.ToXml())
        
    def testAddTask(self):
        story = pytracker.Story()
        self.assertEquals([], story.tasks)
        task = dict(description="simple task", complete=False, id=None)
        story.AddTask(task)
        task = story.GetTask()
        self.assertEquals("simple task", task['description'])
        
    def testCanGetListOfTasks(self):
        story = pytracker.Story()
        story.AddTask(dict(description="simple task", complete=False, id=None))
        story.AddTask(dict(description="simple task", complete=False, id=None))
        self.assertEqual(2, len(story.GetTasks()))
        
    def testUpdateTask(self):
        story = pytracker.Story()
        self.assertEquals([], story.tasks)
        task = dict(description="simple task", complete=False, id=None)
        story.AddTask(task)
        task = story.GetTask()
        task['description'] = "new description"
        updatedTask = story.GetTask()
        self.assertEquals("new description", updatedTask['description'])
        
    STORY_D = """ 
        <story> 
            <id type="integer">129150</id> 
            <story_type>release</story_type> 
            <url>http://tracker/story/show/129150</url> 
            <current_state>unstarted</current_state> 
            <description></description> 
            <name>last frontend push before Google IO</name> 
            <requested_by>Gorbachev</requested_by> 
            <owned_by>Stalin</owned_by> 
            <created_at type="datetime">2009/04/17 00:47:50 GMT</created_at> 
            <tasks type="array">
                <task>
                    <id type="integer">3486391</id>
                    <description>simple task</description>
                    <position type="integer">1</position>
                    <complete type="boolean">true</complete>
                    <created_at type="datetime">2011/09/17 21:48:42 UTC</created_at>
                </task>
                <task>
                    <id type="integer">3486392</id>
                    <description>simple task2</description>
                    <position type="integer">2</position>
                    <complete type="boolean">false</complete>
                    <created_at type="datetime">2011/09/17 21:49:42 UTC</created_at>
                </task>
            </tasks>
            <deadline type="datetime">2009/05/21 19:00:00 GMT</deadline> 
            <iteration> 
                <number>5</number> 
                <start type="datetime">2009/05/26 00:00:04 GMT</start> 
                <finish type="datetime">2009/06/09 00:00:04 GMT</finish> 
            </iteration> 
        </story> 
    """

    def testFromXmlD(self):
        s = pytracker.Story.FromXml(self.STORY_D) 
        self.assertEquals(129150, s.GetStoryId()) 
        self.assertEquals('release', s.GetStoryType()) 
        self.assertEquals('http://tracker/story/show/129150', s.GetUrl()) 
        self.assertEquals('unstarted', s.GetCurrentState()) 
        self.assertEquals('', s.GetDescription()) 
        self.assertEquals('Gorbachev', s.GetRequestedBy()) 
        self.assertEquals('Stalin', s.GetOwnedBy())
        self.assertEquals("simple task", s.GetTask()['description'])
        self.assertEquals("simple task2", s.GetTask(1)['description'])
        self.assertEquals(False, s.GetTask(1)['complete'])
    
    STORY_E = """ 
        <story> 
            <id type="integer">129150</id> 
            <story_type>release</story_type> 
            <url>http://tracker/story/show/129150</url> 
            <current_state>unstarted</current_state> 
            <description></description> 
            <name>last frontend push before Google IO</name> 
            <requested_by>Gorbachev</requested_by> 
            <owned_by>Stalin</owned_by> 
            <created_at type="datetime">2009/04/17 00:47:50 GMT</created_at>
            <updated_at type="datetime">2009/04/22 20:46:56 UTC</updated_at> 
            <deadline type="datetime">2009/05/21 19:00:00 GMT</deadline>
            <iteration> 
                <number>5</number> 
                <start type="datetime">2009/05/26 00:00:04 GMT</start> 
                <finish type="datetime">2009/06/09 00:00:04 GMT</finish> 
            </iteration> 
        </story> 
    """     
    
    def testCanGetUpdatedAtDate(self):
        s = pytracker.Story.FromXml(self.STORY_E) 
        self.assertEquals(1240433216, s.GetUpdatedAt())
        
    STORY_F = """ 
        <story> 
            <id type="integer">129150</id> 
            <story_type>release</story_type> 
            <url>http://tracker/story/show/129150</url> 
            <current_state>unstarted</current_state> 
            <description></description> 
            <name>last frontend push before Google IO</name> 
            <requested_by>Gorbachev</requested_by> 
            <owned_by>Stalin</owned_by> 
            <created_at type="datetime">2009/04/17 00:47:50 GMT</created_at>
            <updated_at type="datetime">2009/04/22 20:46:56 UTC</updated_at> 
            <deadline type="datetime">2009/05/21 19:00:00 GMT</deadline>
            <jira_id>TEST-1280</jira_id>
            <jira_url>https://www.jira.com:1234/browse/TEST-1280</jira_url> 
            <iteration> 
                <number>5</number> 
                <start type="datetime">2009/05/26 00:00:04 GMT</start> 
                <finish type="datetime">2009/06/09 00:00:04 GMT</finish> 
            </iteration> 
        </story> 
    """ 
        
    def testCanGetJiraFields(self):
        s = pytracker.Story.FromXml(self.STORY_F) 
        self.assertEquals("https://www.jira.com:1234/browse/TEST-1280", s.GetJiraUrl())
        
    def testCanGetJiraKey(self):
        s = pytracker.Story.FromXml(self.STORY_F) 
        self.assertEquals("TEST-1280", s.GetJiraKey())

        
class TaskTest(unittest.TestCase):
    def testCanAddTask(self):
        t = pytracker.Task()
        t.SetDescription("simple task")
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><task><description>simple task</description><complete type="boolean">false</complete></task>', t.ToXml())
        self.assertEquals("/tasks", t.GetSubPath())
        self.assertEquals("POST", t.GetMethod())
#    curl -H "X-TrackerToken: $TOKEN" -X POST -H "Content-type: application/xml" \
#    -d "<task><description>clean shields</description></task>" \
#    http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks
        pass

    def testCanUpdateTask(self):
        t = pytracker.Task.FromDictionary(dict(description="sample description", complete=False, id=12345))
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><task><description>sample description</description><complete type="boolean">false</complete></task>', t.ToXml())
        t.SetComplete()
        self.assertEquals(b'<?xml version="1.0" encoding="utf-8"?><task><description>sample description</description><complete type="boolean">true</complete></task>', t.ToXml())
        self.assertEquals("/tasks/12345", t.GetSubPath())
        self.assertEquals("PUT", t.GetMethod())
#  curl -H "X-TrackerToken: $TOKEN" -X PUT -H "Content-type: application/xml" \
#    -d "<task><description>count shields</description><complete>true</complete></task>" \
#    http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks/$TASK_ID
        pass  

#    def testCanDeleteTask(self):
## curl -H "X-TrackerToken: $TOKEN" -X DELETE http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks/$TASK_ID
#        pass

class ExistingCommentsTest(unittest.TestCase):
    def testCanGetCommentsFromXml(self):
        xmlWithComments = '<?xml version="1.0" encoding="UTF-8"?><notes type="array"><note><id type="integer">21913487</id><text>comment1</text><author>lwoydziak</author><noted_at type="datetime">2012/04/27 19:44:46 UTC</noted_at></note><note><id type="integer">21913497</id><text>comment2</text><author>lwoydziak</author><noted_at type="datetime">2012/04/27 19:44:54 UTC</noted_at></note></notes>'
        comments = pytracker.Comment.ExtractAllFromXml(xmlWithComments)
        self.assertEqual(comments[0].GetText(), "comment1")
        self.assertEqual(comments[0].GetId(), 21913487)
        self.assertEqual(comments[0].GetAuthor(), "lwoydziak")
        self.assertEqual(comments[0].GetTime(), 1335555886)
        self.assertEqual(comments[1].GetText(), "comment2")
        pass  

if __name__ == '__main__': 
    unittest.main() 
