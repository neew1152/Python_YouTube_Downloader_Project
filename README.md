# 🎥 Python YouTube Video Downloader Project

A YouTube video downloader built with Python, using `customtkinter` for a modern GUI and `yt-dlp`/`pytube` for downloading video and audio content. This app allows users to:

- View available video/audio formats for any YouTube video
- Choose specific stream IDs to download
- Monitor download progress

---

## 📦 Features

- ✅ Sleek modern interface using `customtkinter`
- ✅ Video/audio format listing via `yt-dlp`
- ✅ Progress tracking and terminal output
- ✅ Optional file renaming
- ✅ Auto-scroll output (on/off toggle)
- ✅ Light/Dark mode switch

---

## 🔧 Requirements

Install the necessary dependencies using pip:

```bash
pip install customtkinter
pip install yt-dlp
pip install pytube
pip install tk
pip install pillow
```` 

---

## 🚀 How to Run

1. Clone or download this repository.
2. Ensure the required packages are installed.
3. Run the script:

```bash
python Python_YouTube_Downloader_Project.py
```

---

## 🖥️ How to Use

1. Paste a YouTube video URL into the URL input field.
2. Click **Search** to retrieve video metadata and available format IDs.
3. Review available formats in the terminal output window.
4. Enter the desired format **ID** in the provided input field.
5. (Optional) Rename the file using the rename input field.
6. Click **Download** to start downloading the video/audio.

---

## 📁 Output Location

All downloaded files will be saved in the `Downloads/` directory (created automatically if it doesn't exist).

---

## 📚 Credits & Resources

The project was inspired by several YouTube tutorials and resources, including:

* https://www.youtube.com/watch?v=NI9LXzo0UY0
* https://www.youtube.com/watch?v=Miydkti_QVE
* https://www.youtube.com/watch?v=Envp9yHb2Ho
* https://www.youtube.com/watch?v=EwL2BwEdduE
* https://www.youtube.com/watch?v=a0MVOloNLB4
* https://www.youtube.com/watch?v=GeflXCubyrA
* https://www.youtube.com/watch?v=QRroCuY1Bhc
* https://www.youtube.com/watch?v=df30Qro3Iu4
* ChatGPT 3.5/GPT-4o
* GitHub
* Google

---

## ⚠️ Disclaimer

This project is for educational purposes only.

---
---

# 🎥 Python YouTube Video Downloader Project

แอปดาวน์โหลดวิดีโอบนยูทูบโดยใช้ `python`, `customtkinter` และ `yt-dlp`/`pytube`

---

## 📦 คุณสมบัติ

- ✅ อินเทอร์เฟซ `customtkinter`
- ✅ รายการฟอร์แมตวิดีโอ / เสียง `yt-dlp`
- ✅ การติดตามความคืบหน้าและเอาต์พุตเทอร์มินัล
- ✅ การเปลี่ยนชื่อไฟล์
- ✅ เอาต์พุตเลื่อนอัตโนมัติ (สลับเปิด / ปิด)
- ✅ สวิตช์โหมดสว่าง / มืด

---

## 🔧 ความต้องการ

ติดตั้ง dependencies ที่จำเป็นโดยใช้ pip :

```bash
pip install customtkinter
pip install yt-dlp
pip install pytube
pip install tk
pip install pillow
````

---

## 🚀 วิธีใช้

1. โคลนหรือดาวน์โหลด Repository นี้
2. ติดตั้งแพ็กเกจที่จำเป็น
3. เรียกใช้สคริปต์:

```bash
python Python_YouTube_Downloader_Project.py
```

---

## 🖥️ วิธีการใช้งาน

1. ป้อน URL วิดีโอ YouTube ลงในช่อง URL
2. คลิก **Search** เพื่อค้นหาข้อมูลเมตา
3. ตรวจสอบฟอร์แมตที่ใช้งานได้ในช่องผลลัพธ์ของเทอร์มินัล
4. ป้อน **ID** รูปแบบที่ต้องการลงในช่องป้อนที่ให้มา
5. (ไม่บังคับ) เปลี่ยนชื่อไฟล์โดยใช้ช่องป้อนเปลี่ยนชื่อ
6. คลิก **Download** เพื่อเริ่มดาวน์โหลด

---

## 📁 ตำแหน่งเอาต์พุต

ไฟล์ที่ดาวน์โหลดทั้งหมดจะถูกบันทึกไว้ในไดเรกทอรี `Downloads/` (สร้างขึ้นอัตโนมัติหากไม่มี)

---

## 📚 เครดิตและแหล่งข้อมูล

โพรเจกต์นี้ได้รับแรงบันดาลใจจากวิดีโอสอนและแหล่งข้อมูลมากมายบน YouTube รวมถึง :

* https://www.youtube.com/watch?v=NI9LXzo0UY0
* https://www.youtube.com/watch?v=Miydkti_QVE
* https://www.youtube.com/watch?v=Envp9yHb2Ho
* https://www.youtube.com/watch?v=EwL2BwEdduE
* https://www.youtube.com/watch?v=a0MVOloNLB4
* https://www.youtube.com/watch?v=GeflXCubyrA
* https://www.youtube.com/watch?v=QRroCuY1Bhc
* https://www.youtube.com/watch?v=df30Qro3Iu4
* ChatGPT 3.5 / GPT-4o
* GitHub
* Google

---

## ⚠️ ข้อสงวนสิทธิ์

โพรเจกต์นี้มีวัตถุประสงค์เพื่อการศึกษาเท่านั้น

---

⏳ Future Update:
- ffmpeg รวมเสียงกับวิดีโอทีเดียวเลย
- เขียนใหม่ ลด process ที่ไม่จำเป็น

อยากทำต่อนะ แต่ไม่มีเวลาว่างเลยยยย แล้วก็โดนคนที่ชอบหักอกมาอีกกกกกก (ชีวิตโคตรเศร้า)

โพรเจกต์นี้เริ่มทำตอน ป.6 (แต่อัปโหลดขึ้น GitHub ตอน ม.2) ตั้งแต่โดนแฟนเก่าคนแรกทิ้ง ไม่รู้จะทำไร เลยมาเขียนนี้
