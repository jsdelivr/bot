from util import PullValidator

import pystache, yaml

from github3 import login
from github3.pulls import PullRequest

class PullBot(PullValidator):
    config = yaml.load(open("config.yml"))

    def __init__(self):
        self.gh = login(self.config["user"], token=self.config["auth_token"])
        self.repo = self.gh.repository(self.config["owner"], self.config["repo"])

    def get_pull(self, pr=None):
        if type(pr) == int:
            return self.repo.pull_request(pr)
        elif type(pr) == PullRequest:
            return pr
        return None

    #validate a pr, pr is an int
    def validate(self, pr=None):
        self.repo.refresh()

        pr = self.get_pull(pr)
        if not pr:
            return False

        issue = self.repo.issue(pr.number)
        last_commit = pr.iter_commits().next()

        self.repo.create_status(sha=last_commit.sha, state="pending")

        status = PullValidator.validate(self, pr)

        if status.warnings or status.ini_issues or status.file_issues or status.version_issues: #report them to the cops
            print "PR {0} failed to validate!".format(pr.number)

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

            #debugging
            # with open("result.md", "w") as f:
            #     f.write(comments_md)

            #failure commit status
            files = {"{0}.md".format(pr.number): {"content": comments_md}}
            gist = self.gh.create_gist("Validation of PR #{0} for jsdelivr/jsdelivr".format(pr.number), files=files, public=False)
            state = "failure" if not status.error_occured else "error"
            self.repo.create_status(sha=last_commit.sha, state=state, target_url=gist.html_url, description="Failed automatic validation")

            #create a comment if nothings happening
            if not any(c.user.login == self.config["user"] for c in issue.iter_comments()):
                issue.create_comment(comments_md)
        else:
            #success status
            self.repo.create_status(sha=last_commit.sha, state="success", target_url="http://www.lgtm.in/g", description="LGTM")
            
