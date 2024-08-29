from cloudinary.uploader import upload
from fastapi import HTTPException, status, UploadFile
from typing import List

async def upload_image(image: UploadFile):
    try:
        upload_result = upload(image.file)
        file_url = upload_result['secure_url']
        return file_url
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading images: {e}")