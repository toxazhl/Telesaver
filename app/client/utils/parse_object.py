import logging
from datetime import datetime
from typing import Any

from pyrogram import Client, enums, types
from pyrogram.enums.auto_name import AutoName


logger = logging.getLogger(__name__)


types_need_client = (
    "CallbackQuery",
    "GameHighScore",
    "ChosenInlineResult",
    "InlineQuery",
    "Animation",
    "Audio",
    "Contact",
    "Dice",
    "Document",
    "Game",
    "Location",
    "MessageEntity",
    "MessageReactions",
    "Message",
    "Photo",
    "PollOption",
    "Poll",
    "Reaction",
    "Sticker",
    "StrippedThumbnail",
    "Thumbnail",
    "Venue",
    "VideoNote",
    "Video",
    "Voice",
    "WebPage",
    "ChatAdminWithInviteLinks",
    "ChatJoinRequest",
    "ChatJoiner",
    "ChatMemberUpdated",
    "ChatMember",
    "ChatPhoto",
    "ChatPreview",
    "ChatReactions",
    "Chat",
    "User",
    "Dialog",
    "EmojiStatus",
)

need_enum_parser = ("action", "filter", "media", "service", "status", "type")

parsers = {
    "next_offline_date": datetime.fromisoformat,
    "date": datetime.fromisoformat,
}


def parse_enum(obj: str) -> AutoName:
    raw_enum, value = obj.split(".")
    enum_type = getattr(enums, raw_enum)
    return getattr(enum_type, value)


def parse(
    obj: dict[str, Any], client: None | Client = None
) -> Any:
    try:
        raw_type = obj.pop("_")
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = parse(v, client=client)

            elif isinstance(v, list):
                obj[k] = [parse(it, client=client) for it in v]

            elif k in parsers.keys():
                parser = parsers[k]
                parser(v)

            elif k in need_enum_parser:
                obj[k] = parse_enum(v)

        if raw_type in types_need_client:
            obj["client"] = client

        class_type = getattr(types, raw_type)
        return class_type(**obj)

    except Exception as e:
        logger.error(f"Error parsing object. Object: {obj}")
        raise e
