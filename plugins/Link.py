from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
import urllib.parse  # URL എൻകോഡ് ചെയ്യാൻ ഇത് ആവശ്യമാണ്

@Client.on_message(filters.command("link") & filters.user(ADMINS))
async def generate_link(client, message):
    command_text = message.text.split(maxsplit=1)
    if len(command_text) < 2:
        await message.reply("Please provide the name for the movie! Example: `/link game of thrones`")
        return
        
    movie_name = command_text[1].replace(" ", "-")
    link = f"https://t.me/Promoviesearcherbot?start=getfile-{movie_name}"
    
    # ലിങ്കിലെ ചിഹ്നങ്ങൾ ടെലിഗ്രാമിന് മനസ്സിലാകുന്ന രീതിയിലേക്ക് മാറ്റുന്നു
    encoded_link = urllib.parse.quote(link, safe='')
    share_url = f"https://telegram.me/share/url?url={encoded_link}"
    
    await message.reply(
        text=f"Here is your link: {link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Share Link", url=share_url)]]
        )
    )
