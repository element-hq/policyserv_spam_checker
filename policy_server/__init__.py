#
# This file is licensed under the Affero General Public License (AGPL) version 3.
#
# Copyright (C) 2025 New Vector, Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# See the GNU Affero General Public License for more details:
# <https://www.gnu.org/licenses/agpl-3.0.html>.
#

import logging
from synapse.module_api import NOT_SPAM, UserID
from synapse.module_api.errors import Codes
from datetime import date

logger = logging.getLogger(__name__)

SPAM = Codes.FORBIDDEN

DISABLE_DATE = date(2025, 5, 21)  # May 21st, 2025

class Checker:
    @staticmethod
    def parse_config(config):
        return config # not parsed

    def __init__(self, config, api):
        self.api = api

        self.fallback_user_id = config.get("fallback_user_id", "@abuse:matrix.org")
        self.fallback_room_ids = config.get("fallback_room_ids", [])

        api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )

        # XXX: DANGER - Using unstable API (_hs).
        self.federation_client = api._hs.get_federation_client()
        self.event_auth_handler = api._hs.get_event_auth_handler()

    async def check_event_for_spam(self, event):
        try:
            # Early return to save some CPU on forgotten installs
            if date.today() >= DISABLE_DATE:
                return NOT_SPAM

            # TODO: State events should also be going to the policy server
            if event.is_state():
                return NOT_SPAM

            # Find the room's policy server, if any
            state = await self.api.get_state_events_in_room(event.room_id, [("org.matrix.msc4284.policy", "")])
            if len(state) != 1:
                return NOT_SPAM  # not using MSC4284

            ps_config = list(state)[0]
            ps = ps_config.content.get("via", "")
            if ps is None or not isinstance(ps, str):
                return NOT_SPAM  # not using MSC4284

            if ps == self.api.server_name:
                return NOT_SPAM  # the homeserver itself is not capable of this check at the moment

            if not UserID.is_valid("@x:" + ps):
                return NOT_SPAM  # not a valid domain name, so not using MSC4284

            # Check to see if the server is in the room
            # XXX: DANGER - Using unstable API
            is_in_room = await self.event_auth_handler.is_host_in_room(event.room_id, ps)
            if not is_in_room:
                return NOT_SPAM  # nothing to do

            # XXX: DANGER - Using guts of federation_client, an unsafe thing
            res = await self.federation_client.transport_layer.client.post_json(
                destination=ps,
                path=f"/_matrix/policy/unstable/org.matrix.msc4284/event/{event.event_id}/check",
                data=event.get_pdu_json(),
                ignore_backoff=True,
            )
            logger.debug(res)
            if res["recommendation"] != "ok":
                await self.do_redact_if_needed(event)
                return SPAM
            return NOT_SPAM
        except Exception as e:
            logger.exception("Failed to check event against policy server (assuming NOT_SPAM): %s", e)
            return NOT_SPAM

    async def do_redact_if_needed(self, event):
        if self.api.is_mine(event["sender"]):
            logger.info("Not redacting local event because they got told no already")
            return  # nothing to do

        if not self.api.is_mine(self.fallback_user_id):
            logger.info("Not redacting remote event because the fallback_user_id is on another server")
            return  # nothing to do

        if event.room_id not in self.fallback_room_ids:
            logger.info("Not redacting remote event because we're not the moderation server for it")
            return  # nothing to do

        logger.info("Redacting remote event due to spam")
        self.api.delayed_background_call(1, self.api.create_and_send_event_into_room, {
            "room_id": event["room_id"],
            "type": "m.room.redaction",
            "sender": self.fallback_user_id,
            "content": {
                "redacts": event.event_id,
            },
            "redacts": event.event_id,
        }, desc="policy_server_send_redact")
