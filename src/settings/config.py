import os
import sys
import pathlib

BASE_PATH = pathlib.Path(__file__).parent.parent

paths = [
    os.path.abspath(BASE_PATH),
]
[sys.path.append(path) for path in paths]
print(sys.path)

API_PREFIX = '/api/v1'

INSTALLED_MODULES = [
    # package name of the modules you want to inject
    'app.modules.auth',
]
LOCALHOST = 'http://localhost(:[0-9]+)?'
TRUSTED_ORIGINS = []
