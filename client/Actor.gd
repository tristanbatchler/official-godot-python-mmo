extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")
onready var sprite: Sprite = get_node("KinematicBody2D/Sprite")
onready var line: Line2D = get_node("KinematicBody2D/CanvasLayer/Line2D")

var server_position: Vector2
var actor_name: String
var velocity: Vector2 = Vector2.ZERO

var is_player: bool = false
var _player_target: Vector2

var speed: float = 70.0

func update(new_model: Dictionary):
	.update(new_model)
	
	var ientity = new_model["instanced_entity"]
	server_position = Vector2(float(ientity["x"]), float(ientity["y"]))
	actor_name = ientity["entity"]["name"]
	
	if label:
		label.text = actor_name
		
	if body and not server_position:
		body.position = server_position

func _physics_process(delta):
	if not body:
		return
		
	var target: Vector2
	if is_player:
		target = _player_target
	elif server_position:
		target = server_position
		
	velocity = body.position.direction_to(target) * self.speed
	
	if body.position.distance_to(server_position) <= self.speed * delta:
		velocity = Vector2.ZERO
		
	body.position += velocity * delta

