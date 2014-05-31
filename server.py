from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

from blinker import signal

import json

class Server(Resource):
    on_pr = signal("pull_event")
    on_comment = signal("comment_event")
    isLeaf = True
    def render_GET(self, request):
        return "<html><body>What are you doin here buddy?</body></html>"

    def render_POST(self, request):
        try:
            parsed = json.loads(request.content.read())
            print parsed
            data = {k: v for k, v in parsed.iteritems()
                            if k in ("issue", "comment", "number", "action")}
        except Exception as e:
            data = {
                "issue": request.args.get("issue", [None])[0],
                "number": int(request.args.get("number", ["-1"])[0]),
                "comment": request.args.get("comment", [None])[0],
                "action": str(request.args.get("action", [""])[0])
            }
            data = {k: v for k, v in data.iteritems() if v and v != -1}

        event = self.on_pr if "number" in data else self.on_comment
        reactor.callInThread(event.send, data) # self.on_pr.send(data)
        return ""

def start(port):
    resource = Server()
    factory = Site(resource)
    print "Booting server on port %d" % (port)
    reactor.listenTCP(port, factory)
    reactor.run()
