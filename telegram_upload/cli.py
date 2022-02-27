import asyncio
from typing import Sequence, Tuple, List, TypeVar

import click
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FormattedTextControl, Window, ConditionalMargin, ScrollbarMargin
from prompt_toolkit.widgets import CheckboxList, RadioList
from prompt_toolkit.widgets.base import E, _DialogList

from telegram_upload.utils import aislice

_T = TypeVar("_T")

PAGE_SIZE = 10


async def async_handler(handler, event):
    if handler:
        await handler(event)

    # Tell the application to redraw. We need to do this,
    # because the below event handler won't be able to
    # wait for the task to finish.
    event.app.invalidate()


class IterableDialogList(_DialogList):
    many = False

    def __init__(self, values: Sequence[Tuple[_T, AnyFormattedText]]) -> None:
        pass

    async def _init(self, values: Sequence[Tuple[_T, AnyFormattedText]]) -> None:
        started_values = await aislice(values, PAGE_SIZE)

        # started_values = await aislice(values, PAGE_SIZE)
        if not started_values:
            raise IndexError('Values is empty.')
        self.values = started_values
        # current_values will be used in multiple_selection,
        # current_value will be used otherwise.
        self.current_values: List[_T] = []
        self.current_value: _T = started_values[0][0]
        self._selected_index = 0

        # Key bindings.
        kb = KeyBindings()

        @kb.add("up")
        def _up(event: E) -> None:
            self._selected_index = max(0, self._selected_index - 1)

        @kb.add("down")
        def _down(event: E) -> None:
            async def handler(event):
                if self._selected_index + 1 >= len(self.values):
                    self.values.extend(await aislice(values, PAGE_SIZE))
                self._selected_index = min(len(self.values) - 1, self._selected_index + 1)
            asyncio.get_event_loop().create_task(async_handler(handler, event))

        @kb.add("pageup")
        def _pageup(event: E) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self._selected_index = max(
                    0, self._selected_index - len(w.render_info.displayed_lines)
                )

        @kb.add("pagedown")
        def _pagedown(event: E) -> None:
            async def handler(event):
                w = event.app.layout.current_window
                if self._selected_index + len(w.render_info.displayed_lines) >= len(self.values):
                    self.values.extend(await aislice(values, PAGE_SIZE))
                if w.render_info:
                    self._selected_index = min(
                        len(self.values) - 1,
                        self._selected_index + len(w.render_info.displayed_lines),
                    )
            asyncio.get_event_loop().create_task(async_handler(handler, event))

        @kb.add("enter")
        def _enter(event: E) -> None:
            if self.many:
                event.app.exit(result=self.current_values)
            else:
                event.app.exit(result=self.current_value)

        @kb.add(" ")
        def _enter(event: E) -> None:
            self._handle_enter()

        # Control and window.
        self.control = FormattedTextControl(
            self._get_text_fragments, key_bindings=kb, focusable=True
        )

        self.window = Window(
            content=self.control,
            style=self.container_style,
            right_margins=[
                ConditionalMargin(
                    margin=ScrollbarMargin(display_arrows=True),
                    filter=Condition(lambda: self.show_scrollbar),
                ),
            ],
            dont_extend_height=True,
        )



class IterableCheckboxList(IterableDialogList, CheckboxList):
    many = True


class IterableRadioList(IterableDialogList, RadioList):
    pass


async def show_cli_widget(widget):
    from prompt_toolkit import Application
    from prompt_toolkit.layout import Layout
    app = Application(full_screen=False, layout=Layout(widget), mouse_support=True)
    return await app.run_async()


async def show_checkboxlist(iterator):
    # iterator = map(lambda x: (x, f'{x.text} by {x.chat.first_name}'), iterator)
    try:
        checkbox_list = IterableCheckboxList(iterator)
        await checkbox_list._init(iterator)
    except IndexError:
        click.echo('No items were found. Exiting...', err=True)
        return []
    return await show_cli_widget(checkbox_list)


async def show_radiolist(iterator):
    try:
        radio_list = IterableRadioList(iterator)
        await radio_list._init(iterator)
    except IndexError:
        click.echo('No items were found. Exiting...', err=True)
        return None
    return await show_cli_widget(radio_list)
