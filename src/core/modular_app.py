import os

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware


def import_settings(config_path):
    import importlib
    settings_module = importlib.import_module(config_path)
    return settings_module


def load_modules(modular_app):
    import importlib

    def add_api_endpoints(name, module, router):
        app = getattr(module, 'app', None)
        if app is not None:
            print('Loaded Views from:', app.__class__.__name__)
            router.include_router(app.router, tags=[name] + app.tags)

    for module in modular_app.settings.INSTALLED_MODULES:
        app_module = importlib.import_module('%s.config' % module)
        get_app = getattr(app_module, 'app', None)
        if get_app is not None:
            name = get_app.__class__.__name__
            add_api_endpoints(name, app_module, modular_app.app.router)
        else:
            import inspect
            config_classes = inspect.getmembers(app_module, lambda member: inspect.isclass(
                member) and member.__module__ == app_module.__name__)
            try:
                assert len(config_classes) == 1
                print(config_classes)
                name, class_object = config_classes[0]
                setattr(app_module, 'app', class_object())
                add_api_endpoints(name, app_module, modular_app.app.router)
            except AssertionError as ae:
                ae.args += (
                    'Config must have a single implementation of [%s]. ' % 'core.module_loader.AbstractModule' +
                    'Found %s implementations! ' % len(config_classes) +
                    'At module [%s]' % app_module.__name__,
                )
                raise ae


def load_views(self):
    import importlib
    path, module, file = self.__module__.rsplit('.', maxsplit=2)
    views = importlib.import_module('.%s.views' % module, package=path)


class AbstractModule:
    def __init__(self):
        from fastapi import APIRouter

        self.name = self.__class__.__name__
        self.tags = [self.name]
        self.router = APIRouter()
        self.router.prefix = '/%s' % (self.name.lower())
        self.initialize()

    def initialize(self):
        import importlib

        curr_module = importlib.import_module(self.__module__)

        setattr(curr_module, 'app', self)
        self.after_init(load_views)

    def ready(self):
        print('Module loaded: ', self.__module__)
        pass

    def after_init(self, callback):
        callback(self)
        self.ready()


class ModularAPI:
    def __init__(self, **kwargs):
        config_path = os.environ.get('FASTAPI_SETTINGS_MODULE', None)
        settings = import_settings(config_path)
        app = FastAPI(**kwargs)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=getattr(settings, 'TRUSTED_ORIGINS', []),
            allow_origin_regex=getattr(settings, 'LOCALHOST', 'http(s)?://localhost(:[0-9]+)?'),
        )
        self.router = APIRouter()
        self.app = app
        self.settings = settings

        load_modules(self)

    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)

