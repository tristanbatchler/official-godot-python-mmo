import math
import utils
import queue
import time
from server import packet
from server import models
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.exception import Disconnected
from django.contrib.auth import authenticate

class GameServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self._packet_queue: queue.Queue[tuple['GameServerProtocol', packet.Packet]] = queue.Queue()
        self._state: callable = self.LOGIN
        self._actor: models.Actor = None
        self._player_direction: list[float] = None
        self._last_delta_time_checked = None
        self._known_others: set['GameServerProtocol'] = set()

    def LOGIN(self, sender: 'GameServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Login:
            username, password = p.payloads

            # Try to get an existing user whose credentials match
            user = authenticate(username=username, password=password)
            
            # If credentials don't match, deny and return
            if not user:
                self.send_client(packet.DenyPacket("Username or password incorrect"))
                return

            # If user already logged in, deny and return
            if user.id in self.factory.user_ids_logged_in:
                self.send_client(packet.DenyPacket("You are already logged in"))
                return

            # Otherwise, proceed
            self._actor = models.Actor.objects.get(user=user)
            self.send_client(packet.OkPacket())

            # Send full model data the first time we log in
            self.broadcast(packet.ModelDeltaPacket(models.create_dict(self._actor)))

            self.factory.user_ids_logged_in.add(user.id)

            self._state = self.PLAY
                

        elif p.action == packet.Action.Register:
            username, password, avatar_id = p.payloads
            
            if not username or not password:
                self.send_client(packet.DenyPacket("Username or password must not be empty"))
                return

            if models.User.objects.filter(username=username).exists():
                self.send_client(packet.DenyPacket("This username is already taken"))
                return

            user = models.User.objects.create_user(username=username, password=password)
            user.save()
            player_entity = models.Entity(name=username)
            player_entity.save()
            player_ientity = models.InstancedEntity(entity=player_entity, x=0, y=0)
            player_ientity.save()
            player = models.Actor(instanced_entity=player_ientity, user=user, avatar_id=avatar_id)
            player.save()
            self.send_client(packet.OkPacket())

    def PLAY(self, sender: 'GameServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Chat:
            if sender == self:
                self.broadcast(p, exclude_self=True)
            else:
                self.send_client(p)
        
        elif p.action == packet.Action.ModelDelta:
            self.send_client(p)
            if sender not in self._known_others:
                # Send our full model data to the new player
                sender.onPacket(self, packet.ModelDeltaPacket(models.create_dict(self._actor)))
                self._known_others.add(sender)
                
        elif p.action == packet.Action.Direction:
            self._player_direction = p.payloads

        elif p.action == packet.Action.Disconnect:
            self._known_others.remove(sender)
            self.send_client(p)

    def _update_position(self) -> bool:
        "Attempt to update the actor's position and return true only if the position was changed"
        if not self._player_direction:
            return False
        pos = [self._actor.instanced_entity.x, self._actor.instanced_entity.y]

        now: float = time.time()
        delta_time: float = 1 / self.factory.tickrate
        if self._last_delta_time_checked:
            delta_time = now - self._last_delta_time_checked
        self._last_delta_time_checked = now

        # Use delta time to calculate distance to travel this time
        dist: float = 70 * delta_time
        
        # Update our model
        d_x, d_y = self._player_direction
        new_x = pos[0] + d_x * dist
        new_y = pos[1] + d_y * dist

        if math.dist(pos, [new_x, new_y]) < 0.01:
            return False

        self._actor.instanced_entity.x += d_x * dist
        self._actor.instanced_entity.y += d_y * dist
        self._actor.instanced_entity.save()

        return True

    def tick(self):
        # Process the next packet in the queue
        if not self._packet_queue.empty():
            s, p = self._packet_queue.get()
            self._state(s, p)

        # To do when there are no packets to process
        elif self._state == self.PLAY: 
            actor_dict_before: dict = models.create_dict(self._actor)
            if self._update_position():
                actor_dict_after: dict = models.create_dict(self._actor)
                self.broadcast(packet.ModelDeltaPacket(models.get_delta_dict(actor_dict_before, actor_dict_after)))


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
        if self._actor:
            self._actor.save()
            self.broadcast(packet.DisconnectPacket(self._actor.id), exclude_self=True)
        self.factory.remove_protocol(self)
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
        try:
            self.sendMessage(b)
        except Disconnected:
            print(f"Couldn't send {p} because client disconnected.")


