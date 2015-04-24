import json

class UpdateJSONValidator():

    def check_update_file(self, schema):
        issues = []

        try:
            config = json.loads(schema["contents"])

            if config["packageManager"] not in ["github", "npm", "bower"]:
                issues.append("Unrecognized `packageManager` for {project}".format(**schema))

            if "files" not in config or type(config["files"]) != dict:
                issues.append("Missing files to include for update.json in {project}".format(**schema))

            elif "basePath" in config["files"] and type(config["files"]["basePath"]) != unicode:
                raise

            # Validate files exist... maybe later
        except Exception,e:
            issues.append("Issues validating *update.json* for {project}: {0}".format(e, **schema))

        return issues