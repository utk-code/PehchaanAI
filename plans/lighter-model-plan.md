# Plan: Switch to Lighter InsightFace Model (buffalo_s)

## Goal
Replace the heavyweight `buffalo_l` model with the lighter `buffalo_s` model to reduce CPU load and memory usage, while keeping it configurable.

## Model Comparison

| Property | buffalo_l (current) | buffalo_s (lighter) |
|----------|---------------------|----------------------|
| Model pack size | ~330MB | ~160MB |
| Detection model | RetinaFace (large) | RetinaFace (small) |
| Recognition model | ResNet100 (ArcFace) | MobileFaceNet |
| Embedding dim | 512 | 512 |
| CPU inference | ~500-800ms | ~100-250ms |
| Accuracy | Higher | Slightly lower |
| RAM usage | ~2-4GB | ~0.5-1GB |

## Files to Change

### 1. `backend/config.py`
Add `face_model_name` setting:
```python
face_model_name: str = Field(
    default="buffalo_s",  # lighter model
    alias="FACE_MODEL_NAME",
)
```

### 2. `backend/face/detector.py`
- Remove hardcoded `"buffalo_l"` from `FaceAnalysis(name="buffalo_l", ...)`
- Read model name from settings via `get_settings()`
- Update `get_face_detector()` factory signature to accept model name

### 3. `backend/face/embedder.py`
- `FaceEmbedder` reuses detector's `_app`, so it automatically inherits the model
- No direct change needed (it uses `self._app.models["recognition"]`)

### 4. `backend/.env.example`
Add:
```
# Face model: buffalo_s (lighter, faster) or buffalo_l (larger, more accurate)
FACE_MODEL_NAME=buffalo_s
```

### 5. `README.md`
Update model mention if needed (optional, low priority)

## Execution Order
1. Update `backend/config.py` - add `face_model_name`
2. Update `backend/face/detector.py` - use configurable model name
3. Update `backend/.env.example` - add option
4. Test backend startup with `/health`
5. Test face detection with a sample image

## Validation
- `python -m pytest tests -q` still passes
- Backend starts and `/health` responds
- (If possible) test an image upload to confirm embedding is still 512-d
