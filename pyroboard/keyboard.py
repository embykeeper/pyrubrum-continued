# Pyroboard - Keyboard manager for Pyrogram
# Copyright (C) 2020 Hearot <https://github.com/hearot>
#
# This file is part of Pyroboard.
#
# Pyroboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyroboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyroboard. If not, see <http://www.gnu.org/licenses/>.

from .base_handler import BaseHandler
from .button import Button
from pyrogram import InlineKeyboardMarkup
from typing import List


class Keyboard(InlineKeyboardMarkup):
    def __init__(self, inline_keyboard: List[List[Button]],
                 handler: BaseHandler, callback_query_id: str):
        super().__init__(
            handler.process_keyboard(inline_keyboard,
                                     str(callback_query_id)))
