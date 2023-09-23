from app.services import ServicesExtension

from . import (
    create_root_profile
)


def run(services: ServicesExtension):
    create_root_profile.run(services)
