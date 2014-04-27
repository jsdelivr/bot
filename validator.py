from util import INIValidator, CodeValidator, VersionValidator

import pystache

import os
import yaml
import re

import requests

from github3 import login
from github3.pulls import PullRequest

valid_file_characters_re = re.compile(r"^[A-Za-z0-9.\-_/]+$")

class PullBot(INIValidator, CodeValidator, VersionValidator):

    config = yaml.load(open("config.yml"))
    last_checked = 0

    def __init__(self):
        auth = self.config["github"]
        self.gh = login(auth["user"], token=auth["auth_token"])
        self.repo = self.gh.repository(self.config["owner"], self.config["repo"])

    def rebase():
        pass

    def get_project(self, project):
        data = requests.get("http://api.jsdelivr.com/v1/jsdelivr/libraries/{0}".format(project)).json()
        return data[0] if len(data) != 0 and type(data[0]) == dict else None

    def get_pull(self, pr=None):
        if type(pr) == int:
            return self.repo.pull_request(pr)
        elif type(pr) == PullRequest:
            return pr
        #otherwise grab lastest pr
        latest = self.repo.iter_pulls().next()

        if latest.number > self.last_checked:
            self.last_checked = latest.number
            return latest
        return None

    #validate a pr, pr is an int
    def validate(self, pr=None):
        self.repo.refresh()

        validation_state = True

        # self.rebase()
        pr = self.get_pull(pr)
        if not pr:
            return False

        issue = self.repo.issue(pr.number)
        #megawac/jsdelivr
        owner_repo = "/".join(pr.head.repo)

        # collection of (<version>, <name>, <contents>)
        code_files = []
        # in case multiple
        ini_files = {}

        warnings = []

        #group files by project like api.jsdelivr.com/v1/jsdelivr/libraries for ease of iterating
        project_grouped = {}

        for pr_file in pr.iter_files():
            split_name = pr_file.filename.split("/")
            contents = requests.get(pr_file.raw_url).text
            ext = os.path.splitext(pr_file.filename)[1]
            name = "/".join(split_name[3:])
            project = split_name[1]
            version = split_name[2]

            data = {
                "contents": contents,
                "project": project,
                "version": version,
                "name": name,
                "extension": ext
            }

            if not pr_file.filename.islower():
                warnings.append("*{0}* should be lowercase".format(pr_file.filename))
            if not valid_file_characters_re.match(pr_file.filename):
                warnings.append("*{0}* contains illegal characters".format(pr_file.filename))

            if split_name[0] == "files" and len(split_name) > 3:
                code_files.append(data)

                if project not in project_grouped:
                    project_grouped[project] = []
                parent = project_grouped[project]
                
                vgroup = next((x for x in parent if x["version"] == version), None)
                if not vgroup:
                    parent.append({
                        "version": version,
                        "files": [name]
                    })
                else:
                    vgroup["files"].append(name)

                if pr_file.deletions > 0: #the nerve
                    warnings.append("Yo wtf why you be touching the contents of {0}".format(name))

            elif ext == ".ini" and len(split_name) == 3:
                ini_files[project] = data

        checked = {}
        ini_issues = []
        for project_name,project in project_grouped.iteritems():
            checked[project_name] = True
            ini_issues += self.validate_ini(ini_files.get(project_name, None), changed_files=project, project_name=project_name, owner_repo=owner_repo)

        #ini file changed with no other files changed?
        for project,files in ini_files.iteritems():
            if project not in checked:
                ini_issues += self.validate_ini(ini_data=files)

        code_issues = self.validate_code(code_files)

        version_issues = []
        for project_name,project in project_grouped.iteritems():
            version_issues += self.validate_version(project_name, project)

        has_commented = any(c.user.login == self.config["github"]["user"] for c in issue.iter_comments())

        if not has_commented and (warnings or ini_issues or code_issues or version_issues): #report them to the cops
            data = {
                "user": pr.user,

                "has-ini-issues": ini_issues != [],
                "info-issues": ini_issues,

                "has-file-issues": code_issues != [],
                "file-issues": code_issues,

                "has-warnings": warnings != [],
                "warnings": warnings,

                "has-version-issues": version_issues != [],
                "version-issues": version_issues
            }

            with open("templates/pr-issue.tpl") as f:
                issue_template = f.read()
            comments_md = pystache.render(issue_template, data)

            #debugging
            # with open("result.md", "w") as f:
            #     f.write(comments_md)

            issue.create_comment(comments_md)
