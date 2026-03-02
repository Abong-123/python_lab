from weasyprint import HTML

async def generate_meal_pdf(meal: dict) -> bytes:
    ingredients_rows = ""
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "").strip()
        msr = meal.get(f"strMeasure{i}", "").strip()
        if ing:
            ingredients_rows += f"<tr><td>{msr}</td><td>{ing}</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #e67e22; border-bottom: 2px solid #e67e22; padding-bottom: 8px; }}
        .meta {{ color: #888; margin-bottom: 20px; }}
        img {{ width: 300px; border-radius: 8px; }}
        h2 {{ border-left: 4px solid #e67e22; padding-left: 10px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        td {{ padding: 6px 10px; border-bottom: 1px solid #eee; }}
        tr:nth-child(even) td {{ background: #fafafa; }}
        .instructions {{ font-size: 14px; line-height: 1.8; white-space: pre-line; }}
    </style>
    </head>
    <body>
        <h1>{meal['strMeal']}</h1>
        <p class="meta">📂 {meal['strCategory']} &nbsp;|&nbsp; 🌍 {meal['strArea']}</p>
        <img src="{meal['strMealThumb']}" alt="{meal['strMeal']}">

        <h2>Ingredients</h2>
        <table>{ingredients_rows}</table>

        <h2>Instructions</h2>
        <div class="instructions">{meal['strInstructions']}</div>
    </body>
    </html>
    """
    return HTML(string=html).write_pdf()