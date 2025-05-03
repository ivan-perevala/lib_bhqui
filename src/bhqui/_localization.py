# SPDX-FileCopyrightText: 2020-2024 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import bpy

__all__ = (
    "update_localization",
    "request_localization_from_file",
)


def update_localization(*, module: str, langs: dict):
    """
    Updates localization in realtime.

    :param module: Extension module name.
    :type module: str
    :param langs: Updated language dictionary to be used.
    :type langs: dict
    """

    try:
        bpy.app.translations.unregister(module)
    except RuntimeError:
        pass
    else:
        bpy.app.translations.register(module, langs)


def request_localization_from_file(*, module: str, langs: dict, msgctxt: str, src: str, dst: dict[str, str]):
    """
    Updates localization from files. Might be useful, for example, for `README.md` or `LICENSE` files translation.

    :param module: Extension module name.
    :type module: str
    :param langs: Language dictionary to be updated.
    :type langs: dict
    :param msgctxt: Translation context.
    :type msgctxt: str
    :param src: Original file.
    :type src: str
    :param dst: Dictionary in format: {language: path_to_translated_file}.
    :type dst: dict[str, str]
    :return: Original file text data.
    :rtype: str
    """

    for lang, translations in langs.items():
        if lang in dst:
            for item in translations.keys():
                if item[0] == msgctxt:
                    return item[1]

    src_data = ""
    with open(src, 'r', encoding='utf-8') as src_file:
        src_data = src_file.read()
        for dst_locale, dst_filename in dst.items():
            with open(dst_filename, 'r', encoding='utf-8') as dst_file:
                if dst_locale not in langs:
                    langs[dst_locale] = dict()
                langs[dst_locale][(msgctxt, src_data)] = dst_file.read()

    update_localization(module=module, langs=langs)
    return src_data
