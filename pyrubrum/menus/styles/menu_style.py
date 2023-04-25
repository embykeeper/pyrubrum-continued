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

from itertools import islice
from typing import Any, Dict, List, Optional, Set, Union

from pyrogram import Client

from .base_style import BaseStyle


class MenuStyle(BaseStyle):
    """Provide a standard keyboard with which you can refer to children and
    parent menus effortlessly.

    Parameters:
        back_text (Optional[str]): The text which will be displayed
            inside the button that lets the user go back to the parent
            menu. Defaults to "🔙".
        limit (Optional[int]): The limit of buttons per row. Defaults to ``2``.
    """

    def __init__(
        self,
        back_text: Optional[str] = "🔙",
        back_to: str = None,
        back_enable: bool = True,
        extras: List = [],
        limit: Optional[int] = 2,
    ):
        self.back_text = back_text
        self.back_to = back_to
        self.back_enable = back_enable
        self.extras = extras
        self.limit = limit

    async def generate(
        self,
        handler: "Handler",  # noqa
        client: Client,
        context: Any,
        parameters: Dict[str, Any],
        menu: "Menu",  # noqa
    ) -> List[List["Button"]]:
        """Provide a keyboard, filled with all the buttons which refer to the
        children menus and a special button for linking the user to the parent
        menu, if any.

        Parameters:
            handler (BaseHandler): The handler which coordinates the management
                of the menus.
            client (Client): The client which is linked to the handler.
            context (Union[CallbackQuery, Message]): The context for which the
                button is generated.
            parameters (Dict[str, Any]): The parameters which were passed to
                the handler.
            menu (Menu): The menu the keyboard is being built for.

        Returns:
            pyrogram.InlineKeyboardMarkup: The generated inline keyboard,
            which is then displayed to the user.
        """
        parent, children = handler.get_family(menu.menu_id)

        keyboard = []

        if children:
            iterable = iter(children)
            keyboard = list(
                iter(
                    lambda: list(
                        map(
                            lambda child: child.button(handler, client, context, parameters),
                            islice(iterable, self.limit),
                        )
                    ),
                    [],
                )
            )

        extras = [handler[e] if isinstance(e, str) else e for e in self.extras]
        buttons = [m.button(handler, client, context, parameters) for m in extras]
        if buttons:
            keyboard += [buttons]

        if self.back_to:
            parent = handler[self.back_to]
        
        if parent and self.back_enable:
            parent_button = parent.button(handler, client, context, parameters)
            parent_button.name = self.back_text
            if buttons:
                keyboard += [[parent_button]]

        return keyboard
