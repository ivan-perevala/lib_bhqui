# SPDX-FileCopyrightText: 2020-2024 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
from typing import Iterable

import bpy
import bpy.utils.previews
from bpy.types import ImagePreview

__all__ = (
    "IconsCache",
)


class IconsCache:
    """
    Abstract icons cache class.
    """

    _directory: str = ""
    "Icons source directory"

    _cache: dict[str, int] = dict()
    "Icons map: `identifier: icon_value`"
    
    _pcoll_cache: None | bpy.utils.previews.ImagePreviewCollection = None
    "Image icons cache"

    @classmethod
    def _intern_initialize_from_data_files(cls, *, directory: str, ids: Iterable[str]):
        for identifier in ids:
            try:
                icon_value = bpy.app.icons.new_triangles_from_file(os.path.join(directory, f"{identifier}.dat"))
            except ValueError:
                # log.warning(f"Unable to load icon \"{identifier}\"")
                icon_value = 0

            cls._cache[identifier] = icon_value

    @classmethod
    def _intern_initialize_from_image_files(cls, *, directory: str, ids: Iterable[str]):
        pcoll = bpy.utils.previews.new()
        for identifier in ids:
            prv: ImagePreview = pcoll.load(identifier, os.path.join(directory, f"{identifier}.svg"), 'IMAGE')
            cls._cache[identifier] = prv.icon_id
        cls._pcoll_cache = pcoll

    @classmethod
    def initialize(cls, *, directory: str, data_identifiers: Iterable[str], image_identifiers: Iterable[str]):
        """
        Icons cache initialization method.

        :param directory: Source icons directory. It may be images and data files.
        :type directory: str
        :param data_identifiers: Data file icons identifiers.
        :type data_identifiers: Iterable[str]
        :param image_identifiers: Image icon identifiers.
        :type image_identifiers: Iterable[str]
        """

        if cls._cache and cls._directory == directory:
            return

        cls.release()

        if directory:
            cls._intern_initialize_from_data_files(directory=directory, ids=data_identifiers)
            cls._intern_initialize_from_image_files(directory=directory, ids=image_identifiers)

        cls._directory = directory

    @classmethod
    def release(cls):
        """
        Releases icons cache. Should be used in extension ``unregister`` function.
        """

        if cls._pcoll_cache is not None:
            bpy.utils.previews.remove(cls._pcoll_cache)
            cls._pcoll_cache = None

        cls._cache.clear()

    @classmethod
    def get_id(cls, identifier: str) -> int:
        """
        Retrieves `icon_value` to be used in UI using icon identifier.

        :param identifier: Icon identifier, one of provided during cache initialization.
        :type identifier: str
        :return: Icon value to be used for UI calls.
        :rtype: int
        """
        return cls._cache.get(identifier, 0)
