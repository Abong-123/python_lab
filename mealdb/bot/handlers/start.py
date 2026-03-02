from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Search by Name", callback_data="menu_search")],
        [InlineKeyboardButton(text="🎲 Random Meal", callback_data="menu_random")],
        [InlineKeyboardButton(text="🌍 Filter by Country", callback_data="menu_country")],
        [InlineKeyboardButton(text="🥕 Filter by Ingredient", callback_data="menu_ingredient")],
        [InlineKeyboardButton(text="📂 Filter by Category", callback_data="menu_category")],
    ])
    await message.answer(
        "👨‍🍳 *Welcome to Meal Finder Bot!*\n\nPilih menu di bawah:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )