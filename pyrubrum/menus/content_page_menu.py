from asyncio import iscoroutinefunction
import asyncio
from typing import Any, Dict, Optional, Tuple, Union

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.types import CallbackQuery, Message
from pyrubrum.keyboard.element import Element
from pyrubrum.menus.styles import PageStyle
from pyrubrum.types import Types

from .page_menu import PageMenu


class ContentPageMenu(PageMenu):
    def __init__(
        self,
        name: str,
        menu_id: str,
        content: Tuple[int, str],
        header: str = None,
        footer: str = None,
        deep_link: Optional[bool] = False,
        default: Optional[bool] = False,
        message_filter: Optional[Filter] = None,
        preliminary: Types.Preliminary = None,
        style: PageStyle = PageStyle(limit=5, limit_items=10),
        **kwargs,
    ):
        PageMenu.__init__(
            self,
            name,
            menu_id,
            content,
            items=None,
            deep_link=deep_link,
            default=default,
            message_filter=message_filter,
            preliminary=preliminary,
            style=style,
            **kwargs,
        )

        self.header = header
        self.footer = footer
        self.entries = []

    @staticmethod
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx : min(ndx + n, l)]

    async def on_update(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Union[CallbackQuery, Message],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        element_id = parameters.get("element_id", "")
        if element_id == "":
            page = int(parameters.get(f"page_{self.menu_id}", 0))
        elif parameters.get('same_menu', False):
            page = int(element_id)
        else:
            page = 0

        content = await self.parse(self.content, handler, client, context, parameters)
        if content is None:
            return

        if (not self.entries) or (not parameters.get("same_menu", False)):
            self.entries = list(
                self.batch(
                    content,
                    self.style.limit_items,
                )
            )

        if self.entries:
            for i, (c, t, x) in enumerate(self.entries[page]):
                self.entries[page][i] = (await self.parse(c, handler, client, context, parameters), t, x)

        text = "\n".join([c for c, t, x in self.entries[page]]) if self.entries else ''
        if self.header:
            text = await self.parse(self.header, handler, client, context, parameters) + "\n" + text
        if self.footer:
            text = text + "\n" + await self.parse(self.footer, handler, client, context, parameters)
        await self.call_preliminary(handler, client, context, parameters)

        self.items = [Element(t, x) for page in self.entries for c, t, x in page]
        keyboard = await self.keyboard(handler, client, context, parameters)

        if isinstance(context, CallbackQuery):
            await context.edit_message_text(text, reply_markup=keyboard, **self.kwargs)
        elif isinstance(context, Message):
            await context.reply_text(text, reply_markup=keyboard, **self.kwargs)
