# 📄 PDF Ofis Stüdyosu (PDF Office Studio)

Python ve CustomTkinter ile geliştirilmiş, modern arayüze sahip, çok fonksiyonlu bir PDF yönetim aracıdır. Ofis çalışanlarının günlük belge işlerini (birleştirme, ayırma, dönüştürme, imzalama) tek bir çatı altında toplar.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)

## 🌟 Özellikler

* **Sürükle & Bırak Desteği:** Dosyaları pencereye sürükleyerek işlem yapabilirsiniz.
* **Çoklu Dil Desteği:** Tek tıkla Türkçe (TR) ve İngilizce (EN) arasında geçiş.
* **Format Dönüştürme:**
    * JPG/PNG -> PDF (Toplu çeviri)
    * Word (.docx) -> PDF
* **PDF İşlemleri:**
    * **Birleştirme:** PDF'leri sıraya dizin ve tek dosyada birleştirin.
    * **Ayrıştırma & Döndürme:** Sayfaları görsel olarak görün, seçin ve ters duranları döndürün.
    * **Sıkıştırma:** Dosya boyutunu kalite ayarı yaparak düşürün.
* **Akıllı İmza & Kaşe:**
    * İmza resimlerinin arka planını otomatik temizler (Şeffaf yapar).
    * İmzayı belge üzerinde sürükleyip istediğiniz konuma yerleştirebilirsiniz.
    * Kaydetmeden önce tam ekran önizleme yapabilirsiniz.

## 🛠️ Kurulum ve Çalıştırma

Bu projeyi bilgisayarınızda çalıştırmak için:

1.  Repoyu klonlayın:
    ```bash
    git clone [https://github.com/KULLANICI_ADIN/PDF-Ofis-Studyosu.git](https://github.com/KULLANICI_ADIN/PDF-Ofis-Studyosu.git)
    ```
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayı başlatın:
    ```bash
    python main.py
    ```

## 📦 EXE Oluşturma

Projeyi tek bir çalıştırılabilir (.exe) dosyaya dönüştürmek için hazır scripti kullanabilirsiniz:

```bash
python exe_olustur.py