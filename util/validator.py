from validate_ini import INIValidator
from validate_code import CodeValidator
from validate_version import VersionValidator
from validate_update_json import UpdateJSONValidator

from os import path
import re

import requests

class ValidationState:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

valid_file_characters_re = re.compile(r"^[A-Za-z0-9.\-_/]+$")

class PullValidator(INIValidator, CodeValidator, VersionValidator, UpdateJSONValidator):
    """
        Does the heavy lifting bringing together the components to validate a pr
    """
    def __init__(self):
        pass

    def get_project(self, project):
        """
            Get project project from the api
        """
        data = requests.get("http://api.jsdelivr.com/v1/jsdelivr/libraries/{0}".format(project)).json()
        return data[0] if len(data) != 0 and type(data[0]) == dict else None

    def validate(self, pr, debug=False):
        """
            validate a pull request for jsdelivr/jsdelivr
        """

        # did validation raise an exception somewhere?
        errored_out = False

        # e.g. megawac/jsdelivr
        owner_repo = "/".join(pr.head.repo)
        ref = pr.head.ref

        # collection of (<version>, <name>, <contents>)
        code_files = []

        # update.json files
        update_files = []

        # in case multiple
        ini_files = {}

        warnings = []

        # group files by project like api.jsdelivr.com/v1/jsdelivr/libraries for ease of iterating
        project_grouped = {}

        for pr_file in pr.iter_files():
            if pr_file.changes != 0: #text based file
                contents = requests.get(pr_file.raw_url).text
            else: #binary file
                contents = None

            split_name = pr_file.filename.split("/")

            if len(split_name) < 2 or split_name[0] != "files":
                continue
            elif len(split_name) == 2:
                warnings.append("Files should exist under `files/<project>` not under `files`!")

            project, version = split_name[1:3]
            name = "/".join(split_name[3:])

            ext = path.splitext(pr_file.filename)[1]

            data = {
                "contents": contents,
                "project": project,
                "version": version,
                "name": name,
                "extension": ext
            }

            if not "/".join(split_name[:3]).islower():
                warnings.append("*{0}* should be lowercase".format(pr_file.filename))
            if not valid_file_characters_re.match(pr_file.filename):
                warnings.append("*{0}* contains illegal characters".format(pr_file.filename))

            if len(split_name) > 3:
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

                if pr_file.status == "modified": #the nerve
                    warnings.append("You appear to be changing the file contents of *{0}* in *{1}*!".format(name, version))

            elif ext == ".ini" and len(split_name) == 3:
                ini_files[project] = data
            elif ext == ".json" and len(split_name) == 3:
                if name == "update":
                    update_files.append(data)
            else:
                code_files.append("Unexpected file at {0}".format(pr.filename))


        checked = {}
        ini_issues = []
        for project_name, project in project_grouped.iteritems():
            checked[project_name] = True
            try:
                ini_issues += self.validate_ini(ini_files.get(project_name, None), changed_files=project, project_name=project_name, owner_repo=owner_repo, ref=ref)
            except Exception,e:
                if debug == True: raise
                errored_out = True
                ini_issues.append("Failed to validate {0}: {1}".format(project_name, str(e)))

        #ini file changed with no other files changed?
        for project,files in ini_files.iteritems():
            if project not in checked:
                try:
                    ini_issues += self.validate_ini(ini_data=files)
                except Exception,e:
                    if debug == True: raise
                    errored_out = True
                    ini_issues.append("Failed to validate {0}: {1}".format(project_name, str(e)))

        try:
            code_issues = self.validate_code(code_files)
        except Exception,e:
            if debug == True: raise
            errored_out = True
            code_issues = [str(e)]

        version_issues = []
        for project_name, project in project_grouped.iteritems():
            version_issues += self.validate_version(project_name, project)

            try:
                warnings += self.validate_tags(project_name, project, ini_files.get(project_name, None))
            except: pass

        for update_file in update_files:
            self.check_update_file(update_file)

        result = {
            "ini_issues": ini_issues,
            "file_issues": code_issues,
            "version_issues": version_issues,
            "warnings": warnings,

            "error_occured": errored_out
        }

        return ValidationState(**result)
