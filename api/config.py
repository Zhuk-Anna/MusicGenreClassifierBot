from pathlib import Path

# API-константы
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.ogg'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
API_TITLE = "Music Genre Classification API"

# Аудио и ML-параметры
SAMPLE_RATE = 22050
N_MFCC = 40
N_MELS = 128
HOP_LENGTH = 512
DURATION = 30
STRIDE = 15
MAX_TIME = 800

# Пути
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pth"
LABELS_PATH = BASE_DIR / "models" / "labels.json"
TEMP_DIR = BASE_DIR / "tmp"
