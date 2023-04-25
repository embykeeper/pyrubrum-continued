# Pyrubrum - An intuitive framework for creating Telegram bots
# Copyright (C) 2020 Hearot <https://github.com/hearot>
#
# This file is part of Pyrubrum.
#
# Pyrubrum is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrubrum is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyrubrum. If not, see <https://www.gnu.org/licenses/>.

from asyncio import iscoroutinefunction
from typing import Any, Callable, Dict, Iterable, Optional, Union

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InputMedia, Message
from pyrubrum.keyboard import Keyboard
from pyrubrum.menus.styles import MenuStyle
from pyrubrum.types import Types

from .base_menu import BaseMenu


class Menu(BaseMenu):
    """Implementation of a menu who has got, by definition, a content to display
    (i.e. what the user will see by accessing it), a name and a style.

    See Also:
        For complete examples of styles you can make use of:

        * `MenuStyle`
        * `PageStyle` (although it is recommended to use it only
          with `PageMenu`)

    Parameters:
        name (str): The name you give to the menu, which will be used as
            the text of callback button, if needed. See `BaseMenu` for more
            information.
        menu_id (str): The unique identifier given to the menu, which will
            refer unequivocally to this entity. The hash for this class is
            generated relying on the content of this field. Avoid using ``0``
            as it is used for buttons whose purpose is only related to
            design (i.e. they do not point to any menu,
            see :term:`Null-pointer button`). See `BaseMenu` for more
            information.
        content (Types.Content): What will be displayed whenever a user
            accesses this menu. Both text and media can be provided. A
            function that returns such values can be provided as well
            and must follow the this arguments pattern::

                func(handler, client, context, parameters)

        deep_link (Optional[bool]): If this menu shall be reached by a
            deep-link whose payload is the identifier of this instance.
            Defaults to ``False``.
        default (Optional[bool]): If this menu shall be displayed if no
            other :term:`top-level menu <Top-level menu>` has been matched.
            It works only if this menu is a :term:`top-level <Top-level menu>`
            one.
        message_filter (Optional[Filter]): A filter for telling Pyrogram
            when a message should be associated to this menu. It works only
            for :term:`top-level menus <Top-level menu>` (see `Handler.setup`).
            Defaults to ``None``, which automatically makes this menu reachable
            when the user texts a message that follows this pattern::

                /[MENU_ID]

        preliminary (Types.Preliminary): A function which is executed each time
            before doing anything else in `on_callback` and `on_message`.
            You can provide a list of such functions as well, which will be
            executed following the same order as the one of the list.
            Defaults to ``None``, which means that no function is going to
            be executed.
        style (BaseStyle): The class which generates the keyboard for this
            function following a certain style. Defaults to `MenuStyle()`.

    Note:
        This implementation is compatible with a non-parameterized handler.
    """

    def __init__(
        self,
        name: str,
        menu_id: str,
        content: Union[
            Union[InputMedia, str],
            Callable[
                [
                    "Handler",
                    Client,
                    Union[CallbackQuery, Message],
                    Dict[str, Any],
                ],
                Union[InputMedia, str],
            ],
        ],
        deep_link: Optional[bool] = False,
        default: Optional[bool] = False,
        message_filter: Optional[Filter] = None,
        preliminary: Types.Preliminary = None,
        style: MenuStyle = MenuStyle(),
        **kwargs
    ):
        BaseMenu.__init__(self, name, menu_id)
        self.content = content
        self.deep_link = deep_link
        self.default = default
        self.message_filter = message_filter
        self.preliminary = preliminary
        self.style = style
        self.kwargs = kwargs

    @staticmethod
    async def parse(var, handler, client, context, parameters):
        if iscoroutinefunction(var):
            return await var(handler, client, context, parameters)
        elif callable(var):
            return var(handler, client, context, parameters)
        else:
            return var

    async def call_preliminary(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Union[CallbackQuery, Message],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        if self.preliminary:
            preliminary = (
                [self.preliminary] if not isinstance(self.preliminary, Iterable) else self.preliminary
            )
            for func in preliminary:
                if iscoroutinefunction(func):
                    await func(self, handler, client, context, parameters)
                elif callable(func):
                    func(self, handler, client, context, parameters)

    async def on_update(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Union[CallbackQuery, Message],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        await self.call_preliminary(handler, client, context, parameters)

        keyboard = await self.keyboard(handler, client, context, parameters)
        content = await self.parse(self.content, handler, client, context, parameters)
        if content is None:
            return

        if isinstance(context, Message):
            if isinstance(content, InputMedia):
                await context.reply_cached_media(
                    file_id=content.media, caption=content.caption, reply_markup=keyboard, **self.kwargs
                )
            else:
                await context.reply_text(content, reply_markup=keyboard, **self.kwargs)
        elif isinstance(context, CallbackQuery):
            if isinstance(content, InputMedia):
                await context.edit_message_media(content, reply_markup=keyboard)
            else:
                await context.edit_message_text(content, reply_markup=keyboard, **self.kwargs)

    async def on_callback(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Union[CallbackQuery, Message],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        return await self.on_update(handler, client, context, parameters)

    async def on_message(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Union[CallbackQuery, Message],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        return await self.on_update(handler, client, context, parameters)

    async def keyboard(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Union[CallbackQuery, Message],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> InlineKeyboardMarkup:
        """Provide a keyboard using the chosen style in `Menu.style`.

        Parameters:
            handler (BaseHandler): The handler which coordinates the management
                of the menus.
            client (Client): The client which is linked to the handler.
            context (Union[CallbackQuery, Message]): The context for which the
                button is generated.
            parameters (Dict[str, Any]): The parameters which were passed to
                the handler.

        Returns:
            pyrogram.InlineKeyboardMarkup: The generated inline keyboard,
            which is then displayed to the user.
        """

        keyboard = await self.style.generate(handler, client, context, parameters, self)

        if isinstance(context, Message):
            return (
                Keyboard(
                    keyboard,
                    handler,
                    str(context.id) + str(context.from_user.id),
                    context.chat.id,
                )
                if keyboard
                else None
            )
        elif isinstance(context, CallbackQuery):
            return Keyboard(keyboard, handler, context.id, context.message.chat.id) if keyboard else None
