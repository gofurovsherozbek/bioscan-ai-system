import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# CORS sozlamalari (Frontend ulanishi uchun)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# OpenCV yuz aniqlagich (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

DB_FILE = "biometric_db.json"

def get_face_vector(image_bytes):
    # Rasmni OpenCV formatiga o'tkazish
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Yuzni aniqlash
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        return None
    
    # Birinchi yuzni qirqib olish va o'lchamini bir xillashtirish (100x100)
    (x, y, w, h) = faces[0]
    face_roi = gray[y:y+h, x:x+w]
    face_resized = cv2.resize(face_roi, (100, 100))
    
    # Oddiy vektorizatsiya: Gistogramma (LBPH kabi)
    # Bu yerda rasmni 1D massivga aylantiramiz (10000 o'lchamli vektor)
    vector = face_resized.flatten() / 255.0 # Normallashtirish
    return vector.tolist()

@app.post("/register")
async def register(username: str = Form(...), files: list[UploadFile] = File(...)):
    all_vectors = []
    
    for file in files[:5]: # Faqat 5 ta rasm
        content = await file.read()
        vector = get_face_vector(content)
        if vector:
            all_vectors.append(vector)
    
    if len(all_vectors) < 3: # Kamida 3 tasi muvaffaqiyatli bo'lishi kerak
        return {"status": "error", "message": "Yuzlar aniqlanmadi yoki rasmlar sifatsiz"}

    # 5 ta rasmning o'rtacha vektori (Eng barqaror natija uchun)
    final_vector = np.mean(all_vectors, axis=0).tolist()

    # Bazaga yozish
    db = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    
    db[username] = final_vector
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

    return {"status": "success", "username": username, "vector_size": len(final_vector)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)