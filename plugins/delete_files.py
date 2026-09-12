import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS, LOG_CHANNEL  # LOG_CHANNEL ഇവിടെ ഇമ്പോർട്ട് ചെയ്യുക
from database.ia_filterdb import Media, unpack_new_file_id

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Delete Multiple files from database and send log to Telegram"""

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    # 1. First Attempt: Delete using File ID
    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    
    if result.deleted_count:
        log_msg = f"🗑️ **File Deleted (ID Match):**\n• Name: `{media.file_name}`\n• Size: `{media.file_size}`"
        logger.info('File is successfully deleted from database.')
        await bot.send_message(chat_id=LOG_CHANNEL, text=log_msg)
    
    else:
        # 2. Second Attempt: Clean file name and delete many
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        
        if result.deleted_count:
            log_msg = f"🗑️ **Files Deleted (Clean Name Match):**\n• Count: `{result.deleted_count}`\n• Filter Name: `{file_name}`"
            logger.info('File is successfully deleted from database.')
            await bot.send_message(chat_id=LOG_CHANNEL, text=log_msg)
        
        else:
            # 3. Third Attempt: Original file name match
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            
            if result.deleted_count:
                log_msg = f"🗑️ **Files Deleted (Exact Name Match):**\n• Count: `{result.deleted_count}`\n• Name: `{media.file_name}`"
                logger.info('File is successfully deleted from database.')
                await bot.send_message(chat_id=LOG_CHANNEL, text=log_msg)
            
            else:
                log_msg = f"❌ **File Not Found in DB:**\n• Name: `{media.file_name}`"
                logger.info('File not found in database.')
                await bot.send_message(chat_id=LOG_CHANNEL, text=log_msg)
