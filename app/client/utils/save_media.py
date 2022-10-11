from pyrogram import Client
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
from pyrogram.types import Message


available_media = (
    "audio",
    "document",
    "photo",
    "sticker",
    "animation",
    "video",
    "voice",
    "video_note",
    "new_chat_photo",
)


async def save(client: Client, message: Message):
    for kind in available_media:
        media = getattr(message, kind, None)
        if media is not None:
            break
    else:
        return

    file_id = media.file_id
    file_name = getattr(media, "file_name", "")
    mime_type = getattr(media, "mime_type", "")
    file_id_obj = FileId.decode(media.file_id)
    file_type = file_id_obj.file_type

    if file_name and "." in file_name:
        extension = file_name.rsplit(".", 1)[1]
    else:
        guessed_extension = client.guess_extension(mime_type)

        if file_type in PHOTO_TYPES:
            extension = "jpg"
        elif file_type == FileType.VOICE:
            extension = guessed_extension or "ogg"
        elif file_type in (
            FileType.VIDEO,
            FileType.ANIMATION,
            FileType.VIDEO_NOTE,
        ):
            extension = guessed_extension or "mp4"
        elif file_type == FileType.DOCUMENT:
            extension = guessed_extension or "zip"
        elif file_type == FileType.STICKER:
            extension = guessed_extension or "webp"
        elif file_type == FileType.AUDIO:
            extension = guessed_extension or "mp3"
        else:
            extension = ".unknown"

    file_name = f"{file_id}.{extension}"

    await message.download(file_name=f"files/{file_name}", block=False)
