from pydantic import BaseModel, BaseSettings
# Predictions
class Prediction(BaseModel):
    image_frame: str
    prob: float
    tags: list[str]

# Data
class Data(BaseModel):
    license_id: str
    preds: list[Prediction]

# Payload
class Payload(BaseModel):
    device_id: str
    client_id: str
    created_at: str
    data: Data
