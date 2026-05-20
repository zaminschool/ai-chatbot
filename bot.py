import os
import asyncio
import logging
from service import chatbot
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram import Bot, Dispatcher, F
from aiogram.filters.command import CommandStart, CommandObject
from database import create_table_users, add_user, increment_ai_count, check_user, get_connection, get_referral_link

load_dotenv()
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message, command: CommandObject):
    referred_by = None
    if command.args:
        referral_code = command.args
        with get_connection() as conn:
            cursor = conn.execute("""SELECT user_id FROM users WHERE referral_code = ?""", (referral_code,))
            ref_user = cursor.fetchone()
            if ref_user and ref_user[0] != message.from_user.id:
                referred_by = ref_user[0]
    if not check_user(message.from_user.id):
        add_user(fullname=message.from_user.full_name, username=message.from_user.username,
                 user_id=message.from_user.id, referred_by=referred_by)
    await message.answer("Botga xush kelibsiz")


@dp.message(F.text)
async def ai_chatbot(message: Message):
    blocked = increment_ai_count(message.from_user.id)
    if blocked:
        referral_link = get_referral_link(message.from_user.id, "zaminclass8_bot")
        await message.answer(
            f"""Limit tugadi (10/10) 1 ta odam taklif qiling va limit reset bo'ladi.\nReferral:{referral_link}""")
    else:
        sent_message = await message.answer("...")

        user_id = str(message.from_user.id)

        full_text = ""
        last_update = asyncio.get_event_loop().time()

        try:
            async for chunk in chatbot(
                    user_id=user_id,
                    prompt=message.text
            ):
                full_text += chunk

                now = asyncio.get_event_loop().time()
                if now - last_update > 0.5:

                    try:
                        if full_text.strip():
                            await sent_message.edit_text(full_text[:4096])
                        last_update = now
                    except Exception:
                        pass
                    await asyncio.sleep(0)
            if full_text.strip():
                await sent_message.edit_text(full_text[:4096])

        except Exception as e:
            await sent_message.edit_text(
                f"Xatolik yuz berdi:\n{str(e)}"
            )


async def main():
    create_table_users()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
