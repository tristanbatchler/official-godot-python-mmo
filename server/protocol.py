import math
import queue
import time
from server import packet
from server import models
from autobahn.twisted.websocket import WebSocketServerProtocol

class GameServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self._packet_queue: queue.Queue[tuple['GameServerProtocol', packet.Packet]] = queue.Queue()
        self._state: callable = self.LOGIN
        self._actor: models.Actor = None
        self._last_delta_move_checked = None
        self._delta_move: float = None

    def LOGIN(self, sender: 'GameServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Login:
            username, password = p.payloads
            if models.User.objects.filter(username=username, password=password).exists():
                user = models.User.objects.get(username=username)
                self._actor = models.Actor.objects.get(user=user)
                self._player_target = [self._actor.instanced_entity.x, self._actor.instanced_entity.y]
                
                self.send_client(packet.OkPacket())
                self.send_client(packet.ModelDataPacket(models.create_dict(self._actor)))

                self._state = self.PLAY
            else:
                self.send_client(packet.DenyPacket("Username or password incorrect"))

        elif p.action == packet.Action.Register:
            username, password = p.payloads
            if models.User.objects.filter(username=username).exists():
                self.send_client(packet.DenyPacket("This username is already taken"))
            else:
                user = models.User(username=username, password=password)
                user.save()
                player_entity = models.Entity(name=username)
                player_entity.save()
                player_ientity = models.InstancedEntity(entity=player_entity, x=0, y=0)
                player_ientity.save()
                player = models.Actor(instanced_entity=player_ientity, user=user)
                player.save()
                self.send_client(packet.OkPacket())

    def PLAY(self, sender: 'GameServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Chat:
            if sender == self:
                self.broadcast(p, exclude_self=True)
            else:
                self.send_client(p)
        
        elif p.action == packet.Action.ModelData:
            self.send_client(p)

        elif p.action == packet.Action.Target:
            target = p.payloads
            pos = [self._actor.instanced_entity.x, self._actor.instanced_entity.y]
        
            now = time.time()
            if self._last_delta_move_checked:
                self._delta_move = now - self._last_delta_move_checked
            self._last_delta_move_checked = now

            if self._delta_move:
                print(self._delta_move)
                dist = 70 * self._delta_move
            else:
                dist = 70 / self.factory.tickrate

            if self._distance_squared_to(pos, target) > dist**2:
                # Update our model if we're not already close enough to the target
                d_x, d_y = self._direction_to(pos, target)
                self._actor.instanced_entity.x += d_x * dist
                self._actor.instanced_entity.y += d_y * dist
                
                # Add this packet back to the queue to repeat this process until we're close enough
                self.onPacket(self, p)

                # Broadcast our new model to everyone
                self.broadcast(packet.ModelDataPacket(models.create_dict(self._actor)))
            else:
                self._last_delta_move_checked = None


    def tick(self):
        # Process the next packet in the queue
        if not self._packet_queue.empty():
            s, p = self._packet_queue.get()
            self._state(s, p)

    @staticmethod
    def _distance_squared_to(current: list[float], target: list[float]) -> float:
        if target == current:
            return 0
        
        return (target[0] - current[0])**2 + (target[1] - current[1])**2

    @staticmethod
    def _direction_to(current: list[float], target: list[float]) -> list[float]:
        if target == current:
            return [0, 0]
        
        n_x = target[0] - current[0]
        n_y = target[1] - current[1]

        length = math.sqrt(GameServerProtocol._distance_squared_to(current, target))
        return [n_x / length, n_y / length]

    def broadcast(self, p: packet.Packet, exclude_self: bool = False):
        for other in self.factory.players:
            if other == self and exclude_self:
                continue
            other.onPacket(self, p)

    # Override
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    # Override
    def onOpen(self):
        print(f"Websocket connection open.")

    # Override
    def onClose(self, wasClean, code, reason):
        self.factory.players.remove(self)
        print(f"Websocket connection closed{' unexpectedly' if not wasClean else ' cleanly'} with code {code}: {reason}")

    # Override
    def onMessage(self, payload, isBinary):
        decoded_payload = payload.decode('utf-8')

        try:
            p: packet.Packet = packet.from_json(decoded_payload)
        except Exception as e:
            print(f"Could not load message as packet: {e}. Message was: {payload.decode('utf8')}")

        self.onPacket(self, p)

    def onPacket(self, sender: 'GameServerProtocol', p: packet.Packet):
        self._packet_queue.put((sender, p))
        print(f"Queued packet: {p}")

    def send_client(self, p: packet.Packet):
        b = bytes(p)
        self.sendMessage(b)
