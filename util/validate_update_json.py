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
            
            files = config["files"]
            if "basePath" in files and type(files["basePath"]) != unicode:
                issues.append("basePath for {project} must be a string".format(**schema))

            for cludes in ("include", "exclude"):
                if cludes in files and type(files[cludes]) != list:
                    issues.append("{0} must be an array".format(cludes))

            # Validate files exist... maybe later
        except Exception,e:
            issues.append("Issues validating *update.json* for {project}: {0}".format(e, **schema))

        return issues