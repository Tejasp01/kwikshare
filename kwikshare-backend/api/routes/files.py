from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

router = APIRouter()

# Define a folder for temporary file storage (change as needed)
UPLOAD_DIRECTORY = "uploads/"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and save it to the server.
    """
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/files")
async def list_files():
    """
    List all uploaded files.
    """
    try:
        files = os.listdir(UPLOAD_DIRECTORY)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
