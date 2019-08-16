# -*- coding: future_fstrings -*-

#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging, time
from io import BytesIO

from .. import loader, utils

logger = logging.getLogger(__name__)

def register(cb):
    cb(TestMod())

class TestMod(loader.Module):
    """Self-tests"""
    def __init__(self):
        self.name = "Tester"

    async def pingcmd(self, message):
        """Does nothing"""
        await message.edit('Pong')

    async def dumpcmd(self, message):
        """Use in reply to get a dump of a message"""
        if not message.is_reply:
            return
        await message.edit("<code>"+utils.escape_html((await message.get_reply_message()).stringify())+"</code>")

    async def logscmd(self, message):
        """.logs <level>
           Dumps logs. Loglevels below WARNING may contain personal info."""
        args = utils.get_args(message)
        if not len(args) == 1:
            await message.edit("<code>Please specify verbosity as an integer or string</code>")
            return
        try:
            lvl = int(args[0])
        except ValueError:
            # It's not an int. Maybe it's a loglevel
            lvl = getattr(logging, args[0].upper(), None)
        if lvl is None:
            await message.edit('<code>Invalid loglevel. Please refer to </code><a href="https://docs.python.org/3/library/logging.html#logging-levels">the docs</a><code>.</code>')
            return
        await message.edit("<code>Uploading logs...</code>")
        [handler] = logging.getLogger().handlers
        logs = ("\n".join(handler.dumps(lvl))).encode("utf-8")
        if not len(logs) > 0:
            await message.edit(f"<code>You don't have any logs at verbosity {lvl}.</code>")
            return
        logs = BytesIO(logs)
        logs.name = "ftg-logs.txt"
        await message.client.send_file(message.to_id, logs, caption=f"<code>friendly-telegram logs with verbosity {lvl}")
        await message.delete()

    async def suspendcmd(self, message):
        """.suspend <time>
           Suspends the bot for N seconds"""
        # Blocks asyncio event loop, preventing ANYTHING happening (except multithread ops, but they will be blocked on return).
        try:
            logger.info("Good Night.")
            time.sleep(int(utils.get_args_raw(message)))
            logger.info("Good Morning.")
        except ValueError:
            await message.edit("<code>Invalid time to suspend</code>")
