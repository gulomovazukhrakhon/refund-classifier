import os
import io
import json
import logging
import uvicorn
from PIL import Image
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from .model_utils import predict, load_model, preprocess_image


# Logging
logging.basicConfig(
    filename="app/logs/app.log",  # Log file
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "model", "model_scripted.pt")
CLASSES_PATH = os.path.join(CURRENT_DIR, "classes.json")


# App Version
_VERSION_ = "0.1.0"


# Classes 
with open(CLASSES_PATH) as f:
    classes_idx = json.load(f)
classes = list(classes_idx.keys())


# Load Model
model = load_model(model_path=MODEL_PATH)


# Initialize App
app = FastAPI(
    title="From Model to Production",
    description="Deployment of PyTorch Model into Production",
    version=_VERSION_, 
    debug=True
)


# Define response model
class PredictionResponse(BaseModel):
    predicted_class: str
    confidence: float


# Starting App
@app.get("/")
async def root():
    """
    Root endpoint for API health check.

    Returns:
        dict: Welcome message.
    """
    logging.info("Root API accessed")
    return {"message": "Welcome to the Refund Item Classification API"}


# Prediction on single image
@app.post('/predict/', response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    """
    Predict the class of an uploaded image.

    Args:
        file (UploadFile): Image file uploaded via API.

    Returns:
        dict: Predicted class and confidence score.

    Raises:
        HTTPException: If the file type is invalid.
        HTTPException: If the uploaded file is not a valid image.
    """
    logging.info(f"Received file: {file.filename}")

    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/pjpeg"]:
        logging.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG are supported.")
  
    image_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logging.error(f"Invalid image: {file.filename}")
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

    # Preprocess the image and predict
    image_tensor = preprocess_image(image)
    predicted_class, confidence = predict(model, image_tensor, classes)
    confidence = round(float(confidence), 3)

    logging.info(f"File: {file.filename} | Prediction: {predicted_class} | Confidence: {confidence}")
    return {"predicted_class": predicted_class, "confidence": confidence}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")