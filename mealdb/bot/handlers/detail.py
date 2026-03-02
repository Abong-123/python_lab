from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import BufferedInputFile
from services.meal_service import MealService
from bot.utils.pdf import generate_meal_pdf

router = Router()
meal_service = MealService()

@router.callback_query(F.data.startswith("meal_"))
async def meal_detail(callback: CallbackQuery):
    meal_id = callback.data.replace("meal_", "")
    data = await meal_service.get_meal_detail(meal_id)
    meal = data.get("meals")[0] if data.get("meals") else None

    if not meal:
        await callback.message.answer("❌ Detail tidak ditemukan.")
        await callback.answer()
        return

    # Susun ingredients
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "").strip()
        msr = meal.get(f"strMeasure{i}", "").strip()
        if ing:
            ingredients.append(f"• {msr} {ing}")

    text = (
        f"🍽️ *{meal['strMeal']}*\n"
        f"📂 {meal['strCategory']} | 🌍 {meal['strArea']}\n\n"
        f"*Ingredients:*\n" + "\n".join(ingredients) +
        f"\n\n*Instructions:*\n{meal['strInstructions'][:800]}..."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Download PDF", callback_data=f"pdf_{meal_id}")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="menu_main")]
    ])

    await callback.message.answer_photo(
        photo=meal["strMealThumb"],
        caption=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pdf_"))
async def send_pdf(callback: CallbackQuery):
    meal_id = callback.data.replace("pdf_", "")
    data = await meal_service.get_meal_detail(meal_id)
    meal = data.get("meals")[0] if data.get("meals") else None

    await callback.message.answer("⏳ Generating PDF...")

    pdf_bytes = await generate_meal_pdf(meal)
    filename = f"{meal['strMeal'].replace(' ', '_')}.pdf"

    await callback.message.answer_document(
        document=BufferedInputFile(pdf_bytes, filename=filename),
        caption=f"📄 *{meal['strMeal']}* - Recipe PDF",
        parse_mode="Markdown"
    )
    await callback.answer()

# Kembali ke main menu
@router.callback_query(F.data == "menu_main")
async def back_to_menu(callback: CallbackQuery):
    from bot.handlers.start import start
    await start(callback.message)
    await callback.answer()