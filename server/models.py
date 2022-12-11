from django.db import models
from django.forms import model_to_dict

def create_dict(model: models.Model) -> dict:
    """
    Recursively creates a dictionary based on the supplied model and all its foreign relationships.
    """
    d: dict = model_to_dict(model)
    model_type: type = type(model)
    d["model_type"] = model_type.__name__

    if model_type == InstancedEntity:
        d["entity"] = create_dict(model.entity)

    elif model_type == Actor:
        d["instanced_entity"] = create_dict(model.instanced_entity)
        # Purposefully don't include user information here.
    
    return d

def get_delta_dict(model_dict_before: dict, model_dict_after: dict) -> dict:
    """
    Returns a dictionary containing all differences between the supplied model dicts
    (except for the ID and Model Type).
    """

    delta: dict = {}

    for k in model_dict_before.keys() & model_dict_after.keys():  # Intersection of keysets
        v_before = model_dict_before[k]
        v_after = model_dict_after[k]

        if k in ("id", "model_type"):
            delta[k] = v_after
        if v_before == v_after:
            continue

        if not isinstance(v_before, dict):
            delta[k] = v_after
        else:
            delta[k] = get_delta_dict(v_before, v_after)

    return delta

class User(models.Model):
    username = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=99)

class Entity(models.Model):
    name = models.CharField(max_length=100)

class InstancedEntity(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

class Actor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instanced_entity = models.OneToOneField(InstancedEntity, on_delete=models.CASCADE)
    avatar_id = models.IntegerField(default=0)
