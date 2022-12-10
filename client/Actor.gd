extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")
onready var sprite: Sprite = get_node("KinematicBody2D/Avatar")
onready var animation_player: AnimationPlayer = get_node("KinematicBody2D/Avatar/AnimationPlayer")

var server_position: Vector2
var initialised_position: bool = false
var actor_name: String
var velocity: Vector2 = Vector2.ZERO

var is_player: bool = false
var _player_target: Vector2

var rubber_band_radius: float = 200

var speed: float = 70.0

func _ready():
	update(initial_data)

func update(new_model: Dictionary):
	.update(new_model)
	
	# Set the correct sprite for the actor's avatar ID
	if new_model.has("avatar_id"):
		sprite.set_region_rect(Rect2(368, new_model["avatar_id"] * 48, 64, 48))
	
	if new_model.has("instanced_entity"):
		var ientity = new_model["instanced_entity"]
		
		if ientity.has("x") and ientity.has("y"):
			server_position = Vector2(float(ientity["x"]), float(ientity["y"]))
			
			if not initialised_position:
				initialised_position = true
				body.position = server_position
				if is_player:
					_player_target = server_position
			elif (body.position - server_position).length() > rubber_band_radius:
				# Rubber band if body position too far away from server position
				body.position = server_position
				
			
		if ientity.has("entity"):
			var entity = ientity["entity"]
			if entity.has("name"):
				actor_name = ientity["entity"]["name"]
		
				if label:
					label.text = actor_name

func _physics_process(delta):	
	var target: Vector2
	if is_player:
		target = _player_target
	else:
		target = server_position
		
	velocity = (target - body.position).normalized() * speed
	if (target - body.position).length() > 5:
		velocity = body.move_and_slide(velocity)
	else:
		velocity = Vector2.ZERO

func _process(delta):
	# Get the direction angle
	var angle = velocity.angle()

	# Check which quadrant the angle is in and play animation accordingly
	if velocity.length() <= 5:
		animation_player.stop()
	elif -PI/4 <= angle and angle < PI/4:
		animation_player.play("walk_right")
	elif PI/4 <= angle  and angle < 3*PI/4:
		animation_player.play("walk_down")
	elif -3*PI/4 <= angle and angle < -PI/4:
		animation_player.play("walk_up")
	else:
		animation_player.play("walk_left")


