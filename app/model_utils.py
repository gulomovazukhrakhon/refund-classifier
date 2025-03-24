# Notebook Imports
import torch
import os
from torchvision import transforms


# Device "GPU" or "CPU"
device = 'cuda' if torch.cuda.is_available() else 'cpu'


# Loading Pytorch Model
def load_model(model_path, device=device):
    """
    Load a PyTorch model from a given file path.

    Args:
        model_path (str): Path to the saved PyTorch model (.pt file).
        device (str): The device to load the model onto ("cuda" or "cpu").

    Returns:
        torch.nn.Module: Loaded PyTorch model set to evaluation mode.

    Raises:
        RuntimeError: If the model cannot be loaded.
    """

    model = torch.jit.load(model_path, map_location=device)
    model.eval()
    return model


# Preprocessing Image
def preprocess_image(image):
    """
    Preprocess an image for model inference.

    Args:
        image (PIL.Image): The input image to be transformed.

    Returns:
        torch.Tensor: Preprocessed image tensor with batch dimension.
    """

    test_transform = transforms.Compose([
        transforms.Resize(size=(224, 224)), 
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return test_transform(image).unsqueeze(0)


# Model Prediction
def predict(model, image_tensor, classes):
    """
    Perform inference on a given image tensor and return the predicted class.

    Args:
        model (torch.nn.Module): Trained PyTorch model for classification.
        image_tensor (torch.Tensor): Preprocessed image tensor.
        classes (list): List of class labels.

    Returns:
        tuple: (Predicted class label (str), Confidence score (float))

    Raises:
        RuntimeError: If model inference fails.
    """

    try:
        image_tensor = image_tensor.to(device)  # Move image tensor to the correct device
        with torch.no_grad():
            results = model(image_tensor)  # Run inference

        y_probs = torch.softmax(results, dim=1)  # Get probabilities
        y_pred = torch.argmax(y_probs, dim=1).item()  # Convert tensor to int

        y_class = classes[y_pred]  # Get predicted class
        confidence = y_probs.max().item()  # Convert tensor to float

        return y_class, confidence
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")