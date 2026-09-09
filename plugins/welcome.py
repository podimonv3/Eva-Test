import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageDraw, ImageFont, ImageOps
import urllib.request

# നിങ്ങൾക്ക് ഇഷ്ടമുള്ള ഫോട്ടോയുടെ ലിങ്ക് ഇവിടെ നൽകുക
BACKGROUND_LINK = "https://files.catbox.moe/oryxah.jpg"

def create_default_background():
    bg_path = "welcome_bg.jpg"
    
    # ഫയൽ നിലവിൽ ഇല്ലെങ്കിൽ ലിങ്കിൽ നിന്ന് ഡൗൺലോഡ് ചെയ്യും
    if not os.path.exists(bg_path):
        try:
            print("Downloading background image from link...")
            urllib.request.urlretrieve(BACKGROUND_LINK, bg_path)
            
            # ഡൗൺലോഡ് ചെയ്ത ഫോട്ടോ കൃത്യം 800x400 സൈസിലേക്ക് മാറ്റുന്നു
            img = Image.open(bg_path)
            img = img.resize((800, 400))
            img.save(bg_path)
        except Exception as e:
            print(f"Error downloading background image: {e}")
            # ലിങ്ക് വർക്ക് ആയില്ലെങ്കിൽ ബോട്ട് തനിയെ ഒരു ഡിഫോൾട്ട് ബാക്ക്ഗ്രൗണ്ട് ഉണ്ടാക്കും
            img = Image.new("RGB", (800, 400), color="#1e272e")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(20, 20), (780, 380)], outline="#00d2d3", width=5)
            img.save(bg_path)
            
    return bg_path


@Client.on_message(filters.new_chat_members)
async def welcome_card_generator(client: Client, message: Message):
    for member in message.new_chat_members:
        # ബോട്ട് തന്നെയാണ് ഗ്രൂപ്പിൽ കയറിയതെങ്കിൽ വെൽക്കം കാർഡ് ഉണ്ടാക്കേണ്ടതില്ല
        if member.is_self:
            continue

        user_id = member.id
        user_name = member.first_name
        group_name = message.chat.title

        # ഗ്രൂപ്പിലേക്ക് സ്വാഗതം ആശംസിക്കുന്ന ടെക്സ്റ്റ് മെസ്സേജ്
        welcome_text = f"👋 ഹലോ {member.mention},\n**{group_name}** ലേക്ക് ഹാർദ്ദവമായ സ്വാഗതം!"

        # 1. ബാക്ക്ഗ്രൗണ്ട് ഇമേജ് സെറ്റ് ചെയ്യുന്നു
        bg_path = create_default_background()
        background = Image.open(bg_path).convert("RGBA")
        
        # 2. യൂസറുടെ പ്രൊഫൈൽ ചിത്രം ഡൗൺലോഡ് ചെയ്യുന്നു
        avatar_path = f"avatar_{user_id}.jpg"
        pfp_downloaded = False
        
        try:
            # യൂസർക്ക് പ്രൊഫൈൽ പിക്ചർ ഉണ്ടോ എന്ന് നോക്കുന്നു
            async for photo in client.get_chat_photos(user_id, limit=1):
                await client.download_media(photo.file_id, file_name=avatar_path)
                pfp_downloaded = True
        except Exception as e:
            print(f"Error downloading profile photo: {e}")

        # പ്രൊഫൈൽ ചിത്രം ഇല്ലെങ്കിൽ ഒരു ഡിഫോൾട്ട് ചിത്രം ഉപയോഗിക്കുന്നു
        if pfp_downloaded and os.path.exists(avatar_path):
            avatar = Image.open(avatar_path).convert("RGBA")
        else:
            # പ്രൊഫൈൽ ചിത്രം ഇല്ലാത്തവർക്കായി ഒരു താൽക്കാലിക വട്ടം (Circle) നിർമ്മിക്കുന്നു
            avatar = Image.new("RGBA", (150, 150), color="#00d2d3")
        
        # 3. പ്രൊഫൈൽ ചിത്രം വട്ടത്തിലാക്കുന്നു (Circle Crop)
        avatar = avatar.resize((150, 150))
        mask = Image.new("L", (150, 150), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 150, 150), fill=255)
        
        output_avatar = ImageOps.fit(avatar, (150, 150), centering=(0.5, 0.5))
        output_avatar.putalpha(mask)

        # 4. പ്രൊഫൈൽ ചിത്രം ബാക്ക്ഗ്രൗണ്ടിലേക്ക് ഒട്ടിക്കുന്നു (Paste Avatar)
        # (800x400 ചിത്രത്തിന്റെ കൃത്യം നടുവിലായി സെറ്റ് ചെയ്യുന്നു)
        background.paste(output_avatar, (325, 50), output_avatar)

        # 5. കാർഡിൽ പേരും വെൽക്കം ടെക്സ്റ്റും എഴുതുന്നു
        draw = ImageDraw.Draw(background)
        
        # ഡിഫോൾട്ട് ഫോണ്ട് സെറ്റ് ചെയ്യുന്നു (കൂടുതൽ ഭംഗിക്ക് നല്ലൊരു .ttf ഫോണ്ട് ഫയൽ ഉപയോഗിക്കാം)
        try:
            font_title = ImageFont.load_default()
            font_name = ImageFont.load_default()
        except IOError:
            font_title = ImageFont.load_default()
            font_name = ImageFont.load_default()

        # ടെക്സ്റ്റുകൾ ചിത്രത്തിൽ കൃത്യമായി എഴുതുന്നു
        draw.text((400, 240), "WELCOME", fill="#00d2d3", font=font_title, anchor="mm")
        draw.text((400, 280), user_name, fill="#ffffff", font=font_name, anchor="mm")
        draw.text((400, 320), f"To {group_name}", fill="#00d2d3", font=font_title, anchor="mm")

        # 6. പൂർത്തിയായ വെൽക്കം കാർഡ് സേവ് ചെയ്ത് ഗ്രൂപ്പിലേക്ക് അയക്കുന്നു
        output_card_path = f"welcome_card_{user_id}.png"
        final_card = background.convert("RGB")
        final_card.save(output_card_path)

        try:
            # ഗ്രൂപ്പിലേക്ക് ഫോട്ടോ സെൻഡ് ചെയ്യുന്നു
            await message.reply_photo(photo=output_card_path, caption=welcome_text)
        except Exception as e:
            print(f"Error sending welcome card: {e}")

        # 7. താൽക്കാലികമായി നിർമ്മിച്ച ഫയലുകൾ ഡിലീറ്റ് ചെയ്ത് സിസ്റ്റം ക്ലീൻ ആക്കുന്നു
        if os.path.exists(output_card_path):
            os.remove(output_card_path)
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

