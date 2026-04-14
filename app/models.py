from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class UploadResponse(BaseModel):
    status: str
    original_image: str
    enhanced_image: str
    original_width: int
    original_height: int
    enhanced_width: int
    enhanced_height: int
    detail: str


class VideoResponse(BaseModel):
    status: str
    image: str
    video: str
    detail: str