import os
import pickle
import face_recognition
import cv2
import numpy as np
from tqdm import tqdm  # ใช้แสดงความคืบหน้า (ติดตั้งด้วย pip install tqdm ถ้ายังไม่มี)

def train_from_folders(base_dir="img/faces"):
    """
    สร้างโมเดลจดจำใบหน้าจากรูปในโฟลเดอร์
    โครงสร้างโฟลเดอร์: img/faces/name/xx.jpg
    
    Returns:
        dict: ชื่อและ face encoding ของแต่ละคน
    """
    face_encodings_dict = {}
    
    # วนลูปผ่านโฟลเดอร์ของแต่ละคน
    for person_name in os.listdir(base_dir):
        person_dir = os.path.join(base_dir, person_name)
        
        # ข้ามไฟล์ที่ไม่ใช่โฟลเดอร์
        if not os.path.isdir(person_dir):
            continue
            
        print(f"กำลัง training ใบหน้าของ {person_name}...")
        person_encodings = []
        
        # วนลูปผ่านรูปภาพในโฟลเดอร์ของคนนี้
        image_files = [f for f in os.listdir(person_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for image_file in tqdm(image_files, desc=f"Processing {person_name}"):
            image_path = os.path.join(person_dir, image_file)
            
            try:
                # โหลดรูปและค้นหาใบหน้า
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                
                # ถ้าพบใบหน้าในรูป
                if len(face_locations) > 0:
                    # ใช้ใบหน้าแรกที่พบในรูป
                    face_encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
                    person_encodings.append(face_encoding)
                else:
                    print(f"  ไม่พบใบหน้าในไฟล์ {image_file}")
            except Exception as e:
                print(f"  เกิดข้อผิดพลาดกับไฟล์ {image_file}: {str(e)}")
        
        # ถ้ามีการเข้ารหัสใบหน้าอย่างน้อย 1 รูป
        if person_encodings:
            # เฉลี่ยการเข้ารหัสใบหน้าทั้งหมดเพื่อให้ได้ตัวแทนที่ดี
            face_encodings_dict[person_name] = np.mean(person_encodings, axis=0)
            print(f"  สำเร็จ: บันทึก {len(person_encodings)} ใบหน้าของ {person_name}")
        else:
            print(f"  ไม่สามารถพบใบหน้าในรูปภาพใดๆ ของ {person_name}")
    
    # บันทึกไฟล์ encodings
    with open("face_encodings.pkl", "wb") as f:
        pickle.dump(face_encodings_dict, f)
    
    print(f"บันทึกการเข้ารหัสใบหน้าสำเร็จ! จำนวนทั้งหมด {len(face_encodings_dict)} คน")
    return face_encodings_dict

if __name__ == "__main__":
    train_from_folders()
    
    # ทดสอบโหลดไฟล์
    with open("face_encodings.pkl", "rb") as f:
        loaded_encodings = pickle.load(f)
    
    print("\nรายชื่อที่ได้รับการฝึก:")
    for name in loaded_encodings.keys():
        print(f"- {name}")