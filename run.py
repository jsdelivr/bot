import server, validator
import os

from blinker import signal

jimaek = validator.PullBot()

def on_pull(data):
    print data
    if data.get("action", None) in ["opened", "reopened", "synchronize"]:
        print "Validating pr {number}".format(**data)
        jimaek.validate(int(data.get("number", None)))

signal("pull_event").connect(on_pull)

DEFAULT_PORT = int(os.environ.get("PORT", 9000))
server.start(DEFAULT_PORT)