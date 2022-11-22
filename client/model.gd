extends Node

var data: Dictionary = {}

func init(initial_data: Dictionary):
	update(initial_data)
	return self

func update(new_model: Dictionary):
	data = new_model
