import json

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
                raise
            
            for key, value in config["files"].iteritems():
                if key == "basePath":
                    if type(value) != unicode:
                        issues.append("`basePath` for {project} must be a string".format(**schema))
                elif key in ("include", "exclude"):
                    if type(value) != list:
                        issues.append("`{0}` must be an array".format(cludes))
                else:
                    issues.append("""Unexpected key `{0}` for {project};
                        valid keys are `basePath`, `include` and `exclude`.
                    """.format(key, **schema))

            # Validate files exist... maybe later
        except Exception,e:
            issues.append("Issues validating *update.json* for {project}: {0}".format(e, **schema))

        return issues