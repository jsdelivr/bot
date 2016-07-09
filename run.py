#! /usr/bin/env python

import server, validator
import os

from blinker import signal

jimaek = validator.PullBot()

def on_pull(data):
    action = data.get("action", None)
    num = int(data.get("number", None))
    if action in ("opened", "reopened", "synchronize"):
        # print "Validating pr {number}".format(**data)
        jimaek.validate(num)
    elif action == "closed":
        jimaek.closed_pr(num)

def on_comment(data):
    number = data["issue"]["number"]
    comment = data["comment"]["body"]
    user = data["comment"]["user"]["login"]

    if data.get("action", None) == "created":
        jimaek.check_comment(number, comment, user)

signal("pull_event").connect(on_pull)
signal("comment_event").connect(on_comment)

DEFAULT_PORT = int(os.environ.get("PORT", 9000))
server.start(DEFAULT_PORT)