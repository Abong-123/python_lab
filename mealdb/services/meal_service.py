import httpx

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

class MealService:
    async def search_by_name(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/search.php",
                params={"s": query}
            )
            return response.json()
    
    async def search_by_ingredient(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/filter.php",
                params={"i": query}
            )
            return response.json()
    
    async def get_random_meal(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/random.php")
            return response.json()
    
    async def get_meal_detail(self, meal_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/lookup.php",
                params={"i": meal_id}
            )
            return response.json()
    
    async def get_categories(self, category: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/filter.php",
                params={"c": category}
            )
            return response.json()
    
    async def get_by_contry(self, country: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/filter.php",
                params={"a": country}
            )
            return response.json()
    
    async def get_categories_list(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/categories.php")
            return response.json()

    async def get_areas_list(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/list.php", params={"a": "list"})
            return response.json()