from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

from blinker import signal

import json, yaml

from hashlib import sha1
import hmac

class AuthenticationException(Exception):
    pass

class Server(Resource):
    on_pr = signal("pull_event")
    on_comment = signal("comment_event")
    isLeaf = True
    secret = yaml.load(open("config.yml"))["post_secret"]

    def render_GET(self, request):
        return "<html><body>What are you doin here buddy?</body></html>"

    def render_POST(self, request):
        body = request.content.read()
        # msg = request.getHeader("X-Hub-Signature")[5:]

        #http://pubsubhubbub.googlecode.com/svn/trunk/pubsubhubbub-core-0.3.html#authednotify
        # hash = hmac.new(self.secret, msg, sha1)
        # if hash.digest().decode("hex") != request.content.getvalue():
        #     raise AuthenticationException("Could not identify")

        parsed = json.loads(body)
        data = {k: v for k, v in parsed.iteritems()
                        if k in ("issue", "comment", "number", "action")}

        event = self.on_pr if "number" in data else self.on_comment
        reactor.callInThread(event.send, data) # self.on_pr.send(data)
        return ""

def start(port):
    resource = Server()
    factory = Site(resource)
    print "Booting server on port %d" % (port)
    reactor.listenTCP(port, factory)
    reactor.run()
