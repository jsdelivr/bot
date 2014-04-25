import server, validator
import os

from blinker import signal

jimaek = validator.PullBot()

def on_pull(data):
    if data["action"] in ["opened", "reopened", "synchronize"]:
        jimaek.validate(data["number"])

signal("pull_event").connect(on_pull)

DEFAULT_PORT = int(os.environ.get("PORT", 9000))
server.start(DEFAULT_PORT)