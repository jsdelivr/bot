import server, validator
import os

from blinker import signal

jimaek = validator.PullBot()

def on_pull(data):
	print "Received pr post: %s" % (str(data))

	action = data["action"][0] if type(data.get("action", None)) == list else data.get("action", None)
	if action in ["opened", "reopened", "synchronize"]:
		print "Validating pr {number}".format(**data)
		number = data["number"][0] if type(data.get("number", None)) == list else data.get("number", None)
        jimaek.validate(int(number))

signal("pull_event").connect(on_pull)

DEFAULT_PORT = int(os.environ.get("PORT", 9000))
server.start(DEFAULT_PORT)