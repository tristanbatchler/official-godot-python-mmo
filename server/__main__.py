import manage
import os
import protocol
import sys

from twisted.internet import reactor, ssl
import logging
from autobahn.twisted.websocket import WebSocketServerFactory
from OpenSSL import crypto
from twisted.internet.ssl import PrivateCertificate, CertificateOptions
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from OpenSSL.crypto import load_privatekey, FILETYPE_PEM
from twisted.internet import reactor, task, ssl


class GameFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        self.protocol = protocol.GameServerProtocol
        super().__init__(f"wss://{hostname}:{port}")

        self.players: set[protocol.GameServerProtocol] = set()
        self.tickrate: int = 20
        self.user_ids_logged_in: set[int] = set()

        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / self.tickrate)

    def tick(self):
        for p in self.players:
            p.tick()

    def remove_protocol(self, p: protocol.GameServerProtocol):
        self.players.remove(p)
        if p._actor and p._actor.user.id in self.user_ids_logged_in:
            self.user_ids_logged_in.remove(p._actor.user.id)
        

    # Override
    def buildProtocol(self, addr):
        p = super().buildProtocol(addr)
        self.players.add(p)
        return p

if __name__ == '__main__':
    print("Starting")
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(format)
    logger.addHandler(stdout_handler)

    certs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
    private_key_data = open(os.path.join(certs_dir, "server.key"), "rb").read()
    certificate_data = open(os.path.join(certs_dir, "server.crt"), "rb").read()

    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data)
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_data)

    cert_options = CertificateOptions(
        privateKey=private_key,
        certificate=certificate,
    )

    PORT: int = 8081
    factory = GameFactory('0.0.0.0', PORT)

    logger.info(f"Server listening on port {PORT}")
    reactor.listenSSL(PORT, factory, cert_options)

    reactor.run()