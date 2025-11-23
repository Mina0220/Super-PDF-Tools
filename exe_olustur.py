import PyInstaller.__main__
import os
import customtkinter
import tkinterdnd2

# --- Kütüphane Yollarını Otomatik Bul ---
ctk_path = os.path.dirname(customtkinter.__file__)
tkdnd_path = os.path.dirname(tkinterdnd2.__file__)

print("Kütüphane yolları bulundu:")
print(f"CustomTkinter: {ctk_path}")
print(f"TkinterDnD2: {tkdnd_path}")

# --- PyInstaller Komutunu Çalıştır ---
PyInstaller.__main__.run([
    'main.py',                            # Dönüştürülecek dosya
    '--name=PDF_Ofis_Asistani',           # EXE'nin adı
    '--onefile',                          # Tek bir dosya olsun
    '--windowed',                         # Konsol (siyah ekran) açılmasın
    '--noconsole',                        # Konsol açılmasın (garanti olsun)
    f'--add-data={ctk_path};customtkinter', # CustomTkinter dosyalarını ekle
    f'--add-data={tkdnd_path};tkinterdnd2', # Sürükle-Bırak dosyalarını ekle
    '--icon=icon.ico',                    # Bu satırı güncelledik! icon.ico dosyasını kullanacak
    '--clean',                            # Önbelleği temizle
])

print("\n-----------------------------------------------------------")
print("  EXE oluşturma işlemi tamamlandı!")
print(f"  EXE dosyanız: {os.path.join(os.getcwd(), 'dist', 'PDF_Ofis_Asistani.exe')}")
print("  Lütfen 'dist' klasörünü kontrol edin.")
print("-----------------------------------------------------------")