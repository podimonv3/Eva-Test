import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import MessageEntityType

# സാധാരണയായി വരുന്ന ലിങ്കുകൾ കണ്ടെത്താനുള്ള Regex
LINK_PATTERN = r"(https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b|t\.me/\S+|me/\+\S+)"

# 18+ അല്ലെങ്കിൽ അനാവശ്യ ഇമോജികൾ
ADULT_EMOJIS = ["🔞", "🍑", "🍆", "💦", "🍒", "🍌"]

# ലിങ്ക് സ്പാം ട്രാക്ക് ചെയ്യാനുള്ള താൽക്കാലിക മെമ്മറി (User Link Counter)
SPAM_COUNTER = {}

# അഡ്മിൻമാരെ ഒഴിവാക്കാൻ ഉള്ള ഫങ്クション
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

# ഗ്രൂപ്പിലെ മെസ്സേജുകൾ നിരീക്ഷിക്കാനുള്ള ഫിൽട്ടർ
@Client.on_message(filters.group & (filters.text | filters.caption))
async def advanced_antispam_filter(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    text = message.text or message.caption

    # മെസ്സേജ് അയച്ചത് അഡ്മിൻ ആണെങ്കിൽ ബോട്ട് ഒന്നും ചെയ്യില്ല
    if await is_admin(client, chat_id, user_id):
        return

    # 1. 18+ ഇമോജികൾ ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു
    has_adult_emoji = any(emoji in text for emoji in ADULT_EMOJIS)

    if has_adult_emoji:
        try:
            await message.delete()
            
            # പെർമനന്റ് ആയി മ്യൂട്ട് ചെയ്യുന്നു
            await client.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )

            warning_msg = await message.reply_text(
                f"⚠️ **അച്ചടക്ക നടപടി!**\n{user_name}, ഗ്രൂപ്പിൽ അനുവദനീയമല്ലാത്ത ഇമോജികൾ ഉപയോഗിച്ചതിനാൽ നിങ്ങളെ **Permanent ആയി Mute** ചെയ്തിരിക്കുന്നു. കൂടുതൽ വിവരങ്ങൾ PM-ൽ അയച്ചിട്ടുണ്ട്."
            )

            # PM മെസ്സേജ്
            try:
                pm_text = (
                    f"👋 ഹലോ {user_name},\n\n"
                    f"**{message.chat.title}** എന്ന ഗ്രൂപ്പിൽ നിങ്ങൾ 18+ ഇമോജികൾ ഉപയോഗിച്ചതിനാൽ നിങ്ങളെ **Permanent (ശാശ്വതമായി)** മ്യൂട്ട് ചെയ്തിരിക്കുകയാണ്.\n\n"
                    f"📝 **നിങ്ങൾ അയച്ച മെസ്സേജ്:** {text}\n\n"
                    f"ദയവായി ഗ്രൂപ്പുകളിൽ അച്ചടക്കം പാലിക്കുക."
                )
                await client.send_message(chat_id=user_id, text=pm_text)
            except Exception as pm_error:
                print(f"Could not send PM to user {user_id}: {pm_error}")

            await asyncio.sleep(5)
            await warning_msg.delete()
            return
        except Exception as e:
            print(f"Error in emoji mute: {e}")

    # 2. ലിങ്കുകൾ ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു (സാധാരണ ലിങ്കുകളും ടെക്സ്റ്റിനുള്ളിൽ ഒളിപ്പിച്ച ലിങ്കുകളും)
    has_normal_link = re.search(LINK_PATTERN, text, re.IGNORECASE)
    has_text_link = False

    # മെസ്സേജിലെ Entities പരിശോധിച്ചു Text Hyperlinks ഉണ്ടോ എന്ന് ഉറപ്പുവരുത്തുന്നു
    if message.entities or message.caption_entities:
        entities = message.entities or message.caption_entities
        for entity in entities:
            if entity.type in [MessageEntityType.TEXT_LINK, MessageEntityType.URL]:
                has_text_link = True
                break

    # സാധാരണ ലിങ്കോ ടെക്സ്റ്റിനുള്ളിൽ ഒളിപ്പിച്ച ലിങ്കോ കണ്ടെത്തിയാൽ പ്രവർത്തിക്കുന്നു
    if has_normal_link or has_text_link:
        try:
            await message.delete()

            # ഗ്രൂപ്പിന്റെ കൗണ്ടർ സെറ്റ് ചെയ്യുന്നു
            if chat_id not in SPAM_COUNTER:
                SPAM_COUNTER[chat_id] = {}
            
            # യൂസറുടെ ലിങ്ക് കൗണ്ട് വർദ്ധിപ്പിക്കുന്നു
            current_count = SPAM_COUNTER[chat_id].get(user_id, 0) + 1
            SPAM_COUNTER[chat_id][user_id] = current_count

            # തുടർച്ചയായി 3 തവണ ലിങ്ക് അയച്ചാൽ BAN ചെയ്യും
            if current_count >= 3:
                await client.ban_chat_member(chat_id=chat_id, user_id=user_id)
                SPAM_COUNTER[chat_id][user_id] = 0  # കൗണ്ടർ റീസെറ്റ് ചെയ്യുന്നു

                warning_msg = await message.reply_text(
                    f"🚨 **ലിങ്ക് സ്പാം അലേർട്ട്!**\n{user_name} തുടർച്ചയായി ലിങ്കുകൾ അയച്ച് ഗ്രൂപ്പ് സ്പാം ചെയ്തതിനാൽ ഗ്രൂപ്പിൽ നിന്നും **BAN** ചെയ്തിരിക്കുന്നു."
                )
                
                try:
                    pm_text = (
                        f"🚨 ഹലോ {user_name},\n\n"
                        f"**{message.chat.title}** എന്ന ഗ്രൂപ്പിൽ നിങ്ങൾ തുടർച്ചയായി ലിങ്കുകൾ (വാക്കുകൾക്കുള്ളിലെ ലിങ്കുകൾ ഉൾപ്പെടെ) അയച്ച് സ്പാം ചെയ്തതിനാൽ നിങ്ങളെ ഗ്രൂപ്പിൽ നിന്നും **BAN** ചെയ്തിരിക്കുകയാണ്."
                    )
                    await client.send_message(chat_id=user_id, text=pm_text)
                except Exception as pm_error:
                    print(f"Could not send PM to user {user_id}: {pm_error}")

            else:
                remains = 3 - current_count
                warning_msg = await message.reply_text(
                    f"⚠️ {user_name}, ഈ ഗ്രൂപ്പിൽ യാതൊരുവിധ ലിങ്കുകളും (വാക്കുകൾക്കുള്ളിൽ ഒളിപ്പിച്ച ലിങ്കുകൾ ഉൾപ്പെടെ) അനുവദനീയമല്ല. നിങ്ങളുടെ മെസ്സേജ് ഡിലീറ്റ് ചെയ്തിട്ടുണ്ട്.\n"
                    f" (ഇനിയും {remains} തവണ ലിങ്ക് അയച്ചാൽ നിങ്ങളെ ഗ്രൂപ്പിൽ നിന്നും **BAN** ചെയ്യുന്നതായിരിക്കും!)"
                )

            # 5 സെക്കന്റിന് ശേഷം ബോട്ടിന്റെ മുന്നറിയിപ്പ് മെസ്സേജ് ഡിലീറ്റ് ചെയ്യുക
            await asyncio.sleep(5)
            await warning_msg.delete()

        except Exception as e:
            print(f"Error handling link spam: {e}")

