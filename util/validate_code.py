import os, re

class CodeValidator():
    minfile_max_lines = 10
    warn_statements = [r"\bprompt\b", "\balert\b", r"\bconfirm\b", r"document\.write"]
    valid_extensions = [".css", ".js", ".map",
        ".png", ".jpg", ".jpeg", ".gif", ".ico",
        ".otf", ".eot", ".svg", ".ttf", ".woff"]

    
    def validate_code(self, files):
        issues = []

        for file in files:
            if file["extension"] not in self.valid_extensions:
                issues.append("*{extension}* (on *{name}*) seems odd to want to host?".format(**file))
                continue

            if not (file["extension"] == ".js" or file["extension"] == ".css"):
                continue

            contents = file["contents"]
            
            if re.search("\bmin\b", file["name"]):
                if len(contents.splitlines(True)) > minfile_max_lines:
                    issues.append("**Is {name} ({version}) properly minimized?**".format(**file))

            for test in self.warn_statements:
                if re.search(test, contents):
                    issues.append("Expression `{0}` had a match in the contents of *{name}* ({version}).".format(test, **file))

            #no comments... could be more sound by checking start
            # if not re.search(r"(?:\/\*(?:[\s\S]*?)\*\/)|(?:([\s;])+\/\/(?:.*)$)", contents, re.MULTILINE):
            #     issues.append("*{name}* ({version}) probably should start with a header detailing author and code source".format(**file))

        return issues

