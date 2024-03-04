from app.models import ModelsExtension
from app.services import ServicesExtension

from . import (
    create_root_profile
)


def run(services: ServicesExtension, models: ModelsExtension):
    create_root_profile.run(models)
