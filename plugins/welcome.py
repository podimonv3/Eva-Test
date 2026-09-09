import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# 🖼️ പ്രൊഫൈൽ ഫോട്ടോ ഇല്ലാത്തവർക്കായി ഉപയോഗിക്കേണ്ട വെൽക്കം ഇമേജ് ലിങ്ക്
DEFAULT_WELCOME_IMAGE_URL = "https://example.com"

# 🔄 അവസാനത്തെ വെൽക്കം മെസ്സേജ് ഐഡി ട്രാക്ക് ചെയ്യാനുള്ള ഡിക്ഷ്ണറി
# ഫോർമാറ്റ്: { chat_id: last_message_id }
LAST_WELCOME_MESSAGES = {}

@Client.on_message(filters.new_chat_members)
async def delete_old_and_send_welcome(client: Client, message: Message):
    chat_id = message.chat.id

    for member in message.new_chat_members:
        if member.is_self:
            continue

        user_id = member.id
        user_mention = member.mention

        # 🗑️ പുതിയ ആൾ വരുമ്പോൾ പഴയ വെൽക്കം മെസ്സേജ് ഡിലീറ്റ് ചെയ്യാനുള്ള ഭാഗം
        if chat_id in LAST_WELCOME_MESSAGES:
            try:
                old_msg_id = LAST_WELCOME_MESSAGES[chat_id]
                await client.delete_messages(chat_id=chat_id, message_ids=old_msg_id)
            except Exception as e:
                # മെസ്സേജ് മുൻപേ ഡിലീറ്റ് ആയിട്ടുണ്ടെങ്കിലോ പെർമിഷൻ ഇല്ലെങ്കിലോ എറർ വരാതിരിക്കാൻ
                print(f"Error deleting old welcome message: {e}")

        # 🌟 മലയാളം വെൽക്കം ടെക്സ്റ്റ് (ക്യാപ്ഷൻ)
        welcome_text = (
            f"Hai {user_mention}❤️,\n"
            f"Welcome To\n"
            f"★📣**ഉർവശി തിയേറ്റേഴ്സ്**™📣★,\n\n"
            f"♻️**മടിക്കേണ്ട കൂട്ടുകാർക്കും ഷെയർ ചെയ്തോ ഗ്രൂപ്പ് പവർ ആകട്ടെ...**\n\n"
            f"```\n"
            f"Movie Request Format ❞\n\n"
            f"Bhramam ❌\n"
            f"Bhramam 2020 ✅\n"
            f"```\n"
            f"**ഇങ്ങനെ റിക്വസ്റ്റ് ചെയ്തിട്ടും മൂവി ലഭിച്ചില്ലെങ്കിൽ**\n"
            f"`/request Bhramam 2020`\n"
            f"**(ഉപയോഗിക്കുക)**\n\n"
            f"⚠️ **NB: [Movie+Year] Format -ൽ കിട്ടിയില്ലെങ്കിൽ മാത്രം** ❞\n\n"
            f"📌**(Must Join)**👇"
        )

        # 🔘 ഇൻലൈൻ ബട്ടണുകൾ
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📍 Channel 📍", url="https://t.me/UrvashiTheaters_Main")],
                [InlineKeyboardButton("💬 Group 💬", url="https://t.me/+Jtn9PDMtLvthMWE1:same")],
                [InlineKeyboardButton("📜 RULE$ 📜", url="https://telegra.ph/RULES-OF-12-22")]
            ]
        )

        photo_path = f"welcome_pfp_{user_id}.jpg"
        pfp_downloaded = False

        # 🔍 MAXIMUM EFFORT: പ്രൊഫൈൽ ഫോട്ടോ ഡൗൺലോഡ് ചെയ്യാൻ ശ്രമിക്കുന്നു
        try:
            user_info = await client.get_users(user_id)
            if user_info.photo:
                await client.download_media(user_info.photo.big_file_id, file_name=photo_path)
                pfp_downloaded = True
        except Exception as e:
            print(f"Primary photo download failed: {e}")
            if not pfp_downloaded:
                try:
                    async for photo in client.get_chat_photos(user_id, limit=1):
                        await client.download_media(photo.file_id, file_name=photo_path)
                        pfp_downloaded = True
                except Exception as pfp_err:
                    print(f"Fallback photo download failed: {pfp_err}")

        # 📤 വെൽക്കം കാർഡ് അയക്കുന്നു
        sent_message = None
        try:
            if pfp_downloaded and os.path.exists(photo_path):
                sent_message = await message.reply_photo(
                    photo=photo_path,
                    caption=welcome_text,
                    reply_markup=reply_markup
                )
                os.remove(photo_path)
            else:
                sent_message = await message.reply_photo(
                    photo=DEFAULT_WELCOME_IMAGE_URL,
                    caption=welcome_text,
                    reply_markup=reply_markup
                )

            # 💾 ഇപ്പോൾ അയച്ച പുതിയ മെസ്സേജിന്റെ ID ഓർമ്മയിൽ സൂക്ഷിക്കുന്നു
            if sent_message:
                LAST_WELCOME_MESSAGES[chat_id] = sent_message.id

        except Exception as e:
            print(f"Error sending welcome message: {e}")
