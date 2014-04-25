from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from blinker import signal

import logging

class Server(Resource):
    on_pr = signal("pull_event")

    def render_POST(self, request):
        print request
        try:
            data = {
                "number": request.args["number"],
                "action": request.args["action"]
            }
            self.on_pr.send(data)
        except:
            print "Failed to validate request\n\n"
        return ""

def start(port):
    root = Resource()
    root.putChild("form", Server())
    factory = Site(root)
    print "Booting server on port %d" % (port)
    reactor.listenTCP(port, factory)
    reactor.run()