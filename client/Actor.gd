extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")
onready var sprite: Sprite = get_node("KinematicBody2D/Sprite")

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

func _physics_process(delta):
	var target: Vector2
	if is_player:
		target = _player_target
	elif server_position:
		target = server_position
		
	velocity = (target - body.position).normalized() * speed
	if (target - body.position).length() > 5:
		velocity = body.move_and_slide(velocity)
