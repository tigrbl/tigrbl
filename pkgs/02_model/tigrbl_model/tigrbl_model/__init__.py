"""Pydantic-independent models for Tigrbl."""

from .config import ConfigDict, ModelConfig
from .errors import ErrorDetails, ModelUserError, ValidationError
from .factory import create_model
from .fields import AliasChoices, Field, FieldInfo, PydanticUndefined, Undefined
from .mixins import JsonMixin, SerdeMixin, TomlMixin, YamlMixin
from .model import BaseModel, Model
from .root import RootModel
from .validators import field_validator, model_validator

__version__ = "0.4.5.dev4"

__all__ = [
    "AliasChoices",
    "BaseModel",
    "ConfigDict",
    "ErrorDetails",
    "Field",
    "FieldInfo",
    "JsonMixin",
    "Model",
    "ModelConfig",
    "ModelUserError",
    "PydanticUndefined",
    "RootModel",
    "SerdeMixin",
    "TomlMixin",
    "Undefined",
    "ValidationError",
    "YamlMixin",
    "create_model",
    "field_validator",
    "model_validator",
]
