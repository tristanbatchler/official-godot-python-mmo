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

var points_x: float = 0

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
	if body:
		if not is_player:
			if server_position:
				velocity = body.position.direction_to(server_position) * 70
				
				if body.position.distance_squared_to(server_position) <= 25:
					velocity = Vector2.ZERO

			
		else:
			velocity = body.position.direction_to(_player_target) * 70
			
			if body.position.distance_squared_to(_player_target) <= 25:
					velocity = Vector2.ZERO
			
		body.position += velocity * delta

