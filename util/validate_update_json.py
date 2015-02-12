import json

class UpdateJSONValidator():

    def check_update_file(self, schema):
        issues = []

        try:
            config = json.loads(schema["contents"])

            if config["packageManager"] not in ["github", "npm", "bower"]:
                issues.append("Unrecognized `packageManager` for {project}".format(**schema))
            if config["name"] != schema["project"]:
                issues.append("Name mismatch for update.json in {project}".format(**schema))

            if type(config["files"]) != dict or type(config["files"]["basePath"]) != unicode:
                issues.append("Missing files to include for update.json in {project}".format(**schema))

            # Validate files exist... maybe later
        except Exception,e:
            issues.append("Issues validating *update.json* for {project}: {0}".format(e, **schema))

        return issues