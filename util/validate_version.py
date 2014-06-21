from find_closest_version import closest_version
import pystache
from urlparse import urljoin

class VersionValidator():
    difference_template = open("templates/file-differences.tpl").read()

    def validate_version(self, project_name, project_files):
        issues = []
        existing_project = self.get_project(project_name)

        if existing_project:
            assets = existing_project["assets"]
            assets.reverse()

            #in case they added files to a version?
            computed = self.get_library_files(project_files, assets)

            for version in project_files:
                closest = closest_version(assets, version, key=lambda p: p["version"])
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
                            "project": project_name,
                            "previous-version": closest["version"],
                            "version": version["version"],
                            "new-files": new_files,
                            "missing-files": missing_files
                        }
                        issues.append(pystache.render(self.difference_template, data))
        return issues

    def validate_tags(self, project_name, project_files, ini_file=None):
        issues = []
        if ini_file is None:
            ini_file = self.get_project(project_name)

        github_url = ini_file["github"]
        if github_url:
            if not github_url.endswith("/"):
                github_url += "/"
            repo = self.gh.repository(*github_url.split("/")[-2:])
            for version in project_files:
                if not any(version["version"] in tag.name for tag in repo.iter_tags()):
                    github_tag_url = urljoin(github_url, "releases")
                    issues.append("{0} **{version} is [not tagged]({1})**".format(project_name, github_tag_url, **version))
        return issues
