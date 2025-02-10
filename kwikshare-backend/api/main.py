from fastapi import FastAPI
from api.routes import files  # Import the routes for handling file operations

app = FastAPI()  # Create FastAPI application instance

# Include the routes
app.include_router(files.router)

# Root route (For testing if the API is running)
@app.get("/")
def read_root():
    return {"message": "KwikShare API is running!"}
