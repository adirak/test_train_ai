#!/bin/bash

echo "เริ่มการติดตั้งระบบจดจำใบหน้าบน Raspberry Pi"

# 1. ติดตั้งแพ็คเกจที่จำเป็น
echo "ติดตั้งแพ็คเกจที่จำเป็น..."
sudo apt update
sudo apt install -y build-essential cmake
sudo apt install -y libopenblas-dev liblapack-dev 
sudo apt install -y python3-dev python3-opencv
sudo apt install -y python3-full python3-venv
sudo apt install -y espeak

# 2. สร้าง virtual environment
echo "สร้าง virtual environment..."
python3 -m venv ~/face_env

# 3. เปิดใช้งาน virtual environment และติดตั้งแพ็คเกจ
echo "ติดตั้งแพ็คเกจใน virtual environment..."
source ~/face_env/bin/activate
pip install --upgrade pip
pip install numpy
pip install dlib --no-cache-dir
pip install face_recognition
pip install pyttsx3
pip install opencv-python

# 4. สร้างไฟล์สคริปต์สำหรับรันโปรแกรม
echo "สร้างสคริปต์สำหรับรันโปรแกรม..."
echo '#!/bin/bash
source ~/face_env/bin/activate
python3 /home/admin/pi/train_ai/recognize_faces2.py
deactivate' > ~/run_face_recognition.sh

chmod +x ~/run_face_recognition.sh

echo "การติดตั้งเสร็จสมบูรณ์"
echo "สั่งรันโปรแกรมด้วยคำสั่ง: ~/run_face_recognition.sh"