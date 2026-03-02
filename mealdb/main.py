from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from services import meal_service
from fastapi.staticfiles import StaticFiles
from starlette.staticfiles import StaticFiles
from weasyprint import HTML
import io


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
meal_service = meal_service.MealService()

# ✅ Helper — dipanggil di semua route
async def get_filter_data():
    categories = await meal_service.get_categories_list()
    areas = await meal_service.get_areas_list()
    return {
        "categories": categories.get("categories", []),
        "areas": areas.get("meals", [])
    }

# ✅ Helper — dipanggil di semua route
async def get_filter_data():
    categories = await meal_service.get_categories_list()
    areas = await meal_service.get_areas_list()
    return {
        "categories": categories.get("categories", []),
        "areas": areas.get("meals", [])
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    filter_data = await get_filter_data()
    return templates.TemplateResponse("index.html", {
        "request": request, **filter_data
    })

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str):
    data = await meal_service.search_by_name(query)
    meals = data.get("meals")
    filter_data = await get_filter_data()
    return templates.TemplateResponse("index.html", {
        "request": request, "meals": meals, "query": query, **filter_data
    })

@app.get("/random", response_class=HTMLResponse)
async def random_meal(request: Request):
    data = await meal_service.get_random_meal()
    meal = data.get("meals")[0] if data.get("meals") else None
    filter_data = await get_filter_data()  # ✅ tambah ini
    return templates.TemplateResponse("index.html", {
        "request": request, "meal": meal, **filter_data
    })

@app.get("/meal/{meal_id}", response_class=HTMLResponse)
async def meal_detail(request: Request, meal_id: str):
    data = await meal_service.get_meal_detail(meal_id)
    meal = data.get("meals")[0] if data.get("meals") else None
    return templates.TemplateResponse("details.html", {
        "request": request, "meal": meal
    })

@app.get("/filter/category", response_class=HTMLResponse)
async def filter_category(request: Request, category: str):
    data = await meal_service.get_categories(category)
    meals = data.get("meals")
    filter_data = await get_filter_data()
    return templates.TemplateResponse("index.html", {
        "request": request, "meals": meals, "query": f"Category: {category}", **filter_data
    })

@app.get("/filter/country", response_class=HTMLResponse)
async def filter_country(request: Request, country: str):
    data = await meal_service.get_by_contry(country)
    meals = data.get("meals")
    filter_data = await get_filter_data()
    return templates.TemplateResponse("index.html", {
        "request": request, "meals": meals, "query": f"Area: {country}", **filter_data
    })

@app.get("/filter/ingredient", response_class=HTMLResponse)
async def filter_ingredient(request: Request, ingredient: str):
    data = await meal_service.search_by_ingredient(ingredient)
    meals = data.get("meals")
    filter_data = await get_filter_data()
    return templates.TemplateResponse("index.html", {
        "request": request, "meals": meals, "query": f"Ingredient: {ingredient}", **filter_data
    })

@app.get("/meal/{meal_id}/pdf")
async def meal_pdf(request: Request, meal_id: str):
    data = await meal_service.get_meal_detail(meal_id)
    meal = data.get("meals")[0] if data.get("meals") else None

    # Render template ke string HTML
    html_str = templates.TemplateResponse(
        "pdf_template.html", {"request": request, "meal": meal}
    ).body.decode("utf-8")

    # Generate PDF pakai WeasyPrint
    pdf_bytes = HTML(string=html_str, base_url=str(request.base_url)).write_pdf()

    meal_name = meal["strMeal"].replace(" ", "_") if meal else "meal"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={meal_name}.pdf"}
    )