extends Control

onready var username_field: LineEdit = get_node("CanvasLayer/VBoxContainer/GridContainer/LineEdit_Username")
onready var password_field: LineEdit = get_node("CanvasLayer/VBoxContainer/GridContainer/LineEdit_Password")
onready var login_button: Button = get_node("CanvasLayer/VBoxContainer/CenterContainer/HBoxContainer/Button_Login")
onready var register_button: Button = get_node("CanvasLayer/VBoxContainer/CenterContainer/HBoxContainer/Button_Register")

onready var avatar_panel: Panel = get_node("CanvasLayer/Panel")
onready var avatar_sprite: Sprite = get_node("CanvasLayer/Panel/Control/Avatar")
onready var avatar_animation_player: AnimationPlayer = get_node("CanvasLayer/Panel/Control/Avatar/AnimationPlayer")
onready var avatar_left: Button = get_node("CanvasLayer/Panel/VBoxContainer/HBoxContainer/Button_Left")
onready var avatar_ok: Button = get_node("CanvasLayer/Panel/VBoxContainer/HBoxContainer/Button_Ok")
onready var avatar_right: Button = get_node("CanvasLayer/Panel/VBoxContainer/HBoxContainer/Button_Right")

var avatar_id = 0

signal login(username, password)
signal register(username, password)

func _ready():
	password_field.secret = true
	avatar_panel.visible = false
	
	login_button.connect("pressed", self, "_login")
	register_button.connect("pressed", self, "_choose_avatar")
	
	avatar_left.connect("pressed", self, "_next_avatar")
	avatar_ok.connect("pressed", self, "_register")
	avatar_right.connect("pressed", self, "_prev_avatar")

func _login():
	emit_signal("login", username_field.text, password_field.text)

func _choose_avatar():
	avatar_panel.visible = true
	avatar_animation_player.play("walk_down")

func _next_avatar():
	avatar_id += 1
	if avatar_id >= 6:
		avatar_id = 0
	_update_sprite()

func _prev_avatar():
	avatar_id -= 1
	if avatar_id < 0:
		avatar_id = 5
	_update_sprite()

func _update_sprite():
	avatar_sprite.set_region_rect(Rect2(368, avatar_id * 48, 64, 48))

func _register():
	emit_signal("register", username_field.text, password_field.text, avatar_id)
