---

# 📄 PDF Office Studio (Ultimate)

A multifunctional, modern desktop application for PDF management, developed with **Python** and **CustomTkinter**. It streamlines daily document tasks (merging, splitting, converting, signing) under a single roof.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)

## 🌟 Features

* **Drag & Drop Support:** Process files easily by dragging them into the window.
* **Multi-Language Support:** Toggle between Turkish (TR) and English (EN) instantly.
* **Format Conversion:**
    * JPG/PNG -> PDF (Batch conversion)
    * Word (.docx) -> PDF
* **PDF Operations:**
    * **Merge:** Queue PDFs and combine them into a single file.
    * **Split & Rotate:** Visual interface to select specific pages and rotate incorrect orientations.
    * **Compress:** Reduce file size with adjustable quality slider.
* **Smart Stamp & Sign:**
    * **Auto-Transparency:** Automatically removes white backgrounds from uploaded signature/stamp images.
    * **Movable Objects:** Drag and drop your signature to the exact position on the document.
    * **Preview Mode:** Full-screen preview before saving.

## 🛠️ Installation & Usage

To run this project on your local machine:

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/PDF-Office-Studio.git](https://github.com/YOUR_USERNAME/PDF-Office-Studio.git)
    ```
2.  Install required packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## 📦 Create Executable (.exe)

You can use the included script to package the app into a single standalone `.exe` file:

```bash
python exe_olustur.py
