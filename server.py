from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

from blinker import signal

class Server(Resource):
    on_pr = signal("pull_event")
    isLeaf = True
    def render_GET(self, request):
        print request
        return "<html><body>What are you doin here buddy?</body></html>"

    def render_POST(self, request):
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
    resource = Server()
    factory = Site(resource)
    print "Booting server on port %d" % (port)
    reactor.listenTCP(port, factory)
    reactor.run()
