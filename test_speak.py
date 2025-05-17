# วิธีที่ 1: ใช้ pyttsx3 (ทำงานแบบออฟไลน์)
import pyttsx3
import platform
import os

def speak_text_offline(text):
    """
    ฟังก์ชั่นอ่านออกเสียงข้อความแบบออฟไลน์โดยใช้ pyttsx3
    """
    engine = pyttsx3.init()
    # สามารถปรับความเร็วในการพูดได้
    engine.setProperty('rate', 150)  # ค่าปกติคือ 200
    # สามารถเลือกเสียงได้ (ขึ้นอยู่กับระบบของคุณ)
    voices = engine.getProperty('voices')
    # เลือกเสียงแรกในระบบ (อาจเป็นเสียงภาษาไทยถ้ามี)
    engine.setProperty('voice', voices[0].id)
    
    # พูดข้อความ
    engine.say(text)
    engine.runAndWait()

# วิธีที่ 2: ใช้ gTTS (ต้องเชื่อมต่ออินเทอร์เน็ต เพราะใช้บริการ Google)
from gtts import gTTS

def speak_text_online(text, language='th'):
    """
    ฟังก์ชั่นอ่านออกเสียงข้อความโดยใช้ Google Text-to-Speech
    สนับสนุนภาษาไทยอย่างเป็นทางการ
    """
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save("output.mp3")
    
    # เล่นไฟล์เสียง (แตกต่างกันตามระบบปฏิบัติการ)
    system = platform.system()
    if system == 'Darwin':  # macOS
        os.system("afplay output.mp3")
    elif system == 'Linux':  # Linux (Raspberry Pi)
        os.system("mpg321 output.mp3")  # ต้องติดตั้ง mpg321 ก่อน: sudo apt-get install mpg321
    else:  # Windows
        os.system("start output.mp3")

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    #text_to_speak = "สวัสดีครับ นี่คือการทดสอบระบบอ่านออกเสียงภาษาไทยด้วยไพธอน"
    text_to_speak = "สวัสดีครับ คุณอะตอม  อติทัศ แก้วมะหิงษ์ อายุ 3 ขวด สี่เดือน กลัวป้าย สอสอ เจ๊จู และแผ่นดินไหว มีแม่ชือแม่ช้าง ช้าง ช้าง..."
    
    # เลือกใช้วิธีใดวิธีหนึ่ง
    # วิธีที่ 1: ออฟไลน์
    #speak_text_offline(text_to_speak)
    
    # วิธีที่ 2: ออนไลน์ (Google TTS - รองรับภาษาไทยดี)
    speak_text_online(text_to_speak, language='th')