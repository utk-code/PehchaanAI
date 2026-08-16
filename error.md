# Error Log - Backend Flow Testing

## Summary
Attempting to test the full backend flow with a sample image (POST /cases/photo/embedding endpoint) to verify the lighter `buffalo_s` model works correctly.

## Issues Encountered

### 1. Tailwind CSS Missing (Frontend)
- **Problem**: Frontend showed plain white text with no styling
- **Root Cause**: Tailwind CSS v4+ requires `@tailwindcss/postcss` package and `@import "tailwindcss";` syntax instead of `@tailwind base/components/utilities;`
- **Fixed**: Added `@tailwindcss/postcss`, `postcss`, `autoprefixer` packages and updated `postcss.config.js` and `styles.css`

### 2. Model Configuration (Backend)
- **Problem**: Hardcoded `buffalo_l` model (heavy, ~330MB, slow on CPU)
- **Fixed**: Added `FACE_MODEL_NAME` config setting (default `buffalo_s`) in `backend/config.py`, updated `backend/face/detector.py` to read from config, updated `.env.example`

### 3. Test Image Creation Issues
- **Problem**: `test_images/lenna.png` not being created/found in working directory
- **Details**: Multiple attempts to create test image using Python/PIL resulted in file not found errors
- **Working directory**: `d:\Projects\Project Ace`
- **Commands tried**:
  ```python
  # Multiple attempts to create test image
  python -c "
  import numpy as np
  from PIL import Image
  import os
  img = np.zeros((200, 200, 3), dtype=np.uint8)
  img[60:140, 60:140] = [180, 160, 140]
  img[80:100, 80:120] = [50, 50, 50]
  img[120:135, 80:120] = [100, 80, 60]
  os.makedirs('test_images', exist_ok=True)
  Image.fromarray(img).save('test_images/lenna.png')
  print('Created:', os.path.abspath('test_images/lenna.png'))
  "
  ```
- **Result**: File creation appears to succeed but subsequent checks show `Exists: False`

### 4. Test Script Path Issues
- **Script**: `test_embedding.py` uses `os.path.join(os.path.dirname(__file__), 'test_images', 'lenna.png')`
- **Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'd:\\Projects\\Project Ace\\test_images\\lenna.png'`
- **Note**: The file system walk search shows no `test_images` directory exists in the workspace

### 5. Backend Server Running
- **Status**: Backend runs successfully on port 8000
- **Health check**: `GET /health` returns `{"status":"ok"}`
- **Model loading**: First request to `/cases/photo/embedding` triggers model download (~160MB for buffalo_s)

## Current State
- Backend config updated to use `buffalo_s` (lighter model)
- All tests pass (24/24)
- Frontend builds successfully with Tailwind
- Test image creation appears to fail silently
- Cannot test embedding endpoint without valid test image

## Next Steps
1. Verify file system permissions for `test_images` directory creation
2. Try creating test image with absolute path
3. Or use an existing image from the filesystem
4. Test the embedding endpoint once image is available