from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import mysql.connector
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory (service root)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

app = FastAPI(title="Saista Bakers User Service")

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Asad@1234'),
    'database': os.getenv('DB_NAME', 'saista_bakers'),
    'port': int(os.getenv('DB_PORT', 3306))
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = ""

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    full_name: str
    email: str
    message: str

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str

# Auth Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return int(user_id)

# Routes
@app.get("/health")
def health():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    cursor.close()
    conn.close()
    return {"status": "healthy", "service": "user-service"}

@app.post("/signup", status_code=201)
def signup(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
            (user.username, user.email, password_hash, user.full_name)
        )
        conn.commit()
        user_id = cursor.lastrowid
        access_token = create_access_token(data={"sub": str(user_id)})
        return {
            "message": "User created successfully",
            "user_id": user_id,
            "access_token": access_token
        }
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="Username or email already exists")
    finally:
        cursor.close()
        conn.close()

@app.post("/login", response_model=Token)
def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, full_name, email FROM users WHERE username = %s", (user.username,))
    db_user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not db_user or not verify_password(user.password, db_user[1]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": str(db_user[0])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user[0],
        "username": user.username,
        "full_name": db_user[2],
        "email": db_user[3],
        "message": "Login successful"
    }

@app.get("/profile")
def get_profile(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, full_name, phone, address FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "full_name": user[3],
        "phone": user[4],
        "address": user[5]
    }

@app.get("/products")
def get_products(category: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute(
            "SELECT id, name, description, price, category FROM products WHERE category = %s AND available = TRUE ORDER BY name",
            (category,)
        )
    else:
        cursor.execute("SELECT id, name, description, price, category FROM products WHERE available = TRUE ORDER BY category, name")
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    product_list = [
        ProductResponse(id=p[0], name=p[1], description=p[2], price=float(p[3]), category=p[4])
        for p in products
    ]
    return {"products": product_list, "total": len(product_list)}

@app.get("/products/categories")
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE available = TRUE ORDER BY category")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"categories": [c[0] for c in categories]}

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, category FROM products WHERE id = %s AND available = TRUE", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(id=product[0], name=product[1], description=product[2], price=float(product[3]), category=product[4])

@app.get("/users/{user_id}")
def get_user_info(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, full_name FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "full_name": user[3]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5001, reload=True)
