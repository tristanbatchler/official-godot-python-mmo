extends Node

const Packet = preload("res://packet.gd")

signal connected
signal data
signal disconnected
signal error

# Our WebSocketPeer instance
var socket = WebSocketPeer.new()

func _ready():
	var hostname = "localhost"
	var port = 8081
	var websocket_url = "wss://%s:%d" % [hostname, port]
	var options = TLSOptions.client_unsafe()
	var err = socket.connect_to_url(websocket_url, options)

	if err != OK:
		print("Unable to connect")
		set_process(false)
		emit_signal("error")

func _process(delta):
	socket.poll()
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			print("Packet: ", packet)
			data.emit(packet.get_string_from_utf8())
	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass
	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.

func send_packet(packet: Packet) -> void:
	# Sends a packet to the server
	_send_string(packet.tostring())

func _send_string(string: String) -> void:
	socket.send_text(string)
	print("Sent string ", string)

