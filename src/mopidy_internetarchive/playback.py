from __future__ import annotations

from typing import TYPE_CHECKING

from mopidy import backend
from mopidy.types import Uri

from . import translator

if TYPE_CHECKING:
    from .backend import InternetArchiveBackend


class InternetArchivePlaybackProvider(backend.PlaybackProvider):
    backend: InternetArchiveBackend  # type: ignore[assignment]

    def translate_uri(self, uri: str) -> Uri | None:
        identifier, filename, _ = translator.parse_uri(uri)
        return Uri(self.backend.client.geturl(identifier, filename))
