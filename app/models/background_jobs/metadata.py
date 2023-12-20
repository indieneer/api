from . import Serializable
from typing import Dict, Type
from dataclasses import dataclass


class BaseMetadata(Serializable):
    def __init__(self, **kwargs):
        pass


@dataclass
class EsSeederMetadata(BaseMetadata):
    match_query: str


JOB_METADATA: Dict[str, Type[BaseMetadata]] = {
    "es_seeder": EsSeederMetadata
}
JOB_TYPES = JOB_METADATA.keys()


class JobMetadata:
    """
    Factory class to create metadata objects based on the job type.
    """

    @staticmethod
    def create(job_type: str, **kwargs) -> BaseMetadata:
        """
        Creates a metadata object based on the job type.

        :param job_type: The job type.
        :param kwargs: The metadata.
        :return: The metadata object.
        """
        metadata = JOB_METADATA.get(job_type)

        if metadata is None:
            raise ValueError(f"Unsupported job type: {job_type}")

        return metadata(**kwargs)
