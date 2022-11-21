extends Control

onready var username_field: LineEdit = get_node("CanvasLayer/VBoxContainer/GridContainer/LineEdit_Username")
onready var password_field: LineEdit = get_node("CanvasLayer/VBoxContainer/GridContainer/LineEdit_Password")
onready var login_button: Button = get_node("CanvasLayer/VBoxContainer/CenterContainer/HBoxContainer/Button_Login")
onready var register_button: Button = get_node("CanvasLayer/VBoxContainer/CenterContainer/HBoxContainer/Button_Register")

signal login(username, password)
signal register(username, password)

func _ready():
	password_field.secret = true
	login_button.connect("pressed", self, "_login")
	register_button.connect("pressed", self, "_register")

func _login():
	emit_signal("login", username_field.text, password_field.text)

func _register():
	emit_signal("register", username_field.text, password_field.text)
