from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
import json
import tempfile
import os

from .model_utils import SimplifiedCNNRNN, predict_audio, DEVICE
from .config import SUPPORTED_AUDIO_FORMATS, MAX_FILE_SIZE, API_TITLE, MODEL_PATH, LABELS_PATH, TEMP_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    # Загрузка модели
    try:
        model = SimplifiedCNNRNN(n_classes=10).to(DEVICE)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        app.state.model = model
        print("Модель успешно загружена")
    except Exception as e:
        raise RuntimeError(f"Не удалось загрузить модель: {e}")

    # Загрузка меток
    try:
        with open(LABELS_PATH, 'r') as f:
            labels = json.load(f)
            app.state.label2idx = labels['label2idx']
            app.state.idx2label = {int(k): v for k, v in labels['idx2label'].items()}
        print("Метки успешно загружены")
    except Exception as e:
        raise RuntimeError(f"Не удалось загрузить метки: {e}")

    yield
    print("API остановлено")


app = FastAPI(title=API_TITLE, lifespan=lifespan)

# CORS middleware. Разрешает обращаться к API из браузера, с любого домена
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"message": "Music Genre Classification API is running"}


@app.get("/info")
async def info():
    return {
        "description": "Классификация музыкальных жанров с помощью ML",
        "supported_genres": list(app.state.label2idx.keys()),
        "supported_formats": list(SUPPORTED_AUDIO_FORMATS)
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not any(file.filename.lower().endswith(ext) for ext in SUPPORTED_AUDIO_FORMATS):
        raise HTTPException(400, "Неподдерживаемый формат файла")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE: # TODO: убрать?
        raise HTTPException(400, "Файл слишком большой")

    temp_path = None
    with tempfile.NamedTemporaryFile(
            delete=False,
            dir=TEMP_DIR,
            suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(contents)
        temp_path = tmp.name

    try:
        genre, confidence = predict_audio(
            temp_path,
            app.state.model,
            app.state.label2idx,
            app.state.idx2label)
        return {"genre": genre, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

