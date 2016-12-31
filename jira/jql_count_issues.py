from jira import JIRA
import os
import sys

(_, assignee, jql) = sys.argv

with open(os.path.expanduser("~/.jira"), "r") as f:
    (u, p) = f.readline().strip("\n").split(" ")

api = JIRA("https://tools.crowdtwist.com/issues", basic_auth=(u, p))

result = api.search_issues("assignee=%s AND %s" % (assignee, jql), maxResults=1)

print "%s, %s" % (assignee, result.total)


