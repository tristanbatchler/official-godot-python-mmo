import manage
import sys
import protocol
from twisted.python import log
from twisted.internet import reactor, task
from autobahn.twisted.websocket import WebSocketServerFactory


class GameFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        self.protocol = protocol.GameServerProtocol
        super().__init__(f"ws://{hostname}:{port}")

        self.players: set[protocol.GameServerProtocol] = set()
        self.tickrate: int = 5

    def tick(self):
        for p in self.players:
            p.tick()

    # Override
    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        task.LoopingCall(p.tick).start(1 / self.tickrate)
        self.players.add(p)
        return p


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    PORT: int = 8081
    factory = GameFactory('0.0.0.0', PORT)

    reactor.listenTCP(PORT, factory)
    reactor.run()
