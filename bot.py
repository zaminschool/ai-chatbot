import os
import asyncio
import logging
from service import chatbot
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram import Bot, Dispatcher, F
from database import create_table_users, add_user, increment_ai_count, check_user
from aiogram.filters.command import CommandStart

load_dotenv()
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    if check_user(message.from_user.id) == False:
        add_user(message.from_user.full_name, message.from_user.username, message.from_user.id)
        await message.answer("Assalomu alaykum!")
    else:
        await message.answer("Assalomu alaykum sizni yana bir bor ko'ranimizdan mamnummiz:)")


@dp.message(F.text)
async def ai_chatbot(message: Message):
    blocked = increment_ai_count(message.from_user.id)
    if blocked:
        await message.answer("Limit tugagan (10/10). Premium kerak.")
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
