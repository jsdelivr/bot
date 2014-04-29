from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

from blinker import signal

import json

class Server(Resource):
    on_pr = signal("pull_event")
    isLeaf = True
    def render_GET(self, request):
        return "<html><body>What are you doin here buddy?</body></html>"

    def render_POST(self, request):
        try:
            parsed = json.loads(request.content.read())
            data = {k: parsed[k] for k in ("number", "action")}
        except Exception as e:
            data = {
                "number": int(request.args.get("number", [""])[0]),
                "action": str(request.args.get("action", [""])[0])
            }
        reactor.callInThread(self.on_pr.send, data) # self.on_pr.send(data)
        return ""

def start(port):
    resource = Server()
    factory = Site(resource)
    print "Booting server on port %d" % (port)
    reactor.listenTCP(port, factory)
    reactor.run()
