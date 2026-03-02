from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.meal_service import MealService

router = Router()
meal_service = MealService()

class SearchState(StatesGroup):
    waiting_for_name = State()
    waiting_for_ingredient = State()

# ── Search by name ──────────────────────────────────────────
@router.callback_query(F.data == "menu_search")
async def ask_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchState.waiting_for_name)
    await callback.message.answer("🔍 Ketik nama makanan yang mau dicari:")
    await callback.answer()

@router.message(SearchState.waiting_for_name)
async def do_search(message: Message, state: FSMContext):
    await state.clear()
    data = await meal_service.search_by_name(message.text)
    meals = data.get("meals")

    if not meals:
        await message.answer("❌ Tidak ditemukan. Coba kata kunci lain.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m["strMeal"], callback_data=f"meal_{m['idMeal']}")]
        for m in meals[:10]  # max 10 hasil
    ])
    await message.answer(f"✅ Ditemukan {len(meals)} hasil:", reply_markup=keyboard)

# ── Random meal ─────────────────────────────────────────────
@router.callback_query(F.data == "menu_random")
async def random_meal(callback: CallbackQuery):
    data = await meal_service.get_random_meal()
    meal = data.get("meals")[0] if data.get("meals") else None

    if not meal:
        await callback.message.answer("❌ Gagal mengambil random meal.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Lihat Detail", callback_data=f"meal_{meal['idMeal']}")],
        [InlineKeyboardButton(text="🎲 Random Lagi", callback_data="menu_random")]
    ])
    await callback.message.answer_photo(
        photo=meal["strMealThumb"],
        caption=f"🎲 *{meal['strMeal']}*\n📂 {meal['strCategory']} | 🌍 {meal['strArea']}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

# ── Search by ingredient ─────────────────────────────────────
@router.callback_query(F.data == "menu_ingredient")
async def ask_ingredient(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchState.waiting_for_ingredient)
    await callback.message.answer("🥕 Ketik nama bahan makanan (contoh: chicken, tomato):")
    await callback.answer()

@router.message(SearchState.waiting_for_ingredient)
async def do_ingredient_search(message: Message, state: FSMContext):
    await state.clear()
    data = await meal_service.search_by_ingredient(message.text)
    meals = data.get("meals")

    if not meals:
        await message.answer("❌ Tidak ditemukan. Coba bahan lain.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m["strMeal"], callback_data=f"meal_{m['idMeal']}")]
        for m in meals[:10]
    ])
    await message.answer(
        f"✅ {len(meals)} meal dengan bahan *{message.text}*:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )