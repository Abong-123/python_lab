from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.meal_service import MealService

router = Router()
meal_service = MealService()

def chunk(lst, n):
    """Bagi list jadi beberapa baris, n item per baris"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# ── Filter by Country ────────────────────────────────────────
@router.callback_query(F.data == "menu_country")
async def show_countries(callback: CallbackQuery):
    data = await meal_service.get_areas_list()
    areas = data.get("meals", [])

    buttons = [
        InlineKeyboardButton(text=a["strArea"], callback_data=f"country_{a['strArea']}")
        for a in areas
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=list(chunk(buttons, 3)))
    await callback.message.answer("🌍 Pilih negara:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("country_"))
async def filter_by_country(callback: CallbackQuery):
    country = callback.data.replace("country_", "")
    data = await meal_service.get_by_contry(country)
    meals = data.get("meals")

    if not meals:
        await callback.message.answer(f"❌ Tidak ada meal dari {country}.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m["strMeal"], callback_data=f"meal_{m['idMeal']}")]
        for m in meals[:10]
    ])
    await callback.message.answer(
        f"🌍 Meal dari *{country}* ({len(meals)} total):",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

# ── Filter by Category ───────────────────────────────────────
@router.callback_query(F.data == "menu_category")
async def show_categories(callback: CallbackQuery):
    data = await meal_service.get_categories_list()
    categories = data.get("categories", [])

    buttons = [
        InlineKeyboardButton(text=c["strCategory"], callback_data=f"cat_{c['strCategory']}")
        for c in categories
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=list(chunk(buttons, 3)))
    await callback.message.answer("📂 Pilih kategori:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def filter_by_category(callback: CallbackQuery):
    category = callback.data.replace("cat_", "")
    data = await meal_service.get_categories(category)
    meals = data.get("meals")

    if not meals:
        await callback.message.answer(f"❌ Tidak ada meal di kategori {category}.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m["strMeal"], callback_data=f"meal_{m['idMeal']}")]
        for m in meals[:10]
    ])
    await callback.message.answer(
        f"📂 Meal kategori *{category}* ({len(meals)} total):",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()