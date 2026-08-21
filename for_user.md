# PehchaanAI: Missing Child Identification AI System
## A Guide for You: Understanding What We're Building

Welcome! This document explains what we've built so far and what's coming next, using simple language to help you "absorb" the technical side of the project.

---

### 1. The Big Picture
We are building a system where a user (like a parent or police officer) can upload a photo of a missing child. The AI will then:
1. **Find the face** in the photo.
2. **Convert that face** into a mathematical "fingerprint" (called an embedding).
3. **Search a database** to see if that "fingerprint" matches any other known records.

The technical question we're answering: *Can the system still find the right person when the photo you upload and the photo in the database are from very different ages?* (Think: age 7 photo vs. age 18 photo.)

---

### 2. What we have done so far (It's all built!)

The main **core loop works end-to-end** — register, log in, upload a photo, get ranked matches, and download an investigation report.

#### **Project Structure (The Folders)**
- **`backend/`**: This is the "Brain." It handles face detection, the AI math, the search, and the database.
- **`frontend/`**: This is the "Face." It's what you see in your browser (buttons, forms, images).

#### **Authentication (The Key)**
- **Register / Login:** Users create accounts and log in.
- **JWT (JSON Web Tokens):** Like a "VIP Wristband." Once you log in the server gives you a token; you show it with every request so it knows who you are.

#### **Face Detection & Embeddings (The Magic)**
- We use **InsightFace** to find the face in a photo and **ArcFace** to turn it into a **512-number fingerprint** (the embedding).
- Computers are terrible at comparing images but lightning-fast at comparing numbers — so we compare fingerprints, not pictures.

#### **The Database & Search (The Memory + The Matching)**
- We currently use a **SQLite** file (`pehchaanai.db`) holding our test dataset of faces.
- Search is **pure cosine similarity**: we measure how closely two fingerprints point in the same "direction." Higher score = more similar.
- The search is **vectorized** (uses fast math libraries), so a full scan of ~600 records takes a fraction of a second.

#### **Cases & Reports (The Workflow)**
- **Cases:** A case stores a child's photo, name, age at the time, date and location, plus the embedding.
- **Investigation reports:** One click generates a readable report (summary, ranked candidates, confidence levels, next steps) — no external AI service needed.

#### **What we proved (The Results)**
- Loaded the public **FG-NET** research dataset (609 usable photos, 82 people, ages 0-69).
- Ran a **cross-age evaluation**: can we find the same person across age gaps?
  - **Rank-10 accuracy: 89.5%** (the right person shows up in the top 10) — this beats our 70% success target.
  - Rank-5: 80.4% · Rank-1: 23.2%
- **Performance targets met:** full search (find face + make fingerprint + scan ~600 photos) averages **~0.5 seconds** on CPU.

---

### 3. Simple Analogy: The Restaurant
- **You (The User):** Sits at a table (the **Frontend**).
- **The Menu:** Shows you what you can order (the **API**).
- **The Waiter:** Takes your order to the kitchen (**FastAPI**).
- **The Kitchen:** Cooks the food (the **Backend logic & AI**).
- **The Pantry:** Where ingredients are stored (the **Database**).

---

### 4. How to use this project (right now, on your machine)
1. Start the backend (`uvicorn backend.main:app --reload --port 8000`).
2. Start the frontend (`cd frontend; npm install; npm run dev`).
3. Open **`http://127.0.0.1:5173`** in your browser (use 127.0.0.1 — `localhost` can be slow on some Windows setups).
4. **Register** an account, log in.
5. Upload a child's photo, fill in the details, **Create Case**.
6. View **Search Results** (ranked matches with similarity scores) and generate the **Report**.
7. Tip: if no faces have been loaded yet, run `python scripts/ingest_dataset.py --images-root FGNET/images --dataset FGNET` first to fill the database.

---

### 5. What's next (The Roadmap)
- **Age progression** (the big one): take a face and *age it* years into the future so you can search what a missing child might look like now. Plan: add a small model (Fast-AgingGAN first, upgrade to HRFAE later) with a "progress photo" feature in the UI.
  - Important caveat: an aged photo is a **visual aid** — its fingerprint does NOT match the original's, so we never search with it directly.
- **Polish & hardening:** better ranking to lift the Rank-1 score (currently 23%; the right person is usually in the top 5-10 but not always #1).
- **Real-world data:** swapping the FG-NET research dataset for a real (legally obtained) corpus when one is available.

---

### 6. Why are we doing it this way?
We used an **Accelerated Sprint** (7 days of focused work).
- **Speed:** By using pre-built AI models (like InsightFace), we don't have to "teach" the AI what a face looks like from scratch.
- **Accuracy:** Vector search is the industry standard for facial recognition (used by big tech companies).

**Don't worry if it feels like a lot!** The complex math is handled; you focus on the vision. Every time we move to a new step, this guide gets updated.

*Current status: Core system complete and verified. Next up: age progression.*