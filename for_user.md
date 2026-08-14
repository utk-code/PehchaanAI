# PehchaanAI: Missing Child Identification AI System
## A Guide for You: Understanding What We're Building

Welcome! This document explains everything we've done so far and what's coming next, using simple language to help you "absorb" the technical side of the project.

---

### 1. The Big Picture
We are building a system where a user (like a parent or police officer) can upload a photo of a missing child. The AI will then:
1. **Find the face** in the photo.
2. **Convert that face** into a mathematical "fingerprint" (called an embedding).
3. **Search a database** to see if that "fingerprint" matches any other known records.

---

### 2. What we have done so far (The Foundation)

#### **Project Structure (The Folders)**
We've organized the project into two main parts:
- **`backend/`**: This is the "Brain." It handles the logic, the database, and the AI math.
- **`frontend/`**: This is the "Face." It’s what you see in your browser (buttons, forms, images).

#### **Docker (The Container)**
Think of **Docker** as a "shipping container." It packages our entire system so it runs exactly the same on my computer, your computer, or a server. It saves us from "but it worked on my machine!" errors.

#### **Authentication (The Key)**
We've built a system for users to **Register** and **Login**.
- **JWT (JSON Web Tokens):** This is like a "VIP Wristband." Once you log in, the server gives you this token. You show it every time you ask the server for data, so it knows who you are.
- **FastAPI:** This is the tool we use to build the "doors" (API endpoints) to our backend.

#### **The Database (The Memory)**
We are using **PostgreSQL** with something called **pgvector**. 
- Regular databases are good at searching for text (like "Name: John").
- **pgvector** is special because it can search for *shapes and math* (like "Find faces that look 95% like this one").

---

### 3. What we are about to do (The Magic)

Our next big step is **Day 3: Face Detection & Case Management**.

#### **Face Detection (Finding the Face)**
- **The Tool:** We will use **InsightFace** and **OpenCV**.
- **The Why:** A photo might have a background, trees, or multiple people. We need the AI to specifically "crop" out the child's face and ignore everything else.

#### **Embeddings (Turning Faces into Numbers)**
- **The Process:** AI models look at a face and measure things like the distance between eyes, the curve of the nose, etc. It turns these features into a list of 512 numbers.
- **The Why:** Computers are terrible at comparing images, but they are *lightning fast* at comparing numbers.

#### **Case Management (Organizing Information)**
- We will create "Cases." A case includes the child's photo, name, last known location, and the date they went missing.
- This allows us to search not just by face, but also by "Find a child who went missing in this city."

---

### 4. Simple Analogy: The Restaurant
To understand how the different parts work together:
- **You (The User):** Sits at a table (the **Frontend**).
- **The Menu:** Shows you what you can order (the **API**).
- **The Waiter:** Takes your order to the kitchen (**FastAPI**).
- **The Kitchen:** Cooks the food (the **Backend logic & AI**).
- **The Pantry:** Where ingredients are stored (the **Database**).

---

### 5. Why are we doing it this way?
We are using an **Accelerated Sprint** (7 days). 
- **Speed:** By using pre-built AI models (like InsightFace), we don't have to "teach" the AI what a face looks like from scratch. 
- **Accuracy:** Vector search is the industry standard for facial recognition (used by big tech companies).

---

### How to use this project?
Once we finish Day 5, you will be able to:
1. Open your browser.
2. Log in.
3. Upload a photo.
4. See a list of matches instantly.

**Don't worry if it feels like a lot!** My job is to handle the complex math and code, while you focus on the vision of the project. Every time we move to a new step, I'll explain it in this way.

*Next Step: Creating the "Case" system in the database!*
