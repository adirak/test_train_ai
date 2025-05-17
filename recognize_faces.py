import cv2
import face_recognition
import pickle
import time
import numpy as np
import os
from gtts import gTTS
from playsound import playsound
import threading
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# โหลดข้อมูลใบหน้าที่บันทึกไว้
with open("face_encodings.pkl", "rb") as f:
    known_face_encodings = pickle.load(f)

# แยกข้อมูลเป็นรายชื่อและ encodings
known_names = list(known_face_encodings.keys())
known_encodings = list(known_face_encodings.values())

print(f"โหลดใบหน้าทั้งหมด {len(known_names)} คน:")
for name in known_names:
    print(f"- {name}")

# ฟังก์ชันสำหรับสร้างและเล่นเสียงทักทาย
def speak_thai(text):
    try:
        tts = gTTS(text=text, lang='th')
        filename = "temp_voice.mp3"
        tts.save(filename)
        playsound(filename)
        if os.path.exists(filename):
            os.remove(filename)  # ลบไฟล์หลังจากเล่นเสียงเสร็จ
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเล่นเสียง: {str(e)}")

# ฟังก์ชันสำหรับวาดข้อความภาษาไทย
def put_thai_text(img, text, position, font_size=32, color=(255, 255, 255)):
    # แปลงภาพจาก OpenCV เป็น PIL
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # โหลดฟอนต์ภาษาไทย
    font = ImageFont.truetype("fonts/THSarabunNew.ttf", font_size)
    
    # วาดข้อความ
    draw.text(position, text, font=font, fill=color)
    
    # แปลงกลับเป็น OpenCV
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# เปิดกล้อง
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ไม่สามารถเปิดกล้องได้")
    exit()

# ตัวแปรเก็บชื่อล่าสุดที่พบ เพื่อป้องกันการทักทายซ้ำ
last_greeted = ""
last_greeting_time = 0
greeting_cooldown = 10  # จำนวนวินาทีก่อนทักทายซ้ำ

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
                # คำนวณระยะห่างระหว่างใบหน้าที่พบกับใบหน้าที่รู้จักทั้งหมด
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                # ใช้ค่า threshold ที่เข้มงวดขึ้น (0.4)
                if face_distances[best_match_index] < 0.4:
                    name = known_names[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                    
                    # ทักทายถ้าเป็นคนใหม่หรือเจอคนเดิมหลังจากผ่านไปตามเวลาที่กำหนด
                    current_time = time.time()
                    if name != last_greeted or (current_time - last_greeting_time) > greeting_cooldown:
                        greeting = f"สวัสดี {name}"
                        print(f"{greeting} (ความมั่นใจ: {confidence:.2%})")
                        # ใช้ thread เพื่อไม่ให้การพูดขัดขวางการทำงานหลัก
                        threading.Thread(target=speak_thai, args=(greeting,)).start()
                        last_greeted = name
                        last_greeting_time = current_time
                else:
                    name = "ไม่รู้จัก"
                    confidence = 0
                
                # วาดกรอบและชื่อบนภาพ (ปรับขนาดกลับ)
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # สีจะเปลี่ยนตามคนที่รู้จักหรือไม่รู้จัก
                color = (0, 0, 255) if name == "ไม่รู้จัก" else (0, 255, 0)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                label = f"{name} ({confidence:.2%})" if name != "ไม่รู้จัก" else name
                # ใช้ฟังก์ชัน put_thai_text แทน cv2.putText
                frame = put_thai_text(frame, label, (left, bottom + 30), font_size=48, color=color)
    
    process_this_frame = not process_this_frame
    
    # แสดงภาพ
    cv2.imshow('Face Recognition', frame)
    
    # กด 'q' เพื่อออก
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()