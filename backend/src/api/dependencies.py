from functools import lru_cache

from ..services.version_provider import VersionProvider


@lru_cache
def get_version_provider() -> VersionProvider:
    return VersionProvider()

