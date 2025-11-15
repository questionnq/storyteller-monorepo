from fastapi import Header, HTTPException, Depends
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY 

#Инициализируем Supabase клиент для верификации токена
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) 

async def get_current_user(authorization: str = Header(None)) -> str:
    """
    Dependency Injection для FastAPI.
    Извлекает токен из заголовка 'Authorization', проверяет его через Supabase.
    Возвращает user_id (UUID), если токен валиден.
    """
    if not authorization or not authorization.startswith("Bearer "):
        #Этого не должно случиться, если фронтенд работает правильно
        raise HTTPException(status_code=401, detail="Bearer token required")

    token = authorization.split(" ")[1]

    try:
        #Проверяем токен через встроенный API Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user or not user_response.user.id:
            raise HTTPException(status_code=401, detail="Invalid token or user not found")
            
        return user_response.user.id
        
    except Exception as e:
        #В случае ошибки верификации (например, токен истек)
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")