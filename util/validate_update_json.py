import json
from os import path

class UpdateJSONValidator():

    def check_update_file(self, schema):
        issues = []

        try:
            config = json.loads(schema["contents"])

            if config["packageManager"] not in ["github", "npm", "bower"]:
                issues.append("Unrecognized `packageManager` for {project}".format(**schema))

            if "name" not in config:
                issues.append("Missing `name` for {project}".format(**schema))

            if "repo" not in config and config["packageManager"] == "github":
                issues.append("Missing `repo` for {project}".format(**schema))

            if "files" not in config or type(config["files"]) != dict:
                issues.append("Missing files to include for update.json in {project}".format(**schema))
                return issues
            
            for key, value in config["files"].iteritems():
                if key == "basePath":
                    if type(value) != unicode:
                        issues.append("`basePath` for {project} must be a string".format(**schema))
                elif key in ("include", "exclude"):
                    if type(value) != list:
                        issues.append("`{0}` must be an array".format(cludes))
                        continue
                    for x in value:
                        if "basePath" in config["files"] and x.startswith('./'):
                            issues.append('Potentially confusing file path *{0}* with `basePath` set. Consider using *./{0}*'.format(x))
                else:
                    issues.append("""Unexpected key `{0}` for {project};
                        valid keys are `basePath`, `include` and `exclude`.
                    """.format(key, **schema))

            # Validate the linked repo looks
            if config["packageManager"] == "github":
                issues += self.check_gh_repo_schema(config)

            # Validate files exist... maybe later
        except Exception,e:
            issues.append("Issues validating *update.json* for {project}: {0}".format(e, **schema))

        return issues

    def check_gh_repo_schema(self, config):
        split = config["repo"].split("/", 1)
        if len(split) != 2:
            return ["`repo` for Github must be in the format <user>/<repo>"]
        gh_user, gh_repo = split

        repo = self.gh.repository(gh_user, gh_repo)

        if repo is None:
            return ["Could not find repo `%s`" % config["repo"]]

        issues = []

        if next(repo.iter_tags(), None) is None:
            tags_url = "https://github.com/{repo}/tags".format(**config)
            warning = ("The repository appears to have no tagged versions (%s).\n"
                "See [Github Creating Releases](https://help.github.com/articles/creating-releases/) "
                "or [Git tagging basics](https://git-scm.com/book/en/v2/Git-Basics-Tagging). "
                "Auto updating of the library will only take place when `tags` are created."
            ) % (tags_url)
            issues.append(warning)

        return issues
