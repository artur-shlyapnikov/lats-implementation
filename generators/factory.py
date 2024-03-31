from .generator_types import Generator
from .model import GPT35, GPT4Turbo, ModelBase
from .py_generate import PyGenerator


def generator_factory(lang: str) -> Generator:
    if lang == "py" or lang == "python":
        return PyGenerator()
    else:
        raise ValueError(f"Invalid language for generator: {lang}")


def model_factory(model_name: str) -> ModelBase:
    if model_name == "gpt-4-turbo-preview":
        return GPT4Turbo()
    elif model_name == "gpt-3.5-turbo-0613":
        return GPT35()
    else:
        raise ValueError(f"Invalid model name: {model_name}")
