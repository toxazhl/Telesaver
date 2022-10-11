import glob
import logging
from datetime import datetime

from pyrogram import Client
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
)


logger = logging.getLogger(__name__)


def find_file(file_id: str) -> None:
    path = f"app/files/{file_id}.*"
    for infile in glob.glob(path):
        print(infile)
        return infile


async def copy(
    client: Client,
    message: Message,
    chat_id: int | str,
    disable_notification: None | bool = None,
    reply_to_message_id: None | int = None,
    schedule_date: None | datetime = None,
    protect_content: None | bool = None,
    reply_markup: None
    | InlineKeyboardMarkup
    | ReplyKeyboardMarkup
    | ReplyKeyboardRemove
    | ForceReply = None,
) -> Message | list[Message]:
    kwargs = dict(
        chat_id=chat_id,
        disable_notification=disable_notification,
        reply_to_message_id=reply_to_message_id,
        schedule_date=schedule_date,
        protect_content=protect_content,
        reply_markup=message.reply_markup
        if reply_markup is object
        else reply_markup,
    )

    if message.service:
        logger.warning(
            f"Service messages cannot be copied. "
            f"chat_id: {message.chat.id}, message_id: {message.id}"
        )
    elif message.game and not await message._client.storage.is_bot():
        logger.warning(
            f"Users cannot send messages with Game media type. "
            f"chat_id: {message.chat.id}, message_id: {message.id}"
        )
    elif message.empty:
        logger.warning("Empty messages cannot be copied")

    elif message.text:
        send_media = client.send_message
        kwargs.update(
            text=message.text,
            entities=message.entities,
        )
    elif message.media:
        if message.photo:
            send_media = client.send_photo
            kwargs.update(photo=find_file(message.photo.file_id))
        elif message.audio:
            send_media = client.send_audio
            kwargs.update(audio=find_file(message.audio.file_id))
        elif message.document:
            send_media = client.send_document
            kwargs.update(document=find_file(message.document.file_id))
        elif message.video:
            send_media = client.send_video
            kwargs.update(video=find_file(message.video.file_id))
        elif message.animation:
            send_media = client.send_animation
            kwargs.update(animation=find_file(message.animation.file_id))
        elif message.voice:
            send_media = client.send_voice
            kwargs.update(voice=find_file(message.voice.file_id))
        elif message.sticker:
            send_media = client.send_sticker
            kwargs.update(sticker=find_file(message.sticker.file_id))
        elif message.video_note:
            send_media = client.send_video_note
            kwargs.update(video_note=find_file(message.video_note.file_id))
        elif message.contact:
            send_media = client.send_contact
            kwargs.update(
                phone_number=message.contact.phone_number,
                first_name=message.contact.first_name,
                last_name=message.contact.last_name,
                vcard=message.contact.vcard,
            )
        elif message.location:
            send_media = client.send_location
            kwargs.update(
                latitude=message.location.latitude,
                longitude=message.location.longitude,
            )
        elif message.venue:
            send_media = client.send_venue
            kwargs.update(
                latitude=message.venue.location.latitude,
                longitude=message.venue.location.longitude,
                title=message.venue.title,
                address=message.venue.address,
                foursquare_id=message.venue.foursquare_id,
                foursquare_type=message.venue.foursquare_type,
            )
        elif message.poll:
            send_media = client.send_poll
            kwargs.update(
                question=message.poll.question,
                options=[opt.text for opt in message.poll.options],
            )
        elif message.game:
            send_media = client.send_game
            kwargs.update(
                game_short_name=message.game.short_name,
            )
        else:
            raise ValueError("Unknown media type")

        if message.caption:
            kwargs.update(
                caption=message.caption,
                caption_entities=message.caption_entities,
            )
    else:
        raise ValueError("Can't copy this message")

    return await send_media(**kwargs)
