from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.api.v1.routes import router as api_router

app = FastAPI(title="Script Generator")


class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"[CORS] ===== MIDDLEWARE CALLED =====")
        print(f"[CORS] Request: {request.method} {request.url.path}")

        origin = request.headers.get("origin")
        print(f"[CORS] Origin: {origin}")
        print(f"[CORS] Headers: {dict(request.headers)}")

        # Список разрешенных origins
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://storyteller-monorepo.vercel.app",
            "https://storyteller-monorepo.onrender.com",
        ]

        # Проверяем origin
        is_allowed = False
        if origin:
            if origin in allowed_origins:
                is_allowed = True
                print(f"[CORS] Origin in allowed list")
            elif origin.endswith(".vercel.app"):
                is_allowed = True
                print(f"[CORS] Origin is Vercel subdomain")

        if is_allowed:
            # Для preflight запросов (OPTIONS)
            if request.method == "OPTIONS":
                print(f"[CORS] Handling OPTIONS preflight")
                response = Response(status_code=200)
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin, User-Agent"
                response.headers["Access-Control-Expose-Headers"] = "*"
                response.headers["Access-Control-Max-Age"] = "3600"
                response.headers["Content-Length"] = "0"
                response.headers["Vary"] = "Origin"
                print(f"[CORS] OPTIONS response headers: {dict(response.headers)}")
                return response

            # Для обычных запросов
            print(f"[CORS] Handling regular request")
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "*"
            response.headers["Vary"] = "Origin"
            print(f"[CORS] Regular response status: {response.status_code}")
            return response

        # Если origin не разрешен, продолжаем без CORS headers
        print(f"[CORS] Origin not allowed: {origin}, proceeding without CORS headers")
        response = await call_next(request)
        print(f"[CORS] Response sent without CORS headers, status: {response.status_code}")
        return response


app.add_middleware(CustomCORSMiddleware)

app.include_router(api_router, prefix="/api/v1")
