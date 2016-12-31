from jira import JIRA
import sys
import os
from pprint import pprint

(_, assignee) = sys.argv

with open(os.path.expanduser("~/.jira"), "r") as f:
    (u, p) = f.readline().strip("\n").split(" ")

api = JIRA("https://tools.crowdtwist.com/issues", basic_auth=(u, p))


result = api.search_issues("assignee=%s and status = closed and \"Story Points (0,1,2,3,5,8,13,21)\" is not EMPTY" % assignee, maxResults=999)
story_points_field = "customfield_10002"


print "%s, %s, %d" % (assignee, result.total,
                                     sum(getattr(t.fields, story_points_field) for t in result))

