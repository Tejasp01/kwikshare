from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from hashlib import sha256
import os, shutil

app = FastAPI()

# MongoDB Connection
MONGO_URL = "mongodb+srv://your_mongodb_url"
client = AsyncIOMotorClient(MONGO_URL)
db = client["kwikshare"]
users_collection = db["users"]
files_collection = db["files"]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Models
class User(BaseModel):
    username: str
    password: str

class FileAccess(BaseModel):
    file_id: str
    password: str

# Utility: Hash password
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# Register User
@app.post("/register")
async def register(user: User):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = hash_password(user.password)
    await users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "User registered successfully"}

# Upload File
@app.post("/upload")
async def upload_file(file: UploadFile, password: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_data = {
        "filename": file.filename,
        "password": hash_password(password)
    }
    result = await files_collection.insert_one(file_data)
    
    return {"file_id": str(result.inserted_id), "message": "File uploaded successfully"}

# Download File
@app.post("/download")
async def download_file(file_access: FileAccess):
    file_record = await files_collection.find_one({"_id": file_access.file_id})
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    if file_record["password"] != hash_password(file_access.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    file_path = os.path.join(UPLOAD_DIR, file_record["filename"])
    return FileResponse(file_path, filename=file_record["filename"])
