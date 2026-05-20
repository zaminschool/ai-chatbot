from aiogram.utils.keyboard import InlineKeyboardBuilder


def referral_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Referral olish",
        callback_data="get_referral"
    )

    return builder.as_markup()