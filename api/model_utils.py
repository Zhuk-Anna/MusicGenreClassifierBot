import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import librosa

from .config import SAMPLE_RATE, N_MFCC, N_MELS, HOP_LENGTH, DURATION, STRIDE, MAX_TIME

# Определение устройства
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class SimplifiedCNNRNN(nn.Module):
    def __init__(self, n_classes):
        super().__init__()

        # Упрощенная CNN часть
        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=(3, 3), padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(32, 64, kernel_size=(3, 3), padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
            nn.Dropout2d(0.25),
        )
        
        # Автоматический расчет размера
        with torch.no_grad():
            dummy_input = torch.randn(1, 1, 193, 1300)
            dummy_output = self.conv(dummy_input)
            self.gru_input_size = dummy_output.size(1) * dummy_output.size(2)
            self.gru_input_length = dummy_output.size(3)
        
        # Упрощенная RNN часть
        self.gru = nn.GRU(
            input_size=self.gru_input_size,
            hidden_size=128,
            batch_first=True,
            bidirectional=True,
            num_layers=1#,
            #dropout=0.3
        )
        
        # Упрощенные полносвязные слои
        self.fc = nn.Sequential(
            nn.Linear(128 * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, n_classes)
        )
        
        # Инициализация весов
        self._initialize_weights()
    
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        x = self.conv(x)
        batch_size, channels, height, width = x.size()
        x = x.permute(0, 3, 1, 2)
        x = x.contiguous().view(batch_size, width, channels * height)
        out, _ = self.gru(x)
        out = out[:, -1, :]
        out = self.fc(out)
        return out
        # на выходе: [batch_size, n_classes]


# Функции обработки аудио

def load_audio(path, sr=SAMPLE_RATE, duration=DURATION):
    try:
        y, _ = librosa.load(path, sr=sr, mono=True, duration=duration)
        return y
    except Exception as e:
        print(f"Ошибка загрузки файла {path}: {str(e)}")
        return np.zeros(sr * duration)


def extract_enhanced_features(y, sr=SAMPLE_RATE, n_mfcc=N_MFCC, n_mels=N_MELS, hop_length=HOP_LENGTH):
    # MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)

    # Mel spectrogram
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, hop_length=hop_length)
    mel_db = librosa.power_to_db(mel)
    
    # Chroma features
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
    
    # Spectral contrast
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    
    # Tonnetz features
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    
    # Stack features: shape (channels, time)
    feat = np.vstack([mfcc, mel_db, chroma, spectral_contrast, tonnetz])
    return feat.astype(np.float32)


def predict_audio_chunk(y_chunk, model, device=DEVICE):
    """
       Предсказание модели на одном кусочке аудио.
       y_chunk: np.array, сэмплы аудио (1 кусок 30 секунд)
    """
    try:
        features = extract_enhanced_features(y_chunk)
        
        # Ensure fixed length
        if features.shape[1] < MAX_TIME:
            pad_width = MAX_TIME - features.shape[1]
            features = np.pad(features, ((0, 0), (0, pad_width)), mode='constant')
        else:
            features = features[:, :MAX_TIME]
        
        # Normalize
        features = (features - features.mean()) / (features.std() + 1e-6)
        
        # Add batch and channel dimensions
        features = torch.tensor(features).unsqueeze(0).unsqueeze(0).to(device)
        
        # Predict
        model.eval()
        with torch.no_grad():
            output = model(features)
            probs = F.softmax(output, dim=1).cpu().numpy().flatten() # вероятность жанра
            return probs

    except Exception as e:
        raise RuntimeError(f"Ошибка обработки фрагмента аудио: {str(e)}")


def predict_audio(file_path, model, label2idx, idx2label,
                       device=DEVICE, chunk_sec=DURATION, stride_sec=STRIDE, sr=SAMPLE_RATE):
    """
        Предсказание жанра для длинного аудио.
        Делит аудио на куски chunk_sec секунд с перекрытием stride_sec секунд,
        вызывает predict_audio_chunk и усредняет вероятности.
    """
    y, _ = librosa.load(file_path, sr=sr, mono=True)
    chunk_samples = chunk_sec * sr
    stride_samples = stride_sec * sr

    n_classes = len(label2idx)
    probs_total = np.zeros(n_classes)
    n_chunks = 0
    # 0 / 15 / 30 / 45 / 60 / 75 / 90 / 105 / 120 / 135 / 150 / 165
    for start in range(0, len(y) - chunk_samples + 1, stride_samples):
        chunk = y[start:start + chunk_samples]
        probs = predict_audio_chunk(chunk, model, device=device)
        print(f"Chunk {n_chunks + 1} probs =", np.round(probs, 2))
        probs_total += probs
        n_chunks += 1

    # Если аудио короче одного куска — берем весь файл как один кусок
    if n_chunks == 0:
        probs_total = predict_audio_chunk(y, model, device=device)
        print("Single chunk probs =", np.round(probs_total, 2))
        n_chunks = 1

    # Усреднение вероятностей
    probs_avg = probs_total / n_chunks
    print("Averaged probs =", np.round(probs_avg, 2))
    pred_idx = np.argmax(probs_avg)
    confidence = probs_avg[pred_idx]

    return idx2label[pred_idx], float(confidence)