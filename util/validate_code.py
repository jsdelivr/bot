import os, re

# from https://github.com/hamilyon/status/blob/master/grin.py
TEXTCHARS = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))
ALLBYTES = ''.join(map(chr, range(256)))

def is_binary_string(bytes):
    bytes = bytes[:1024] #hack patch #3
    if isinstance(bytes, unicode):
        bytes = bytes.encode("ascii", errors="ignore")
    return bool(bytes.translate(ALLBYTES, TEXTCHARS))


class CodeValidator():
    warn_statements = [r"\bprompt\(\b", r"\balert\(\b", r"\bconfirm\(\b", r"document\.write"]

    # true binary, false non binary
    valid_extensions = {
        ".css": False,
        ".js": False,
        ".map": False,

        #flash
        ".png": True,
        ".jpg": True,
        ".jpeg": True,
        ".gif": True,
        ".ico": True,

        #fonts
        ".otf": True,
        ".eot": True,
        ".ttf": True,
        ".woff": True,

        #etc
        ".svg": False,
        ".swf": True
    }

    def validate_code(self, files):
        issues = []

        for file in files:
            if file["extension"] not in self.valid_extensions:
                issues.append("*{extension}* (on *{name}*) seems odd to want to host?".format(**file))
                continue
            elif is_binary_string(file["contents"]) != self.valid_extensions.get(file["extension"]):
                msg = "to be binary content" if self.valid_extensions.get(file["extension"]) else "to not be binary content"
                issues.append("Expected *{name}* {0}".format(msg, **file))
                continue

            if file["extension"] != ".js" and file["extension"] != ".css":
                continue
            
            if re.search(r"\bmin\b", file["name"]):
                #warn if more than 10 lines in "minimized" file
                if len(file["contents"].splitlines(True)) > 10:
                    issues.append("Is {name} ({version}) properly minimized?".format(**file))

            for test in self.warn_statements:
                if re.search(test, file["contents"]):
                    issues.append("Expression `{0}` had a match in the contents of *{name}* ({version}).".format(test, **file))

            #no comments... could be more sound by checking start
            # if not re.search(r"(?:\/\*(?:[\s\S]*?)\*\/)|(?:([\s;])+\/\/(?:.*)$)", file["contents"], re.MULTILINE):
            #     issues.append("*{name}* ({version}) probably should start with a header detailing author and code source".format(**file))

        return issues

