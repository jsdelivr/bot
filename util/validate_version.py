from find_closest_version import closest_version
import pystache

class VersionValidator():
    difference_template = open("templates/file-differences.tpl").read()

    def validate_version(self, project, project_files):
        issues = []
        existing_project = self.get_project(project)

        if existing_project:
            assets = existing_project["assets"]
            sorted(project_files, key=lambda p: p["version"])
            sorted(assets, key=lambda p: p["version"])
            assets.reverse()

            #in case they added files to a version?
            computed = self.get_library_files(project_files, assets)

            for version in project_files:
                closest = closest_version(assets, version["version"], key=lambda p: p["version"])
                if closest:
                    comp = next(c for c in computed if c["version"] == version["version"])
                    new_files = []
                    missing_files = []
                    for fn in comp["files"]:
                        if fn not in closest["files"]:
                            new_files.append(fn)
                    for fn in closest["files"]:
                        if fn not in comp["files"]:
                            missing_files.append(fn)

                    if new_files or missing_files:
                        data = {
                            "project": project,
                            "previous-version": closest["version"],
                            "version": version["version"],
                            "new-files": new_files,
                            "missing-files": missing_files
                        }
                        issues.append(pystache.render(self.difference_template, data))
        return issues
