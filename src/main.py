import os
import sys
import pathlib

BASE_PATH = pathlib.Path(__file__).parent.parent
paths = [
    os.path.abspath(BASE_PATH / 'src'),
]
[sys.path.append(path) for path in paths]

from core.modular_app import ModularAPI

os.environ['FASTAPI_SETTINGS_MODULE'] = 'settings.config'
app = ModularAPI()
