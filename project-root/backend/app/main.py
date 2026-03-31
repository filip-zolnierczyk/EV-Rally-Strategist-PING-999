'''
Uruchamianie za pomocą dockera:

1. Za pierwszym razem:
    docker compose up --build
2. Przy kolejnych uruchomieniach:
    docker compose up
3. Zmieniłeś kod backendu / requirements.txt i chcesz zbudować obraz ponownie:
    docker compose up --build bakcend
'''


from fastapi import FastAPI
from app.api.routes import health, vehicle_route


app = FastAPI()

app.include_router(health.router)
app.include_router(vehicle_route.router)