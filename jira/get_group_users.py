from jira import JIRA
import sys
import os

(_, group) = sys.argv

with open(os.path.expanduser("~/.jira"), "r") as f:
    (u, p) = f.readline().strip("\n").split(" ")

api = JIRA("https://tools.crowdtwist.com/issues", basic_auth=(u, p))

users = api.group_members(group)
users = [k for k,v in users.iteritems() if v['active']]

with open("%s" % os.path.join(os.getcwd(), group), "w") as f:
    f.writelines("\n".join(users))

print "group: '%s' - %s users written in %s/jira-users.txt" % (group,
                                                               len(users),
                                                               os.getcwd())
