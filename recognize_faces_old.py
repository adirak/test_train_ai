import cv2
import face_recognition
import pickle
import time
import numpy as np
from gtts import gTTS
import platform
import os

# โหลดข้อมูลใบหน้าที่บันทึกไว้
with open("face_encodings.pkl", "rb") as f:
    known_face_encodings = pickle.load(f)

# แยกข้อมูลเป็นรายชื่อและ encodings
known_names = list(known_face_encodings.keys())
known_encodings = list(known_face_encodings.values())

print(f"โหลดใบหน้าทั้งหมด {len(known_names)} คน:")
for name in known_names:
    print(f"- {name}")

# เปิดกล้อง
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ไม่สามารถเปิดกล้องได้")
    exit()

# ตัวแปรเก็บชื่อล่าสุดที่พบ เพื่อป้องกันการทักทายซ้ำ
last_greeted = ""
last_greeting_time = 0
greeting_cooldown = 10  # จำนวนวินาทีก่อนทักทายซ้ำ

def speak_text(text, language='th'):
    """
    ฟังก์ชั่นอ่านออกเสียงข้อความโดยใช้ Google Text-to-Speech
    """
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save("greeting.mp3")
    
    # เล่นไฟล์เสียง (แตกต่างกันตามระบบปฏิบัติการ)
    system = platform.system()
    if system == 'Darwin':  # macOS
        os.system("afplay greeting.mp3")
    elif system == 'Linux':  # Linux (Raspberry Pi)
        os.system("mpg321 greeting.mp3")  # ต้องติดตั้ง mpg321 ก่อน: sudo apt-get install mpg321
    else:  # Windows
        os.system("start greeting.mp3")

print("กด 'q' เพื่อออกจากโปรแกรม")

process_this_frame = True

while True:
    ret, frame = camera.read()
    
    if not ret:
        print("ไม่สามารถอ่านภาพจากกล้องได้")
        break
    
    # ประมวลผลเฉพาะเฟรมที่ต้องการเพื่อเพิ่มประสิทธิภาพ
    if process_this_frame:
        # ลดขนาดภาพเพื่อเพิ่มประสิทธิภาพ
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        # แปลงสีจาก BGR เป็น RGB
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # หาตำแหน่งใบหน้าในภาพ
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        
        # หา encodings สำหรับใบหน้าที่พบ
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            # ตรวจสอบแต่ละใบหน้าที่พบ
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # เปรียบเทียบกับใบหน้าที่รู้จัก
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
                name = "Unknown"
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    
                    # ทักทายถ้าเป็นคนใหม่หรือเจอคนเดิมหลังจากผ่านไปตามเวลาที่กำหนด
                    current_time = time.time()
                    if name != last_greeted or (current_time - last_greeting_time) > greeting_cooldown:
                        greeting = f"สวัสดี {name}"
                        print(greeting)
                        speak_text(greeting, language='th')
                        last_greeted = name
                        last_greeting_time = current_time
                
                # วาดกรอบและชื่อบนภาพ (ปรับขนาดกลับ)
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # สีจะเปลี่ยนตามคนที่รู้จักหรือไม่รู้จัก
                color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 1)
    
    process_this_frame = not process_this_frame
    
    # แสดงภาพ
    cv2.imshow('Face Recognition', frame)
    
    # กด 'q' เพื่อออก
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()