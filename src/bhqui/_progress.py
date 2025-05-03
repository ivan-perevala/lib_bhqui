# SPDX-FileCopyrightText: 2020-2025 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Generator

import bpy
from bl_ui import space_statusbar
from bpy.types import Context, PropertyGroup, STATUSBAR_HT_header, UILayout, WindowManager
from bpy.props import StringProperty, FloatProperty, BoolProperty, IntProperty, CollectionProperty

from . _unique_name import eval_unique_name

__all__ = (
    "progress",
)


def _update_statusbar():
    bpy.context.workspace.status_text_set(text=None)


class progress:
    """
    Displays progressbar in statusbar.

    :cvar int PROGRESS_BAR_UI_UNITS: UI units [4...12] for each progressbar (label and icon size does not count). 6 by default (readonly).

    .. versionadded:: 3.3
    """

    _is_drawn = False
    _attrname = ""

    class ProgressPropertyItem(PropertyGroup):
        """
        Single progressbar indicator.
        """

        identifier: StringProperty(
            maxlen=64,
            options={'HIDDEN'},
        )
        """
        Progressbar identifier name.

        .. versionadded:: 3.6
        """

        def _common_value_update(self, context: Context) -> None:
            _update_statusbar()

        valid: BoolProperty(
            default=True,
            update=_common_value_update,
        )

        num_steps: IntProperty(
            min=1,
            default=1,
            subtype='UNSIGNED',
            options={'HIDDEN'},
            update=_common_value_update,
        )
        """
        Number of steps for progress to complete.

        .. versionadded:: 3.3
        """

        step: IntProperty(
            min=0,
            default=0,
            subtype='UNSIGNED',
            options={'HIDDEN'},
            update=_common_value_update,
        )
        """
        Current progress step.

        .. versionadded:: 3.3
        """

        def _get_progress(self):
            return (self.step / self.num_steps) * 100

        def _set_progress(self, _value):
            pass

        value: FloatProperty(
            min=0.0,
            max=100.0,
            precision=1,
            get=_get_progress,
            # set=_set_progress,
            subtype='PERCENTAGE',
            options={'HIDDEN'},
        )
        """
        Evaluated progress, readonly.

        .. versionadded:: 3.3
        """

        label: StringProperty(
            default="Progress",
            options={'HIDDEN'},
            update=_common_value_update,
        )
        """
        Progressbar label.

        .. versionadded:: 3.3
        """

    def _func_draw_progress(self, context: Context):
        layout: UILayout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.template_input_status()
        layout.separator_spacer()
        layout.template_reports_banner()

        if hasattr(WindowManager, progress._attrname):
            layout.separator_spacer()
            for item in progress.valid_progress_items():
                row = layout.row(align=True)

                row.progress(text=item.label, type='RING', factor=item.value / 100)
                item.step += 5
                item.num_steps = 100
                if item.step == 100:
                    item.step = 0

        layout.separator_spacer()

        row = layout.row()
        row.alignment = 'RIGHT'

        row.label(text=context.screen.statusbar_info())

    @classmethod
    def progress_items(cls) -> tuple[ProgressPropertyItem]:
        return tuple(getattr(bpy.context.window_manager, cls._attrname, tuple()))

    @classmethod
    def valid_progress_items(cls) -> Generator[ProgressPropertyItem]:
        """
        Unfinished progressbar items generator.

        :yield: Unfinished progressbar.
        :rtype: Generator[:class:`ProgressPropertyItem`]
        """

        return (_ for _ in cls.progress_items() if _.valid)

    @classmethod
    def _get(cls, *, identifier: str) -> None | ProgressPropertyItem:
        for item in cls.progress_items():
            if item.identifier == identifier:
                return item

    @classmethod
    def get(cls, *, identifier: str = "") -> ProgressPropertyItem:
        item = cls._get(identifier=identifier)
        if item is None:
            if not cls._is_drawn:
                bpy.utils.register_class(progress.ProgressPropertyItem)
                cls._attrname = eval_unique_name(arr=WindowManager, prefix="bhq_", suffix="_progress")

                setattr(
                    WindowManager,
                    cls._attrname,
                    CollectionProperty(type=progress.ProgressPropertyItem, options={'HIDDEN'})
                )
                STATUSBAR_HT_header.draw = cls._func_draw_progress
                _update_statusbar()

            cls._is_drawn = True
            ret: progress.ProgressPropertyItem = getattr(bpy.context.window_manager, cls._attrname).add()
            ret.identifier = identifier
            return ret
        else:
            ret = item
            ret.valid = True
            return ret

    @classmethod
    def complete(cls, *, identifier: str):
        item = cls._get(identifier=identifier)
        if item:
            item.valid = False

            for _ in cls.valid_progress_items():
                return
            cls.release_all()

    @classmethod
    def release_all(cls):
        """
        Removes all progressbars and restores statusbar to original state.
        """

        import importlib
        if not cls._is_drawn:
            return

        assert (cls._attrname)
        delattr(WindowManager, cls._attrname)
        bpy.utils.unregister_class(progress.ProgressPropertyItem)

        importlib.reload(space_statusbar)
        STATUSBAR_HT_header.draw = space_statusbar.STATUSBAR_HT_header.draw
        _update_statusbar()

        cls._is_drawn = False
