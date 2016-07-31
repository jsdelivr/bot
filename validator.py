from util import PullValidator, GitMerger

import pystache, yaml

from github3 import login
from github3.pulls import PullRequest

from collections import deque

class PullBot(PullValidator, GitMerger):
    config = yaml.load(open("config.yml"))

    def __init__(self):
        GitMerger.__init__(self)
        PullValidator.__init__(self)

        self.gh = login(self.config["user"], token=self.config["auth_token"])
        self.repo = self.gh.repository(self.config["owner"], self.config["repo"])

    def get_pull(self, pr=None):
        if type(pr) == int:
            return self.repo.pull_request(pr)
        elif type(pr) == PullRequest:
            return pr
        return None

    #validate a pr, pr is an int
    def validate(self, pr=None, debug=False):
        self.repo.refresh()

        pr = self.get_pull(pr)
        if not pr: return False

        issue = self.repo.issue(pr.number)
        last_commit = deque(pr.iter_commits(), maxlen=1).pop()

        self.repo.create_status(sha=last_commit.sha, state="pending")

        status = PullValidator.validate(self, pr, debug)

        if status.warnings or status.ini_issues or status.file_issues or status.version_issues:
            #report them to the cops
            data = {
                "login": pr.user.login,

                "has-ini-issues": status.ini_issues != [],
                "info-issues": status.ini_issues,

                "has-file-issues": status.file_issues != [],
                "file-issues": status.file_issues,

                "has-warnings": status.warnings != [],
                "warnings": status.warnings,

                "has-version-issues": status.version_issues != [],
                "version-issues": status.version_issues,

                "qotd": self.gh.zen()
            }

            with open("templates/pr-issue.tpl") as f:
                issue_template = f.read()
            comments_md = pystache.render(issue_template, data)

            #failure commit status
            files = {"{0}.md".format(pr.number): {"content": comments_md}}
            gist = self.gh.create_gist("Validation of PR #{0} for jsdelivr/jsdelivr".format(pr.number), files=files, public=False)
            state = "error" if status.error_occured else "failure"
            message = "Automatic validation encountered an error" if status.error_occured else "Failed automatic validation"
            self.repo.create_status(sha=last_commit.sha, state=state, target_url=gist.html_url, description=message)

            if (debug):
                print comments_md

            #create a comment if nothings happening
            if not any(c.user.login == self.config["user"] for c in issue.iter_comments()):
                issue.create_comment(comments_md)
        else:
            if (debug == True):
                print 'Validation success'
            #success status and attempt to merge it
            self.repo.create_status(sha=last_commit.sha, state="success", target_url="http://www.lgtm.in/g", description="\"LGTM\" - bot")
            self.merge(pr)

    def is_trusted(self, user):
        return user.login in self.config["trusted_users"]

    def delete_branch(self, pr):
        r = self.gh.repository(*pr.head.repo)
        r.ref('heads/' + pr.head.ref).delete()

    # Automatically close branches on bot pull requests when rejected.
    def closed_pr(self, pr):
        pr = self.get_pull(pr)
        if (self.gh.user() == pr.user):
            self.delete_branch(pr)

    def merge(self, pr):
        # only merge trusted users
        if self.is_trusted(pr.user):
            # Attempt to delete the branch (if the bot has permission for the repo)
            try:
                pr.merge("http://www.lgtm.in/g")
                # Until https://github.com/sigmavirus24/github3.py/pull/351 is sorted out
                self.delete_branch(pr)
            except: pass
