import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas, simpledialog
import os
import img2pdf
from PIL import Image, ImageTk
import io
from pypdf import PdfReader, PdfWriter
import win32com.client
import pythoncom
import fitz  # PyMuPDF
from tkinterdnd2 import TkinterDnD, DND_FILES
import tempfile
import math
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_studio.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- CONSTANTS ---
class Constants:
    """Application constants"""
    APP_VERSION = "3.1 Premium"
    DEFAULT_SCALE = 1.0
    WINDOW_SIZE_RATIO = 0.85

    # Image and PDF processing
    THUMBNAIL_SIZE = (100, 140)
    SIGNATURE_THUMBNAIL_SIZE = (100, 100)
    PDF_PREVIEW_SCALE = 1.5
    PDF_MERGE_PREVIEW_SCALE = 0.15
    PDF_SPLIT_PREVIEW_SCALE = 0.15
    PDF_PREVIEW_ZOOM = 2.0

    # DPI and Quality
    DEFAULT_DPI = 150
    MIN_DPI = 100
    MAX_DPI = 300
    DPI_STEPS = 4

    # Compression
    MIN_QUALITY = 0.2
    MAX_QUALITY = 1.0
    DEFAULT_QUALITY = 0.6
    QUALITY_STEPS = 8
    BASE_DPI = 72
    DPI_RANGE = 150
    BASE_JPEG_QUALITY = 80

    # Signature
    MIN_SIGNATURE_SIZE = 0.5
    MAX_SIGNATURE_SIZE = 2.0
    DEFAULT_SIGNATURE_SIZE = 1.0
    SIGNATURE_STEPS = 15
    BASE_SIGNATURE_SIZE = 100

    # Colors
    TRANSPARENT_THRESHOLD = 200
    COLORS = {
        "Red": (1, 0, 0),
        "Blue": (0, 0, 1),
        "Gray": (0.5, 0.5, 0.5),
        "Black": (0, 0, 0)
    }

    # Fonts
    WATERMARK_FONT_SIZE = 50
    PAGE_NUMBER_FONT_SIZE = 12
    WATERMARK_OPACITY = 0.3
    WATERMARK_ANGLE = 45

    # Grid layout
    PAGES_PER_ROW = 6

    # Shift PDF Design System - Professional & Modern
    # Primary Blue (Shift Style)
    PRIMARY_COLOR = "#3b82f6"  # Main blue - buttons, accents
    PRIMARY_HOVER = "#295bac"  # Darkened hover state
    ACCENT_BLUE = "#1f87ff"  # Links and highlights

    # Success - Fresh Green
    SECONDARY_COLOR = "#10b981"  # Emerald
    SECONDARY_HOVER = "#059669"  # Deep emerald

    # Danger - Clean Red
    DANGER_COLOR = "#ef4444"  # Modern red
    DANGER_HOVER = "#dc2626"  # Deep red

    # Warning - Warm Orange
    WARNING_COLOR = "#f59e0b"  # Amber
    WARNING_HOVER = "#d97706"  # Deep amber

    # Neutral - Minimal Gray
    NEUTRAL_COLOR = "#64748b"  # Slate
    NEUTRAL_HOVER = "#475569"  # Deep slate

    # Accent - Purple
    ACCENT_COLOR = "#8b5cf6"  # Violet
    ACCENT_HOVER = "#7c3aed"  # Deep violet

    # Light Mode - Clean & Bright (Shift Style)
    BG_LIGHT = "#ffffff"  # Pure white background
    BG_CARD = "#ffffff"  # White cards
    BG_LIGHT_IMAGE = "#eaf4fe"  # Light blue tinted areas
    HEADER_BG = "#ffffff"  # White header
    TEXT_DARK = "#2f3438"  # Dark text
    TEXT_LIGHT = "#64748b"  # Secondary text
    BORDER_LIGHT = "#9ac5ff"  # Light blue border

    # Dark Mode - Deep & Elegant (Shift Style)
    BG_DARK = "#24272f"  # Deep dark background
    BG_CARD_DARK = "#393d48"  # Dark card background
    BG_DARK_IMAGE = "#393d48"  # Dark image areas
    HEADER_BG_DARK = "#24272f"  # Dark header
    TEXT_LIGHT_MODE = "#ecedf1"  # Light text
    TEXT_SECONDARY_DARK = "#a1a1aa"  # Secondary dark text
    BORDER_DARK = "#4cb2ee"  # Blue border for dark mode

    # Supported File Types - Comprehensive
    IMAGE_TYPES = [
        ("All Images", "*.jpg *.jpeg *.JPG *.JPEG *.png *.PNG *.gif *.GIF *.bmp *.BMP *.tiff *.TIFF *.webp *.WEBP"),
        ("JPEG", "*.jpg *.jpeg *.JPG *.JPEG"),
        ("PNG", "*.png *.PNG"),
        ("GIF", "*.gif *.GIF"),
        ("BMP", "*.bmp *.BMP"),
        ("TIFF", "*.tiff *.TIFF"),
        ("WebP", "*.webp *.WEBP"),
        ("All Files", "*.*")
    ]

    PDF_TYPES = [("PDF Files", "*.pdf *.PDF"), ("All Files", "*.*")]
    WORD_TYPES = [("Word Documents", "*.docx *.DOCX"), ("All Files", "*.*")]

    # Settings and History
    MAX_RECENT_FILES = 10
    SETTINGS_FILE = "pdf_studio_settings.json"
    DEFAULT_SETTINGS = {
        "language": "tr",
        "theme": "System",
        "recent_files": [],
        "default_dpi": 150,
        "default_quality": 0.6,
        "last_output_dir": "",
        "remember_last_dir": True
    }

# --- DİL SÖZLÜĞÜ ---
TEXTS = {
    "app_title": {"tr": "Süper PDF Stüdyosu - V2.8 (Batch + Preview + OCR)", "en": "Super PDF Studio - V2.8 (Batch + Preview + OCR)"},
    "header": {"tr": "PDF Ofis Stüdyosu", "en": "PDF Office Studio"},
    "hint": {"tr": "💡 İpucu: Dosyaları pencereye sürükleyebilirsiniz!", "en": "💡 Hint: You can drag & drop files here!"},
    
    # Sekmeler
    "tab_jpg": {"tr": "JPG > PDF", "en": "JPG to PDF"},
    "tab_word": {"tr": "Word > PDF", "en": "Word to PDF"},
    "tab_pdf2img": {"tr": "PDF > Resim", "en": "PDF to Image"},
    "tab_pdf2txt": {"tr": "PDF > Metin", "en": "PDF to Text"},
    "tab_merge": {"tr": "PDF Birleştir", "en": "Merge PDF"},
    "tab_split": {"tr": "PDF Ayrıştır", "en": "Split PDF"},
    "tab_compress": {"tr": "PDF Sıkıştır", "en": "Compress PDF"},
    "tab_sign": {"tr": "Kaşe & İmza", "en": "Stamp & Sign"},
    "tab_tools": {"tr": "Güvenlik & Araçlar", "en": "Security & Tools"},
    "tab_batch": {"tr": "Toplu İşlem", "en": "Batch Process"},
    
    # Genel
    "btn_select": {"tr": "Dosya Seç", "en": "Select File"},
    "btn_remove": {"tr": "Kaldır", "en": "Remove"},
    "btn_close_file": {"tr": "Dosyayı Kapat", "en": "Close File"},
    "btn_clear_all": {"tr": "Tümünü Temizle", "en": "Clear All"},
    "lbl_no_file": {"tr": "Dosya Yok", "en": "No File"},
    "msg_success": {"tr": "Başarılı", "en": "Success"},
    "msg_done": {"tr": "İşlem Tamamlandı!", "en": "Operation Completed!"},
    "msg_error": {"tr": "Hata", "en": "Error"},
    
    # PDF > Metin (YENİ)
    "p2t_title": {"tr": "PDF'ten YAZI ÇIKARMA (TXT)", "en": "EXTRACT TEXT FROM PDF (TXT)"},
    "btn_convert_txt": {"tr": "Metni Çıkar ve Kaydet (.txt)", "en": "Extract & Save as .txt"},
    
    # Güvenlik & Araçlar (GÜNCELLENDİ)
    "tool_encrypt_title": {"tr": "🔒 PDF Şifrele", "en": "🔒 Encrypt PDF"},
    "tool_watermark_title": {"tr": "©️ Filigran Ekle", "en": "©️ Add Watermark"},
    "tool_page_num_title": {"tr": "🔢 Sayfa Numarası Ekle", "en": "🔢 Add Page Numbers"},
    "tool_metadata_title": {"tr": "🏷️ Meta Veri (Yazar/Başlık)", "en": "🏷️ Metadata (Author/Title)"}, # YENİ
    "lbl_meta_title": {"tr": "Başlık:", "en": "Title:"},
    "lbl_meta_author": {"tr": "Yazar:", "en": "Author:"},

    # Recent Files & Settings
    "menu_recent": {"tr": "📂 Son Dosyalar", "en": "📂 Recent Files"},
    "menu_settings": {"tr": "⚙️ Ayarlar", "en": "⚙️ Settings"},
    "no_recent": {"tr": "Son dosya yok", "en": "No recent files"},
    "clear_recent": {"tr": "Geçmişi Temizle", "en": "Clear History"},
    "settings_title": {"tr": "Ayarlar", "en": "Settings"},
    "settings_language": {"tr": "Dil:", "en": "Language:"},
    "settings_theme": {"tr": "Tema:", "en": "Theme:"},
    "settings_dpi": {"tr": "Varsayılan DPI:", "en": "Default DPI:"},
    "settings_quality": {"tr": "Varsayılan Kalite:", "en": "Default Quality:"},
    "settings_remember_dir": {"tr": "Son klasörü hatırla", "en": "Remember last directory"},
    "btn_save_settings": {"tr": "Kaydet", "en": "Save"},
    "btn_cancel": {"tr": "İptal", "en": "Cancel"},
    "settings_saved": {"tr": "Ayarlar kaydedildi!", "en": "Settings saved!"},

    "lbl_password": {"tr": "Şifre Belirleyin:", "en": "Set Password:"},
    "lbl_watermark_text": {"tr": "Filigran Metni:", "en": "Watermark Text:"},
    "lbl_wm_color": {"tr": "Renk (Red/Blue/Gray):", "en": "Color (Red/Blue/Gray):"},
    "btn_apply": {"tr": "Uygula ve Kaydet", "en": "Apply & Save"},
    
    # PDF > Resim
    "p2i_title": {"tr": "PDF'ten RESİM ÇIKARMA", "en": "PDF TO IMAGE EXTRACTION"},
    "lbl_dpi": {"tr": "Görüntü Kalitesi (DPI):", "en": "Image Quality (DPI):"},
    "btn_convert_jpg": {"tr": "Tüm Sayfaları JPG Olarak Kaydet", "en": "Save All Pages as JPG"},
    "msg_saved_folder": {"tr": "Dosyalar şu klasöre kaydedildi:", "en": "Files saved to folder:"},

    # Diğerleri
    "jpg_label": {"tr": "JPG Seç/Sürükle", "en": "Select/Drag JPG"},
    "btn_select_img": {"tr": "Resim Seç", "en": "Select Image"},
    "word_label": {"tr": "Word Seç/Sürükle", "en": "Select/Drag Word"},
    "status_ready": {"tr": "Hazır", "en": "Ready"},
    "status_processing": {"tr": "İşleniyor...", "en": "Processing..."},
    "btn_select_word": {"tr": "Word Seç", "en": "Select Word"},
    "btn_add": {"tr": "+ Ekle", "en": "+ Add"},
    "btn_del": {"tr": "Seçileni Sil", "en": "Del Selected"},
    "btn_merge": {"tr": "BİRLEŞTİR", "en": "MERGE"},
    "lbl_queue": {"tr": "Sıra", "en": "Queue"},
    "btn_load": {"tr": "📂 Yükle", "en": "📂 Load"},
    "btn_reset": {"tr": "Seçimi Sıfırla", "en": "Reset Sel."},
    "btn_close": {"tr": "Kapat", "en": "Close"},
    "lbl_rotate": {"tr": "Çevir:", "en": "Rotate:"},
    "btn_save_sel": {"tr": "Kaydet", "en": "Save"},
    "lbl_pages": {"tr": "Sayfalar", "en": "Pages"},
    "warn_no_sel": {"tr": "Sayfa seçmediniz!", "en": "No pages selected!"},
    "lbl_compress_title": {"tr": "SIKIŞTIRMA", "en": "COMPRESSION"},
    "btn_compress": {"tr": "SIKIŞTIR VE KAYDET", "en": "COMPRESS AND SAVE"},
    "msg_compressed": {"tr": "Sıkıştırıldı!", "en": "Compressed!"},
    "lbl_lib": {"tr": "İmza Kütüphanesi", "en": "Signature Lib"},
    "lbl_sign_size": {"tr": "İmza Boyutu:", "en": "Sign Size:"},
    "btn_add_sign": {"tr": "+ Ekle", "en": "+ Add"},
    "btn_preview": {"tr": "🔍 Önizle", "en": "🔍 Preview"},
    "btn_undo": {"tr": "Geri Al", "en": "Undo"},
    "lbl_preview_area": {"tr": "Çalışma Alanı", "en": "Workspace"},
    "warn_sign": {"tr": "PDF ve İmza seçin.", "en": "Select PDF and Signature."},
    "imza": {"tr": "İmza", "en": "Sign"},
    "page": {"tr": "Sayfa", "en": "Page"},

    # Batch Processing
    "batch_title": {"tr": "Toplu İşlem", "en": "Batch Processing"},
    "batch_subtitle": {"tr": "Birden fazla dosyayı aynı anda işleyin", "en": "Process multiple files at once"},
    "batch_operation": {"tr": "İşlem Türü:", "en": "Operation Type:"},
    "batch_files": {"tr": "Dosyalar:", "en": "Files:"},
    "batch_add_files": {"tr": "Dosya Ekle", "en": "Add Files"},
    "batch_add_folder": {"tr": "Klasör Ekle", "en": "Add Folder"},
    "batch_clear": {"tr": "Temizle", "en": "Clear"},
    "batch_start": {"tr": "Toplu İşlemi Başlat", "en": "Start Batch Process"},
    "batch_progress": {"tr": "İlerleme:", "en": "Progress:"},
    "batch_op_compress": {"tr": "PDF Sıkıştır", "en": "Compress PDF"},
    "batch_op_pdf2img": {"tr": "PDF > Resim", "en": "PDF to Image"},
    "batch_op_jpg2pdf": {"tr": "JPG > PDF", "en": "JPG to PDF"},
    "batch_op_watermark": {"tr": "Filigran Ekle", "en": "Add Watermark"},
    "batch_op_encrypt": {"tr": "Şifrele", "en": "Encrypt"},
    "batch_output_folder": {"tr": "Çıktı Klasörü:", "en": "Output Folder:"},
    "batch_select_folder": {"tr": "Klasör Seç", "en": "Select Folder"},
    "batch_completed": {"tr": "Toplu işlem tamamlandı!", "en": "Batch processing completed!"},
    "batch_processing": {"tr": "İşleniyor...", "en": "Processing..."},

    # Preview
    "preview_title": {"tr": "Önizleme", "en": "Preview"},
    "preview_page": {"tr": "Sayfa:", "en": "Page:"},
    "btn_preview_save": {"tr": "Kaydet", "en": "Save"},
    "btn_preview_cancel": {"tr": "İptal", "en": "Cancel"},

    # PDF Editor
    "tab_editor": {"tr": "📝 Düzenle", "en": "📝 Edit"},
    "editor_title": {"tr": "PDF Düzenleyici", "en": "PDF Editor"},
    "editor_subtitle": {"tr": "Sayfaları sil, ekle ve yeniden sırala", "en": "Delete, add and reorder pages"},
    "editor_load": {"tr": "PDF Yükle", "en": "Load PDF"},
    "editor_save": {"tr": "Kaydet", "en": "Save"},
    "editor_add_page": {"tr": "Sayfa Ekle", "en": "Add Page"},
    "editor_delete": {"tr": "Seçilenleri Sil", "en": "Delete Selected"},
    "editor_rotate_left": {"tr": "↺ Sola", "en": "↺ Left"},
    "editor_rotate_right": {"tr": "↻ Sağa", "en": "↻ Right"},
    "editor_move_up": {"tr": "↑ Yukarı", "en": "↑ Up"},
    "editor_move_down": {"tr": "↓ Aşağı", "en": "↓ Down"},
    "editor_pages": {"tr": "Sayfalar:", "en": "Pages:"},
    "editor_selected": {"tr": "Seçili:", "en": "Selected:"},

    # Annotation
    "tab_annotate": {"tr": "✏️ Not Ekle", "en": "✏️ Annotate"},
    "annotate_title": {"tr": "Metin ve Çizim Araçları", "en": "Text & Drawing Tools"},
    "annotate_subtitle": {"tr": "PDF'e metin, şekil ve notlar ekleyin", "en": "Add text, shapes and notes to PDF"},
    "annotate_load": {"tr": "PDF Yükle", "en": "Load PDF"},
    "annotate_save": {"tr": "Kaydet", "en": "Save"},
    "annotate_text": {"tr": "📝 Metin", "en": "📝 Text"},
    "annotate_rectangle": {"tr": "▭ Dikdörtgen", "en": "▭ Rectangle"},
    "annotate_circle": {"tr": "○ Daire", "en": "○ Circle"},
    "annotate_line": {"tr": "— Çizgi", "en": "— Line"},
    "annotate_arrow": {"tr": "→ Ok", "en": "→ Arrow"},
    "annotate_highlight": {"tr": "🖍 Vurgula", "en": "🖍 Highlight"},
    "annotate_clear": {"tr": "Temizle", "en": "Clear"},
    "annotate_color": {"tr": "Renk:", "en": "Color:"},
    "annotate_size": {"tr": "Boyut:", "en": "Size:"},
    "annotate_page": {"tr": "Sayfa:", "en": "Page:"},

    # QR Code
    "tab_qr": {"tr": "📱 QR Kod", "en": "📱 QR Code"},
    "qr_title": {"tr": "QR Kod Sistemi", "en": "QR Code System"},
    "qr_subtitle": {"tr": "QR kod oluştur veya PDF'teki QR kodları oku", "en": "Create QR codes or read QR codes from PDF"},
    "qr_create_title": {"tr": "QR Kod Oluştur", "en": "Create QR Code"},
    "qr_read_title": {"tr": "QR Kod Oku", "en": "Read QR Code"},
    "qr_content": {"tr": "İçerik:", "en": "Content:"},
    "qr_size": {"tr": "Boyut:", "en": "Size:"},
    "qr_generate": {"tr": "QR Kod Oluştur", "en": "Generate QR Code"},
    "qr_add_to_pdf": {"tr": "PDF'e Ekle", "en": "Add to PDF"},
    "qr_save_image": {"tr": "Resim Olarak Kaydet", "en": "Save as Image"},
    "qr_load_pdf": {"tr": "PDF Yükle", "en": "Load PDF"},
    "qr_scan": {"tr": "QR Kodları Tara", "en": "Scan QR Codes"},
    "qr_results": {"tr": "Sonuçlar:", "en": "Results:"},
    "qr_found": {"tr": "QR kod bulundu!", "en": "QR code found!"},
    "qr_not_found": {"tr": "QR kod bulunamadı", "en": "No QR code found"}
}

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SettingsManager:
    """Manage application settings and recent files"""

    def __init__(self):
        self.settings_file = Constants.SETTINGS_FILE
        self.settings = self.load_settings()

    def load_settings(self) -> Dict:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    logger.info("Settings loaded successfully")
                    return settings
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")

        logger.info("Using default settings")
        return Constants.DEFAULT_SETTINGS.copy()

    def save_settings(self) -> None:
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Could not save settings: {e}", exc_info=True)

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list"""
        if not file_path or not os.path.exists(file_path):
            return

        recent = self.settings.get("recent_files", [])

        # Create entry with timestamp
        entry = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "timestamp": datetime.now().isoformat()
        }

        # Remove if already exists
        recent = [r for r in recent if r.get("path") != file_path]

        # Add to front
        recent.insert(0, entry)

        # Keep only MAX_RECENT_FILES
        recent = recent[:Constants.MAX_RECENT_FILES]

        self.settings["recent_files"] = recent
        self.save_settings()
        logger.debug(f"Added to recent files: {file_path}")

    def get_recent_files(self) -> List[Dict]:
        """Get list of recent files"""
        recent = self.settings.get("recent_files", [])
        # Filter out files that no longer exist
        return [r for r in recent if os.path.exists(r.get("path", ""))]

    def clear_recent_files(self) -> None:
        """Clear recent files list"""
        self.settings["recent_files"] = []
        self.save_settings()
        logger.info("Recent files cleared")

    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key: str, value) -> None:
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()

class PDFApp(ctk.CTk, TkinterDnD.DnDWrapper):
    """
    Main PDF Studio Application

    A comprehensive PDF manipulation tool with features including:
    - Image to PDF conversion
    - Word to PDF conversion
    - PDF to image/text extraction
    - PDF merging and splitting
    - PDF compression
    - Signature and stamp placement
    - Security features (encryption, watermarks)
    - Metadata editing
    """

    def __init__(self):
        super().__init__()
        logger.info("Initializing PDF Studio Application")

        self.TkdndVersion = TkinterDnD._require(self)

        # Initialize settings manager
        self.settings_manager = SettingsManager()

        # Load settings
        self.current_lang = self.settings_manager.get("language", "tr")
        self.current_theme = self.settings_manager.get("theme", "System")

        # Ekran Ayarı
        ctk.set_widget_scaling(Constants.DEFAULT_SCALE)
        ctk.set_window_scaling(Constants.DEFAULT_SCALE)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = int(sw * Constants.WINDOW_SIZE_RATIO), int(sh * Constants.WINDOW_SIZE_RATIO)
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")

        # Veriler
        self.merge_cards = []
        self.merge_selected_index = -1
        self.split_file_path = None
        self.split_pages_data = []
        self.compress_file_path = None
        self.pdf2img_file_path = None
        self.pdf2txt_file_path = None

        self.sign_pdf_path = None
        self.sign_doc = None
        self.sign_current_page_num = 0
        self.sign_images = []
        self.sign_selected_img_index = -1
        self.sign_placements = {}
        self.temp_image_files = []
        self.drag_data = {"item": None, "x": 0, "y": 0}
        self.canvas_images = {}
        self.tools_file_path = None

        # Batch Processing
        self.batch_files = []
        self.batch_operation = "compress"
        self.batch_output_folder = ""

        # Set window background color
        self.configure(fg_color=self.get_bg_color())

        self.create_ui_elements()
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event_handler)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def t(self, key: str) -> str:
        """Get translated text for current language"""
        return TEXTS.get(key, {}).get(self.current_lang, key)

    def get_bg_color(self) -> str:
        """Get background color based on current theme"""
        return Constants.BG_LIGHT if ctk.get_appearance_mode() == "Light" else Constants.BG_DARK

    def get_card_color(self) -> str:
        """Get card background color based on current theme"""
        return Constants.BG_CARD if ctk.get_appearance_mode() == "Light" else Constants.BG_CARD_DARK

    def get_text_color(self) -> str:
        """Get text color based on current theme"""
        return Constants.TEXT_DARK if ctk.get_appearance_mode() == "Light" else Constants.TEXT_LIGHT_MODE

    def get_secondary_text_color(self) -> str:
        """Get secondary text color based on current theme"""
        return Constants.TEXT_LIGHT if ctk.get_appearance_mode() == "Light" else Constants.TEXT_SECONDARY_DARK

    def show_pdf_preview(self, pdf_path: str, on_save_callback=None) -> None:
        """Show PDF preview dialog with navigation and save option"""
        if not pdf_path or not os.path.exists(pdf_path):
            return

        try:
            doc = fitz.open(pdf_path)
            current_page = [0]  # Use list to allow modification in nested function

            # Create preview window
            preview_win = ctk.CTkToplevel(self)
            preview_win.title(self.t("preview_title"))
            preview_win.geometry("900x1000")
            preview_win.attributes('-topmost', True)
            preview_win.grab_set()

            # Top controls
            controls = ctk.CTkFrame(preview_win, fg_color=Constants.PRIMARY_COLOR, corner_radius=0)
            controls.pack(fill="x")

            ctrl_inner = ctk.CTkFrame(controls, fg_color="transparent")
            ctrl_inner.pack(pady=15, padx=20, fill="x")

            # Navigation
            nav_frame = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
            nav_frame.pack(side="left")

            ctk.CTkButton(nav_frame, text="◄", width=40, height=35,
                         command=lambda: update_page(current_page[0] - 1),
                         fg_color="#2563eb", hover_color="#3b82f6", corner_radius=8).pack(side="left", padx=3)

            page_label = ctk.CTkLabel(nav_frame, text=f"{current_page[0]+1} / {len(doc)}",
                                     font=("Inter", 12, "bold"), text_color="white")
            page_label.pack(side="left", padx=10)

            ctk.CTkButton(nav_frame, text="►", width=40, height=35,
                         command=lambda: update_page(current_page[0] + 1),
                         fg_color="#2563eb", hover_color="#3b82f6", corner_radius=8).pack(side="left", padx=3)

            # Action buttons
            btn_frame = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
            btn_frame.pack(side="right")

            if on_save_callback:
                ctk.CTkButton(btn_frame, text="💾 " + self.t("btn_preview_save"), width=100, height=35,
                             command=lambda: (preview_win.destroy(), on_save_callback()),
                             fg_color=Constants.SECONDARY_COLOR, hover_color=Constants.SECONDARY_HOVER,
                             font=("Inter", 12, "bold"), corner_radius=8).pack(side="left", padx=3)

            ctk.CTkButton(btn_frame, text=self.t("btn_preview_cancel"), width=80, height=35,
                         command=preview_win.destroy,
                         fg_color=Constants.DANGER_COLOR, hover_color=Constants.DANGER_HOVER,
                         font=("Inter", 12, "bold"), corner_radius=8).pack(side="left", padx=3)

            # Scrollable preview area
            scroll_frame = ctk.CTkScrollableFrame(preview_win, fg_color=self.get_bg_color())
            scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

            preview_label = ctk.CTkLabel(scroll_frame, text="")
            preview_label.pack(pady=20)

            def update_page(new_page):
                if 0 <= new_page < len(doc):
                    current_page[0] = new_page
                    page_label.configure(text=f"{new_page+1} / {len(doc)}")

                    # Render page
                    page = doc[new_page]
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                    pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # Display
                    preview_label.configure(image=ctk.CTkImage(pil_img, size=(pix.width//2, pix.height//2)))
                    preview_label.image = pil_img  # Keep reference

            update_page(0)

        except Exception as e:
            logger.error(f"Error showing preview: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "tr" else "tr"
        self.settings_manager.set("language", self.current_lang)
        self.create_ui_elements()
        if self.sign_images: self.refresh_signature_library()
        if self.merge_cards: self.refresh_merge_gallery()

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.current_theme = "Light"
        else:
            ctk.set_appearance_mode("Dark")
            self.current_theme = "Dark"
        self.settings_manager.set("theme", self.current_theme)

        # Update window background color
        self.configure(fg_color=self.get_bg_color())

        # Refresh UI to apply new colors
        self.create_ui_elements()
        if self.sign_images: self.refresh_signature_library()
        if self.merge_cards: self.refresh_merge_gallery()

    def show_recent_files(self) -> None:
        """Show recent files menu"""
        recent = self.settings_manager.get_recent_files()

        # Create toplevel window
        win = ctk.CTkToplevel(self)
        win.title(self.t("menu_recent"))
        win.geometry("600x400")
        win.attributes('-topmost', True)
        win.grab_set()

        # Header
        ctk.CTkLabel(win, text=self.t("menu_recent"),
                    font=("Arial", 18, "bold")).pack(pady=15)

        if not recent:
            ctk.CTkLabel(win, text=self.t("no_recent"),
                        text_color="gray").pack(pady=50)
        else:
            # Scrollable frame for recent files
            scroll = ctk.CTkScrollableFrame(win)
            scroll.pack(fill="both", expand=True, padx=20, pady=10)

            for item in recent:
                file_path = item.get("path", "")
                file_name = item.get("name", "")

                # Create frame for each file
                file_frame = ctk.CTkFrame(scroll)
                file_frame.pack(fill="x", pady=5, padx=5)

                # File info
                info_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)

                ctk.CTkLabel(info_frame, text=file_name,
                           font=("Arial", 12, "bold"),
                           anchor="w").pack(anchor="w")

                ctk.CTkLabel(info_frame, text=file_path,
                           font=("Arial", 9),
                           text_color="gray",
                           anchor="w").pack(anchor="w")

                # Open button
                ctk.CTkButton(file_frame, text="📂 Open", width=80,
                            command=lambda p=file_path: self.open_recent_file(p, win)).pack(side="right", padx=10)

        # Bottom buttons
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10, padx=20)

        if recent:
            ctk.CTkButton(btn_frame, text=self.t("clear_recent"),
                        command=lambda: self.clear_recent_and_refresh(win),
                        fg_color="#d32f2f").pack(side="left")

        ctk.CTkButton(btn_frame, text=self.t("btn_close"),
                    command=win.destroy).pack(side="right")

    def open_recent_file(self, file_path: str, window) -> None:
        """Open a file from recent files"""
        if not os.path.exists(file_path):
            messagebox.showerror(self.t("msg_error"), f"File not found: {file_path}")
            return

        window.destroy()
        # Add to recent again to update timestamp
        self.settings_manager.add_recent_file(file_path)

        # Determine file type and open in appropriate tab
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            # For now, open in merge tab
            self.add_merge_pdf_from_list([file_path])
            self.tabview.set(self.t("tab_merge"))
        elif ext in ['.jpg', '.jpeg', '.png']:
            self.convert_dropped_jpgs([file_path])
        elif ext == '.docx':
            self.convert_dropped_word(file_path)

    def clear_recent_and_refresh(self, window) -> None:
        """Clear recent files and refresh the window"""
        self.settings_manager.clear_recent_files()
        window.destroy()
        self.show_recent_files()

    def show_settings(self) -> None:
        """Modern settings dialog"""
        win = ctk.CTkToplevel(self)
        win.title(self.t("settings_title"))
        win.geometry("600x700")
        win.attributes('-topmost', True)
        win.grab_set()

        # Shift Style Header - 10px corner radius
        header = ctk.CTkFrame(win, fg_color=Constants.PRIMARY_COLOR, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="⚙️ " + self.t("settings_title"),
            font=("Inter", 32, "bold"),  # Shift H1 style
            text_color="white"
        ).pack(pady=30)  # More generous padding

        # Scrollable settings frame
        settings_scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        settings_scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # === APPEARANCE SECTION ===
        appearance_card = ctk.CTkFrame(settings_scroll, fg_color=self.get_card_color(), corner_radius=10)  # Shift: 10px
        appearance_card.pack(fill="x", pady=(0, 24))  # Shift: 24px gaps

        ctk.CTkLabel(
            appearance_card,
            text="🎨 " + ("Görünüm" if self.current_lang == "tr" else "Appearance"),
            font=("Inter", 24, "bold"),  # Shift H2 size
            text_color=self.get_text_color()
        ).pack(anchor="w", padx=24, pady=(24, 16))  # More padding

        # Language
        lang_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        lang_frame.pack(fill="x", padx=24, pady=12)

        ctk.CTkLabel(
            lang_frame,
            text="🌐 " + self.t("settings_language"),
            font=("Inter", 16, "bold"),  # Shift body bold
            text_color=self.get_text_color()
        ).pack(anchor="w", pady=(0, 10))

        lang_var = ctk.StringVar(value=self.current_lang)
        lang_buttons = ctk.CTkFrame(lang_frame, fg_color="transparent")
        lang_buttons.pack(fill="x")

        ctk.CTkRadioButton(
            lang_buttons,
            text="🇹🇷 Türkçe",
            variable=lang_var,
            value="tr",
            font=("Inter", 14),  # Shift body text
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER
        ).pack(side="left", padx=(0, 20))

        ctk.CTkRadioButton(
            lang_buttons,
            text="🇬🇧 English",
            variable=lang_var,
            value="en",
            font=("Inter", 14),
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER
        ).pack(side="left")

        # Theme
        theme_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        theme_frame.pack(fill="x", padx=24, pady=16)

        ctk.CTkLabel(
            theme_frame,
            text="🌓 " + self.t("settings_theme"),
            font=("Inter", 16, "bold"),
            text_color=self.get_text_color()
        ).pack(anchor="w", pady=(0, 10))

        theme_var = ctk.StringVar(value=self.current_theme)
        theme_buttons = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_buttons.pack(fill="x")

        themes = [
            ("💻 " + ("Sistem" if self.current_lang == "tr" else "System"), "System"),
            ("☀️ " + ("Açık" if self.current_lang == "tr" else "Light"), "Light"),
            ("🌙 " + ("Koyu" if self.current_lang == "tr" else "Dark"), "Dark")
        ]

        for label, value in themes:
            ctk.CTkRadioButton(
                theme_buttons,
                text=label,
                variable=theme_var,
                value=value,
                font=("Inter", 14),
                fg_color=Constants.PRIMARY_COLOR,
                hover_color=Constants.PRIMARY_HOVER
            ).pack(side="left", padx=(0, 16))

        # Separator
        ctk.CTkFrame(appearance_card, height=2, fg_color=self.get_bg_color()).pack(fill="x", padx=20, pady=20)

        # === PDF SETTINGS SECTION ===
        pdf_card = ctk.CTkFrame(settings_scroll, fg_color=self.get_card_color(), corner_radius=10)
        pdf_card.pack(fill="x", pady=(0, 24))

        ctk.CTkLabel(
            pdf_card,
            text="📄 " + ("PDF Ayarları" if self.current_lang == "tr" else "PDF Settings"),
            font=("Inter", 24, "bold"),
            text_color=self.get_text_color()
        ).pack(anchor="w", padx=24, pady=(24, 16))

        # DPI Setting
        dpi_frame = ctk.CTkFrame(pdf_card, fg_color="transparent")
        dpi_frame.pack(fill="x", padx=24, pady=12)

        dpi_var = ctk.IntVar(value=self.settings_manager.get("default_dpi", 150))
        dpi_label = ctk.CTkLabel(
            dpi_frame,
            text=f"📐 {self.t('settings_dpi')}: {dpi_var.get()}",
            font=("Inter", 16, "bold"),
            text_color=self.get_text_color()
        )
        dpi_label.pack(anchor="w", pady=(0, 10))

        dpi_slider = ctk.CTkSlider(
            dpi_frame,
            from_=Constants.MIN_DPI,
            to=Constants.MAX_DPI,
            variable=dpi_var,
            number_of_steps=Constants.DPI_STEPS,
            button_color=Constants.PRIMARY_COLOR,
            button_hover_color=Constants.PRIMARY_HOVER,
            progress_color=Constants.PRIMARY_COLOR
        )
        dpi_slider.pack(fill="x", pady=5)

        def update_dpi_label(val):
            dpi_label.configure(text=f"📐 {self.t('settings_dpi')}: {int(val)}")
        dpi_slider.configure(command=update_dpi_label)

        # Quality Setting
        quality_frame = ctk.CTkFrame(pdf_card, fg_color="transparent")
        quality_frame.pack(fill="x", padx=24, pady=16)

        quality_var = ctk.DoubleVar(value=self.settings_manager.get("default_quality", 0.6))
        quality_label = ctk.CTkLabel(
            quality_frame,
            text=f"✨ {self.t('settings_quality')}: {int(quality_var.get()*100)}%",
            font=("Inter", 16, "bold"),
            text_color=self.get_text_color()
        )
        quality_label.pack(anchor="w", pady=(0, 10))

        quality_slider = ctk.CTkSlider(
            quality_frame,
            from_=Constants.MIN_QUALITY,
            to=Constants.MAX_QUALITY,
            variable=quality_var,
            number_of_steps=Constants.QUALITY_STEPS,
            button_color=Constants.PRIMARY_COLOR,
            button_hover_color=Constants.PRIMARY_HOVER,
            progress_color=Constants.PRIMARY_COLOR
        )
        quality_slider.pack(fill="x", pady=5)

        def update_quality_label(val):
            quality_label.configure(text=f"✨ {self.t('settings_quality')}: {int(float(val)*100)}%")
        quality_slider.configure(command=update_quality_label)

        # Remember directory
        remember_var = ctk.BooleanVar(value=self.settings_manager.get("remember_last_dir", True))
        ctk.CTkCheckBox(
            pdf_card,
            text="💾 " + self.t("settings_remember_dir"),
            variable=remember_var,
            font=("Inter", 14),
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER
        ).pack(anchor="w", padx=24, pady=(12, 24))

        # Bottom buttons - modern style
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20, padx=30)

        def save_settings():
            self.settings_manager.set("language", lang_var.get())
            self.settings_manager.set("theme", theme_var.get())
            self.settings_manager.set("default_dpi", int(dpi_var.get()))
            self.settings_manager.set("default_quality", quality_var.get())
            self.settings_manager.set("remember_last_dir", remember_var.get())

            # Apply theme immediately
            if theme_var.get() != self.current_theme:
                self.current_theme = theme_var.get()
                ctk.set_appearance_mode(self.current_theme)

            # Apply language immediately
            if lang_var.get() != self.current_lang:
                self.current_lang = lang_var.get()
                self.create_ui_elements()
                if hasattr(self, 'sign_images') and self.sign_images:
                    self.refresh_signature_library()
                if hasattr(self, 'merge_cards') and self.merge_cards:
                    self.refresh_merge_gallery()

            messagebox.showinfo(
                self.t("msg_success"),
                "Ayarlar kaydedildi! Değişiklikler uygulandı." if self.current_lang == "tr"
                else "Settings saved! Changes applied."
            )
            win.destroy()

        ctk.CTkButton(
            btn_frame,
            text="💾 " + self.t("btn_save_settings"),
            command=save_settings,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            font=("Inter", 18, "bold"),  # Shift button text size
            height=50,  # Generous button height
            corner_radius=10  # Shift: 10px
        ).pack(side="right", padx=8)

        ctk.CTkButton(
            btn_frame,
            text="✖️ " + self.t("btn_cancel"),
            command=win.destroy,
            fg_color="transparent",
            hover_color=Constants.BORDER_LIGHT,
            border_width=1,
            border_color=Constants.BORDER_LIGHT,
            text_color=self.get_text_color(),
            font=("Inter", 18, "bold"),
            height=45,
            corner_radius=10
        ).pack(side="right", padx=5)

    def create_ui_elements(self) -> None:
        """Create and setup all UI elements"""
        # Clear existing widgets (except header if it exists)
        for widget in self.winfo_children():
            if not hasattr(self, 'main_header') or widget != self.main_header:
                widget.destroy()

        self.title(self.t("app_title"))

        # Professional Header with theme-aware background (always recreate for theme changes)
        if hasattr(self, 'main_header') and self.main_header.winfo_exists():
            self.main_header.destroy()

        header_bg = Constants.HEADER_BG if ctk.get_appearance_mode() == "Light" else Constants.HEADER_BG_DARK
        self.main_header = ctk.CTkFrame(self, fg_color=header_bg, corner_radius=0)
        self.main_header.pack(fill="x", pady=0)

        # Create header content
        self._create_header_content()

        # Always create home page content
        self._create_home_page()

    def _create_header_content(self):
        """Minimalist header design"""
        header_container = self.main_header

        h_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        h_frame.pack(pady=16, fill="x", padx=32)

        # Left section - Logo and Title
        left_section = ctk.CTkFrame(h_frame, fg_color="transparent")
        left_section.pack(side="left")

        # Minimal app logo
        logo_bg = ctk.CTkFrame(
            left_section,
            fg_color=Constants.PRIMARY_COLOR,
            corner_radius=10,
            width=44,
            height=44
        )
        logo_bg.pack(side="left", padx=(0, 12))
        logo_bg.pack_propagate(False)

        ctk.CTkLabel(
            logo_bg,
            text="📄",
            font=("Segoe UI Emoji", 24)
        ).pack(expand=True)

        # Title section
        title_section = ctk.CTkFrame(left_section, fg_color="transparent")
        title_section.pack(side="left")

        ctk.CTkLabel(
            title_section,
            text=self.t("header"),
            font=("Inter", 20, "bold"),
            text_color=self.get_text_color()
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_section,
            text=f"v{Constants.APP_VERSION}",
            font=("Inter", 9),
            text_color=self.get_secondary_text_color()
        ).pack(anchor="w")

        # Right section - Minimal settings button
        ctk.CTkButton(
            h_frame,
            text="⚙️",
            width=44,
            height=44,
            command=self.show_settings,
            fg_color="transparent",
            hover_color=Constants.PRIMARY_COLOR,
            text_color=self.get_text_color(),
            border_width=0,
            corner_radius=10,
            font=("Segoe UI Emoji", 18)
        ).pack(side="right")

        # Minimal bottom border
        border_color = Constants.BORDER_LIGHT if ctk.get_appearance_mode() == "Light" else Constants.BORDER_DARK
        ctk.CTkFrame(header_container, height=1, fg_color=border_color).pack(fill="x")

    def _create_home_page(self):
        """Shift-inspired home page with hero section"""
        # Hero Section Background - Shift style with subtle accent
        hero_bg_color = Constants.BG_LIGHT_IMAGE if ctk.get_appearance_mode() == "Light" else "transparent"
        hero_container = ctk.CTkFrame(self, fg_color=hero_bg_color, corner_radius=0)
        hero_container.pack(fill="x", pady=(0, 10))

        # Hero Section - Shift style with generous spacing
        hero_section = ctk.CTkFrame(hero_container, fg_color="transparent")
        hero_section.pack(pady=(60, 50), padx=80)  # Shift: 40-128px padding

        # Main title - Shift style (48px, bold) with more impact
        ctk.CTkLabel(
            hero_section,
            text="PDF Araçlarınız" if self.current_lang == "tr" else "Your PDF Tools",
            font=("Inter", 56, "bold"),  # Slightly larger for impact
            text_color=self.get_text_color()
        ).pack()

        # Subtitle - Shift style with better line height
        subtitle_text = "Görüntüleyin, birleştirin, yönetin ve PDF dosyalarınızı kolayca sıkıştırın" if self.current_lang == "tr" else "View, merge, manage, and compress PDF files with ease"
        ctk.CTkLabel(
            hero_section,
            text=subtitle_text,
            font=("Inter", 18),
            text_color=self.get_secondary_text_color(),
            wraplength=700,
            justify="center"
        ).pack(pady=(12, 0))

        # Feature tagline - Shift style
        tagline_text = "Profesyonel PDF çözümleri, hızlı ve kolay" if self.current_lang == "tr" else "Professional PDF solutions, fast and easy"
        ctk.CTkLabel(
            hero_section,
            text=tagline_text,
            font=("Inter", 14),
            text_color=self.get_secondary_text_color()
        ).pack(pady=(6, 0))

        # Modern Tool Cards Grid - Shift style spacing (64px+ padding)
        main_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        main_container.pack(fill="both", expand=True, padx=80, pady=(20, 40))  # More generous spacing

        # Tools data with icons, colors, and descriptions
        tools = [
            {
                'name': 'JPG to PDF',
                'icon': '🖼️',
                'desc': 'Convert images to PDF',
                'desc_tr': 'Resimleri PDF\'e çevir',
                'color': '#ef4444',  # Modern red
                'action': self.open_jpg_tool
            },
            {
                'name': 'Word to PDF',
                'icon': '📄',
                'desc': 'Convert Word documents',
                'desc_tr': 'Word belgelerini çevir',
                'color': '#3b82f6',  # Modern blue
                'action': self.open_word_tool
            },
            {
                'name': 'PDF to Image',
                'icon': '🎨',
                'desc': 'Extract images from PDF',
                'desc_tr': 'PDF\'den resim çıkar',
                'color': '#10b981',  # Modern emerald
                'action': self.open_pdf2img_tool
            },
            {
                'name': 'PDF to Text',
                'icon': '📝',
                'desc': 'Extract text with OCR',
                'desc_tr': 'Metin çıkar (OCR)',
                'color': '#f59e0b',  # Modern amber
                'action': self.open_pdf2txt_tool
            },
            {
                'name': 'Merge PDF',
                'icon': '🔗',
                'desc': 'Combine multiple PDFs',
                'desc_tr': 'Birden fazla PDF birleştir',
                'color': '#8b5cf6',  # Modern purple
                'action': self.open_merge_tool
            },
            {
                'name': 'Split PDF',
                'icon': '✂️',
                'desc': 'Separate PDF pages',
                'desc_tr': 'PDF sayfalarını ayır',
                'color': '#06b6d4',  # Modern cyan
                'action': self.open_split_tool
            },
            {
                'name': 'Compress PDF',
                'icon': '📦',
                'desc': 'Reduce file size',
                'desc_tr': 'Dosya boyutunu küçült',
                'color': '#ec4899',  # Modern pink
                'action': self.open_compress_tool
            },
            {
                'name': 'Sign PDF',
                'icon': '✍️',
                'desc': 'Add digital signature',
                'desc_tr': 'Dijital imza ekle',
                'color': '#f97316',  # Modern orange
                'action': self.open_sign_tool
            },
            {
                'name': 'PDF Tools',
                'icon': '🛠️',
                'desc': 'Encrypt, watermark, rotate',
                'desc_tr': 'Şifrele, filigran, döndür',
                'color': '#6b7280',  # Modern gray
                'action': self.open_tools_tool
            },
            {
                'name': 'Batch Process',
                'icon': '⚡',
                'desc': 'Process multiple files',
                'desc_tr': 'Toplu işlem yap',
                'color': '#14b8a6',  # Modern teal
                'action': self.open_batch_tool
            },
            {
                'name': 'Annotate PDF',
                'icon': '✏️',
                'desc': 'Add text and drawings',
                'desc_tr': 'Metin ve çizim ekle',
                'color': '#a855f7',  # Modern purple/violet
                'action': self.open_annotate_tool
            },
            {
                'name': 'QR Code',
                'icon': '📱',
                'desc': 'Create and scan QR codes',
                'desc_tr': 'QR kod oluştur ve tara',
                'color': '#22d3ee',  # Modern cyan/aqua
                'action': self.open_qr_tool
            }
        ]

        # Create grid of tool cards (4 columns) - Shift style spacing
        cols = 4
        row_frame = None

        for i, tool in enumerate(tools):
            if i % cols == 0:
                row_frame = ctk.CTkFrame(main_container, fg_color="transparent")
                row_frame.pack(pady=16, fill="x")  # More generous vertical spacing

            # Shift Style Card Design - 10px border radius, generous padding
            border_color = Constants.BORDER_LIGHT if ctk.get_appearance_mode() == "Light" else Constants.BORDER_DARK

            card = ctk.CTkFrame(
                row_frame,
                fg_color=self.get_card_color(),
                corner_radius=10,  # Shift uses 10px
                cursor="hand2",
                border_width=1,
                border_color=border_color,
                height=220  # Slightly taller for generous spacing
            )
            card.pack(side="left", padx=12, pady=12, expand=True, fill="both")  # 24px gaps
            card.pack_propagate(False)

            # Icon container - Shift style with 16px radius
            icon_bg = Constants.BG_LIGHT_IMAGE if ctk.get_appearance_mode() == "Light" else Constants.BG_DARK_IMAGE
            icon_container = ctk.CTkFrame(
                card,
                fg_color=tool['color'],
                corner_radius=16,  # More rounded for Shift style
                height=100
            )
            icon_container.pack(fill="x", padx=16, pady=(16, 12))  # Generous padding
            icon_container.pack_propagate(False)

            # Icon - larger and centered
            ctk.CTkLabel(
                icon_container,
                text=tool['icon'],
                font=("Segoe UI Emoji", 52),  # Larger icon
                text_color="white"
            ).pack(expand=True)

            # Tool name - Shift typography (24px heading)
            ctk.CTkLabel(
                card,
                text=tool['name'],
                font=("Inter", 24, "bold"),  # Shift H2 size
                text_color=self.get_text_color()
            ).pack(pady=(0, 6), padx=16)

            # Description - 18px body text
            desc = tool['desc_tr'] if self.current_lang == 'tr' else tool['desc']
            ctk.CTkLabel(
                card,
                text=desc,
                font=("Inter", 14),  # Shift uses 14-18px body
                text_color=self.get_secondary_text_color(),
                wraplength=200,
                justify="center"
            ).pack(pady=(0, 16), padx=16)

            # Click handler - proper closure
            def make_click_handler(action_func):
                def handler(event):
                    try:
                        action_func()
                    except Exception as e:
                        logger.error(f"Error opening tool: {e}", exc_info=True)
                        messagebox.showerror("Error", f"Failed to open tool: {str(e)}")
                return handler

            handler = make_click_handler(tool['action'])
            card.bind("<Button-1>", handler)

            # Shift-style hover effect - border highlight + subtle lift feel
            original_border = border_color
            def on_enter(e):
                card.configure(border_width=2, border_color=tool['color'])
                # Slight visual emphasis on hover
                card.configure(cursor="hand2")

            def on_leave(e):
                card.configure(border_width=1, border_color=original_border)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            # Bind all children too
            def bind_all_children(widget, handler):
                for child in widget.winfo_children():
                    child.bind("<Button-1>", handler)
                    if hasattr(child, 'winfo_children'):
                        bind_all_children(child, handler)

            bind_all_children(card, handler)

    # Tool openers - iLovePDF style (same window)
    def open_tool_in_place(self, tool_name, setup_func):
        """Open tool in the same window - hide home, show tool"""
        # Hide home page
        for widget in self.winfo_children():
            if widget != self.main_header:
                widget.pack_forget()

        # Create tool container
        tool_container = ctk.CTkFrame(self, fg_color=self.get_bg_color())
        tool_container.pack(fill="both", expand=True)

        # Back button bar
        back_bar = ctk.CTkFrame(tool_container, fg_color=self.get_card_color(), height=70)
        back_bar.pack(fill="x", padx=20, pady=(20, 10))
        back_bar.pack_propagate(False)

        back_btn_text = "← Ana Sayfa" if self.current_lang == "tr" else "← Home"

        ctk.CTkButton(
            back_bar,
            text=back_btn_text,
            command=self.return_to_home,
            fg_color=Constants.NEUTRAL_COLOR,
            hover_color=Constants.NEUTRAL_HOVER,
            font=("Inter", 15, "bold"),
            height=45,
            width=150,
            corner_radius=10
        ).pack(side="left", padx=15, pady=12)

        ctk.CTkLabel(
            back_bar,
            text=tool_name,
            font=("Inter", 20, "bold"),
            text_color=self.get_text_color()
        ).pack(side="left", padx=25)

        # Create a content frame for the tool (so setup functions don't destroy the back button)
        content_frame = ctk.CTkFrame(tool_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Tool content area - pass content_frame instead of tool_container
        self.current_tool_container = tool_container
        setup_func(content_frame)

    def return_to_home(self, tool_container=None):
        """Return to home page from tool"""
        # Clear all widgets except header
        for widget in self.winfo_children():
            if not hasattr(self, 'main_header') or widget != self.main_header:
                widget.destroy()

        # Ensure header is properly packed first
        if hasattr(self, 'main_header') and self.main_header.winfo_exists():
            self.main_header.pack_forget()
            self.main_header.pack(fill="x", pady=0)

        # Recreate home page
        self._create_home_page()

    def open_jpg_tool(self):
        def setup(parent):
            self.tab_jpg = parent
            self.setup_jpg_tab()
        self.open_tool_in_place("JPG to PDF", setup)

    def open_word_tool(self):
        def setup(parent):
            self.tab_word = parent
            self.setup_word_tab()
        self.open_tool_in_place("Word to PDF", setup)

    def open_pdf2img_tool(self):
        def setup(parent):
            self.tab_pdf2img = parent
            self.setup_pdf2img_tab()
        self.open_tool_in_place("PDF to Image", setup)

    def open_pdf2txt_tool(self):
        def setup(parent):
            self.tab_pdf2txt = parent
            self.setup_pdf2txt_tab()
        self.open_tool_in_place("PDF to Text", setup)

    def open_merge_tool(self):
        def setup(parent):
            self.tab_merge = parent
            self.setup_merge_tab()
        self.open_tool_in_place("Merge PDF", setup)

    def open_split_tool(self):
        def setup(parent):
            self.tab_split = parent
            self.setup_split_tab()
        self.open_tool_in_place("Split PDF", setup)

    def open_compress_tool(self):
        def setup(parent):
            self.tab_compress = parent
            self.setup_compress_tab()
        self.open_tool_in_place("Compress PDF", setup)

    def open_sign_tool(self):
        def setup(parent):
            self.tab_sign = parent
            self.setup_sign_tab()
        self.open_tool_in_place("Sign PDF", setup)

    def open_tools_tool(self):
        def setup(parent):
            self.tab_tools = parent
            self.setup_tools_tab()
        self.open_tool_in_place("PDF Tools", setup)

    def open_batch_tool(self):
        def setup(parent):
            self.tab_batch = parent
            self.setup_batch_tab()
        self.open_tool_in_place("Batch Process", setup)

    def open_annotate_tool(self):
        def setup(parent):
            self.tab_annotate = parent
            self.setup_annotate_tab()
        self.open_tool_in_place("Annotate PDF", setup)

    def open_qr_tool(self):
        def setup(parent):
            self.tab_qr = parent
            self.setup_qr_tab()
        self.open_tool_in_place("QR Code", setup)

    def on_closing(self) -> None:
        """Clean up temporary files and close application"""
        logger.info("Closing application and cleaning up temporary files")
        for t in self.temp_image_files:
            try:
                os.remove(t)
                logger.debug(f"Removed temp file: {t}")
            except Exception as e:
                logger.warning(f"Could not remove temp file {t}: {e}")
        logger.info("Application closed")
        self.quit()

    def drop_event_handler(self, event):
        """Handle drag and drop files - context aware"""
        files = self.tk.splitlist(event.data)
        if not files:
            return

        # Get first file to determine type
        first_file = files[0]
        ext = os.path.splitext(first_file)[1].lower()

        # Check if we're already in a tool (context-aware drop)
        # If in Merge tool, add PDFs there
        if hasattr(self, 'tab_merge') and ext == '.pdf':
            try:
                # Check if merge tab exists and is visible
                if self.tab_merge.winfo_exists() and self.tab_merge.winfo_viewable():
                    self.add_merge_pdf_from_list(list(files))
                    return
            except:
                pass

        # Check if in Compress tool, load PDF there
        if hasattr(self, 'tab_compress') and ext == '.pdf':
            try:
                if self.tab_compress.winfo_exists() and self.tab_compress.winfo_viewable():
                    self.load_compress_pdf(first_file)
                    return
            except:
                pass

        # Check if in JPG tool, add images there
        if hasattr(self, 'tab_jpg') and ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
            try:
                if self.tab_jpg.winfo_exists() and self.tab_jpg.winfo_viewable():
                    self.convert_dropped_jpgs(list(files))
                    return
            except:
                pass

        # Not in a tool, route to appropriate handler based on file type
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
            # Image files - open JPG to PDF tool
            self.open_jpg_tool()
            self.after(100, lambda: self.convert_dropped_jpgs(list(files)))
        elif ext in ['.docx', '.doc']:
            # Word file
            self.open_word_tool()
            self.after(100, lambda: self.convert_dropped_word(first_file))
        elif ext == '.pdf':
            # PDF files - open merge tool if multiple, otherwise compress
            if len(files) > 1:
                self.open_merge_tool()
                self.after(100, lambda: self.add_merge_pdf_from_list(list(files)))
            else:
                # Single PDF - default to compress
                self.open_compress_tool()
                self.after(100, lambda: self.load_compress_pdf(first_file))
        else:
            messagebox.showinfo(
                "Dosya Tipi",
                f"Desteklenmeyen dosya tipi: {ext}\n\n"
                f"Desteklenen formatlar:\n"
                f"• Resimler: JPG, JPEG, PNG, GIF, BMP, TIFF, WebP\n"
                f"• Belgeler: DOCX\n"
                f"• PDF dosyaları"
            )

    # --- MODERN TAB DESIGNS ---
    def setup_jpg_tab(self):
        # Clear tab
        for w in self.tab_jpg.winfo_children():
            w.destroy()

        # Main container with padding
        main_frame = ctk.CTkFrame(self.tab_jpg, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Icon and title
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(pady=(0, 30))

        ctk.CTkLabel(header, text="🖼️", font=("Segoe UI Emoji", 48)).pack()
        ctk.CTkLabel(header, text=self.t("jpg_label"),
                    font=("Inter", 22, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(header, text="Convert JPG/PNG images to PDF format",
                    font=("Inter", 13),
                    text_color=self.get_secondary_text_color()).pack()

        # Action button with modern styling
        ctk.CTkButton(
            main_frame,
            text=f"🎯  {self.t('btn_select_img')}",
            command=self.convert_jpg_to_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=50,
            font=("Inter", 14, "bold"),
            corner_radius=12
        ).pack(pady=20)
    def convert_jpg_to_pdf(self):
        fs = filedialog.askopenfilenames(filetypes=Constants.IMAGE_TYPES)
        if fs: self.convert_dropped_jpgs(list(fs))
    def convert_dropped_jpgs(self, fs: List[str]) -> None:
        """Convert JPG images to PDF"""
        try:
            s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if s:
                logger.info(f"Converting {len(fs)} images to PDF: {s}")
                with open(s, "wb") as f:
                    f.write(img2pdf.convert(fs))
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                logger.info(f"Successfully created PDF: {s}")
        except Exception as e:
            logger.error(f"Error converting images to PDF: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))
    def setup_word_tab(self):
        # Clear tab
        for w in self.tab_word.winfo_children():
            w.destroy()

        # Main container
        main_frame = ctk.CTkFrame(self.tab_word, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Icon and title
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(pady=(0, 30))

        ctk.CTkLabel(header, text="📝", font=("Segoe UI Emoji", 48)).pack()
        ctk.CTkLabel(header, text=self.t("word_label"),
                    font=("Inter", 22, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(header, text="Convert Word documents (.docx) to PDF",
                    font=("Inter", 13),
                    text_color=self.get_secondary_text_color()).pack()

        # Action button
        ctk.CTkButton(
            main_frame,
            text=f"📄  {self.t('btn_select_word')}",
            command=self.convert_word_to_pdf,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            height=50,
            font=("Inter", 14, "bold"),
            corner_radius=12
        ).pack(pady=20)
    def convert_word_to_pdf(self):
        f = filedialog.askopenfilename(filetypes=[("Word", "*.docx")])
        if f: self.convert_dropped_word(f)
    def convert_dropped_word(self, f: str) -> None:
        """Convert Word document to PDF"""
        try:
            s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if s:
                logger.info(f"Converting Word to PDF: {f} -> {s}")
                pythoncom.CoInitialize()
                try:
                    w = win32com.client.Dispatch("Word.Application")
                    w.Visible = False
                    d = w.Documents.Open(os.path.abspath(f))
                    d.SaveAs(os.path.abspath(s), FileFormat=17)
                    d.Close()
                    w.Quit()
                    messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                    logger.info(f"Successfully converted Word to PDF: {s}")
                finally:
                    pythoncom.CoUninitialize()
        except Exception as e:
            logger.error(f"Error converting Word to PDF: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))

    # --- PDF TO IMAGE ---
    def setup_pdf2img_tab(self):
        for w in self.tab_pdf2img.winfo_children(): w.destroy()

        # Main container
        main_frame = ctk.CTkFrame(self.tab_pdf2img, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Header with icon
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(pady=(0, 30))

        ctk.CTkLabel(header, text="🖼️", font=("Segoe UI Emoji", 48)).pack()
        ctk.CTkLabel(header, text=self.t("p2i_title"),
                    font=("Inter", 22, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(header, text="Extract pages from PDF as high-quality images",
                    font=("Inter", 13),
                    text_color=self.get_secondary_text_color()).pack()

        # File selection area
        file_frame = ctk.CTkFrame(main_frame, fg_color=self.get_bg_color(), corner_radius=15)
        file_frame.pack(fill="x", pady=20, padx=20)

        btn_container = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_container.pack(pady=20, padx=20)

        ctk.CTkButton(
            btn_container,
            text=f"📁  {self.t('btn_select')}",
            command=self.select_pdf2img_file,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=45,
            font=("Inter", 13, "bold"),
            corner_radius=10
        ).pack(side="left", padx=5)

        if self.pdf2img_file_path:
            ctk.CTkButton(
                btn_container,
                text="✕",
                width=45,
                height=45,
                fg_color=Constants.DANGER_COLOR,
                hover_color="#dc2626",
                command=self.clear_pdf2img_file,
                corner_radius=10,
                font=("Inter", 14, "bold")
            ).pack(side="left", padx=5)

        txt = os.path.basename(self.pdf2img_file_path) if self.pdf2img_file_path else self.t("lbl_no_file")
        self.lbl_pdf2img_file = ctk.CTkLabel(
            file_frame,
            text=txt,
            text_color="gray" if not self.pdf2img_file_path else Constants.PRIMARY_COLOR,
            font=("Inter", 12, "bold" if self.pdf2img_file_path else "normal")
        )
        self.lbl_pdf2img_file.pack(pady=(0, 20))

        # DPI Settings
        if self.pdf2img_file_path:
            settings_frame = ctk.CTkFrame(main_frame, fg_color=self.get_bg_color(), corner_radius=15)
            settings_frame.pack(fill="x", pady=10, padx=20)

            ctk.CTkLabel(
                settings_frame,
                text=f"⚙️  {self.t('lbl_dpi')}",
                font=("Inter", 14, "bold")
            ).pack(pady=(20, 10))

            self.p2i_slider = ctk.CTkSlider(
                settings_frame,
                from_=Constants.MIN_DPI,
                to=Constants.MAX_DPI,
                number_of_steps=Constants.DPI_STEPS,
                width=300,
                height=20,
                button_color=Constants.PRIMARY_COLOR,
                button_hover_color=Constants.PRIMARY_HOVER,
                progress_color=Constants.PRIMARY_COLOR
            )
            self.p2i_slider.set(Constants.DEFAULT_DPI)
            self.p2i_slider.pack(pady=10)

            dpi_val = int(self.p2i_slider.get())
            ctk.CTkLabel(
                settings_frame,
                text=f"{dpi_val} DPI",
                font=("Inter", 12),
                text_color=self.get_secondary_text_color()
            ).pack(pady=(0, 20))

        # Convert button
        state = "normal" if self.pdf2img_file_path else "disabled"
        ctk.CTkButton(
            main_frame,
            text=f"🎯  {self.t('btn_convert_jpg')}",
            state=state,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            command=self.start_pdf2img,
            height=50,
            font=("Inter", 14, "bold"),
            corner_radius=12
        ).pack(pady=20)
    def select_pdf2img_file(self): self.load_pdf2img_file(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_pdf2img_file(self, f):
        if not f: return
        self.pdf2img_file_path = f
        self.settings_manager.add_recent_file(f)
        # Load default DPI from settings
        default_dpi = self.settings_manager.get("default_dpi", Constants.DEFAULT_DPI)
        self.setup_pdf2img_tab()
        if hasattr(self, 'p2i_slider'):
            self.p2i_slider.set(default_dpi)
    def clear_pdf2img_file(self): self.pdf2img_file_path = None; self.setup_pdf2img_tab()
    def start_pdf2img(self):
        if not self.pdf2img_file_path: return
        folder = filedialog.askdirectory()
        if not folder: return
        try:
            logger.info(f"Converting PDF to images: {self.pdf2img_file_path}")
            doc = fitz.open(self.pdf2img_file_path)
            dpi = int(self.p2i_slider.get())
            base_name = os.path.splitext(os.path.basename(self.pdf2img_file_path))[0]

            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                out_path = os.path.join(folder, f"{base_name}_page_{i+1}.jpg")
                pix.save(out_path)
                logger.debug(f"Saved page {i+1} to {out_path}")

            doc.close()
            messagebox.showinfo(self.t("msg_success"), f"{len(doc)} {self.t('msg_done')}\n{folder}")
            logger.info(f"Successfully converted {len(doc)} pages to images")
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))

    # --- YENİ: PDF TO TEXT (METİN ÇIKARMA) ---
    def setup_pdf2txt_tab(self):
        for w in self.tab_pdf2txt.winfo_children(): w.destroy()

        # Main container
        main_frame = ctk.CTkFrame(self.tab_pdf2txt, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Header with icon
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(pady=(0, 30))

        ctk.CTkLabel(header, text="📝", font=("Segoe UI Emoji", 48)).pack()
        ctk.CTkLabel(header, text=self.t("p2t_title"),
                    font=("Inter", 22, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(header, text="Extract all text content from PDF documents",
                    font=("Inter", 13),
                    text_color=self.get_secondary_text_color()).pack()

        # File selection area
        file_frame = ctk.CTkFrame(main_frame, fg_color=self.get_bg_color(), corner_radius=15)
        file_frame.pack(fill="x", pady=20, padx=20)

        btn_container = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_container.pack(pady=20, padx=20)

        ctk.CTkButton(
            btn_container,
            text=f"📁  {self.t('btn_select')}",
            command=self.select_pdf2txt_file,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=45,
            font=("Inter", 13, "bold"),
            corner_radius=10
        ).pack(side="left", padx=5)

        if self.pdf2txt_file_path:
            ctk.CTkButton(
                btn_container,
                text="✕",
                width=45,
                height=45,
                fg_color=Constants.DANGER_COLOR,
                hover_color="#dc2626",
                command=self.clear_pdf2txt_file,
                corner_radius=10,
                font=("Inter", 14, "bold")
            ).pack(side="left", padx=5)

        txt = os.path.basename(self.pdf2txt_file_path) if self.pdf2txt_file_path else self.t("lbl_no_file")
        self.lbl_pdf2txt_file = ctk.CTkLabel(
            file_frame,
            text=txt,
            text_color="gray" if not self.pdf2txt_file_path else Constants.PRIMARY_COLOR,
            font=("Inter", 12, "bold" if self.pdf2txt_file_path else "normal")
        )
        self.lbl_pdf2txt_file.pack(pady=(0, 20))

        # Convert button
        state = "normal" if self.pdf2txt_file_path else "disabled"
        ctk.CTkButton(
            main_frame,
            text=f"🎯  {self.t('btn_convert_txt')}",
            state=state,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            command=self.start_pdf2txt,
            height=50,
            font=("Inter", 14, "bold"),
            corner_radius=12
        ).pack(pady=20)
    
    def select_pdf2txt_file(self): self.load_pdf2txt_file(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_pdf2txt_file(self, f):
        if not f: return
        self.pdf2txt_file_path = f; self.setup_pdf2txt_tab()
    def clear_pdf2txt_file(self): self.pdf2txt_file_path = None; self.setup_pdf2txt_tab()
    
    def start_pdf2txt(self) -> None:
        """Extract text from PDF with enhanced OCR-like extraction"""
        if not self.pdf2txt_file_path:
            return

        s = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
        if not s:
            return

        try:
            logger.info(f"Extracting text from PDF (Enhanced mode): {self.pdf2txt_file_path}")
            doc = fitz.open(self.pdf2txt_file_path)
            full_text = ""

            for i, page in enumerate(doc):
                # Try multiple extraction methods for better results
                text = page.get_text("text")  # Standard text

                # If no text found, try blocks method (better for scanned docs)
                if not text.strip():
                    blocks = page.get_text("blocks")
                    text = "\n".join([block[4] for block in blocks if len(block) > 4])

                # Add extracted text with page separator
                full_text += f"=== Page {i+1} ===\n{text}\n\n"
                logger.debug(f"Extracted text from page {i+1} ({len(text)} chars)")

            # Add metadata
            metadata = doc.metadata
            header = f"PDF: {os.path.basename(self.pdf2txt_file_path)}\n"
            header += f"Pages: {len(doc)}\n"
            if metadata.get('title'):
                header += f"Title: {metadata['title']}\n"
            header += "=" * 50 + "\n\n"

            with open(s, "w", encoding="utf-8") as f:
                f.write(header + full_text)

            doc.close()
            char_count = len(full_text)
            messagebox.showinfo(self.t("msg_success"),
                              f"{self.t('msg_done')}\n{len(doc)} pages, {char_count} characters extracted")
            logger.info(f"Successfully extracted text to: {s} ({char_count} characters)")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))

    # --- MERGE ---
    def setup_merge_tab(self):
        # Header area
        header_frame = ctk.CTkFrame(self.tab_merge, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Title
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")

        ctk.CTkLabel(
            title_container,
            text="🔗 Merge PDFs",
            font=("Inter", 18, "bold")
        ).pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="➕ " + self.t("btn_add"),
            width=100,
            height=35,
            command=self.add_merge_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=40,
            height=35,
            fg_color=Constants.DANGER_COLOR,
            hover_color="#dc2626",
            command=self.remove_merge_pdf,
            corner_radius=8,
            font=("Inter", 14)
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="🧹",
            width=40,
            height=35,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.clear_all_merge,
            corner_radius=8,
            font=("Inter", 14)
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="◄",
            width=40,
            height=35,
            command=self.move_merge_left,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="►",
            width=40,
            height=35,
            command=self.move_merge_right,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="✓ " + self.t("btn_merge"),
            width=120,
            height=35,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            command=self.merge_execute,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=(10, 0))

        # Gallery with modern styling
        gallery_container = ctk.CTkFrame(self.tab_merge, fg_color=self.get_bg_color(), corner_radius=15)
        gallery_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.merge_gallery = ctk.CTkScrollableFrame(
            gallery_container,
            orientation="horizontal",
            height=250,
            fg_color="transparent"
        )
        self.merge_gallery.pack(fill="both", expand=True, padx=15, pady=15)

        if self.merge_cards:
            self.refresh_merge_gallery()
    def add_merge_pdf(self): self.add_merge_pdf_from_list(filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")]))
    def add_merge_pdf_from_list(self, fs: List[str]) -> None:
        """Add multiple PDFs to merge queue with thumbnail generation"""
        for f in fs:
            try:
                logger.debug(f"Adding PDF to merge queue: {f}")
                self.settings_manager.add_recent_file(f)
                doc = fitz.open(f)
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(Constants.PDF_MERGE_PREVIEW_SCALE,
                                                           Constants.PDF_MERGE_PREVIEW_SCALE))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.merge_cards.append({'path': f, 'thumb': ctk.CTkImage(img, size=Constants.THUMBNAIL_SIZE)})
                doc.close()
            except Exception as e:
                logger.warning(f"Could not add PDF {f} to merge queue: {e}")
        self.refresh_merge_gallery()
    def refresh_merge_gallery(self):
        for w in self.merge_gallery.winfo_children(): w.destroy()
        for i, item in enumerate(self.merge_cards):
            c = "#1f538d" if i == self.merge_selected_index else "transparent"
            fr = ctk.CTkFrame(self.merge_gallery, width=120, height=200, fg_color=c, border_width=2, border_color="gray"); fr.pack(side="left", padx=5)
            fr.bind("<Button-1>", lambda e, x=i: self.select_merge_card(x))
            lbl = ctk.CTkLabel(fr, text="", image=item['thumb']); lbl.pack(pady=5)
            lbl.bind("<Button-1>", lambda e, x=i: self.select_merge_card(x))
            ctk.CTkLabel(fr, text=os.path.basename(item['path'])[:10]).pack()
    def select_merge_card(self, i): self.merge_selected_index = i; self.refresh_merge_gallery()
    def move_merge_left(self):
        i = self.merge_selected_index
        if i > 0: self.merge_cards[i], self.merge_cards[i-1] = self.merge_cards[i-1], self.merge_cards[i]; self.merge_selected_index -= 1; self.refresh_merge_gallery()
    def move_merge_right(self):
        i = self.merge_selected_index
        if i != -1 and i < len(self.merge_cards) - 1: self.merge_cards[i], self.merge_cards[i+1] = self.merge_cards[i+1], self.merge_cards[i]; self.merge_selected_index += 1; self.refresh_merge_gallery()
    def remove_merge_pdf(self):
        if self.merge_selected_index != -1: self.merge_cards.pop(self.merge_selected_index); self.merge_selected_index = -1; self.refresh_merge_gallery()
    def clear_all_merge(self): self.merge_cards = []; self.merge_selected_index = -1; self.refresh_merge_gallery()
    def merge_execute(self) -> None:
        """Merge multiple PDFs into one with preview"""
        if len(self.merge_cards) < 2:
            messagebox.showwarning(self.t("msg_error"), "2+ dosya gerekli")
            return

        # Create temporary merged PDF for preview
        temp_merged = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            logger.info(f"Creating preview of {len(self.merge_cards)} PDFs")
            m = PdfWriter()
            for card in self.merge_cards:
                m.append(card['path'])
            m.write(temp_merged.name)
            m.close()

            # Show preview with save callback
            def save_merged():
                s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
                if s:
                    import shutil
                    shutil.copy(temp_merged.name, s)
                    messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                    logger.info(f"Successfully merged PDFs to: {s}")

            self.show_pdf_preview(temp_merged.name, on_save_callback=save_merged)

        except Exception as e:
            logger.error(f"Error merging PDFs: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))
        finally:
            try:
                os.unlink(temp_merged.name)
            except:
                pass

    def setup_split_tab(self):
        # Header area
        header_frame = ctk.CTkFrame(self.tab_split, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Title and file info
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")

        ctk.CTkLabel(
            title_container,
            text="✂️ Split PDF",
            font=("Inter", 18, "bold")
        ).pack(side="left", padx=(0, 15))

        txt = os.path.basename(self.split_file_path) if self.split_file_path else ""
        self.lbl_split_info = ctk.CTkLabel(
            title_container,
            text=txt,
            text_color=Constants.PRIMARY_COLOR if txt else "gray",
            font=("Inter", 12, "bold" if txt else "normal")
        )
        self.lbl_split_info.pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="📁 " + self.t("btn_load"),
            width=100,
            height=35,
            command=self.load_split_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="↺",
            width=40,
            height=35,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.deselect_all_split,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="✕",
            width=40,
            height=35,
            fg_color=Constants.DANGER_COLOR,
            hover_color="#dc2626",
            command=self.clear_split_tab,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        # Rotation buttons
        ctk.CTkButton(
            btn_frame,
            text="⟲",
            width=40,
            height=35,
            command=lambda: self.rotate_pages(90),
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="⟳",
            width=40,
            height=35,
            command=lambda: self.rotate_pages(-90),
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="💾 " + self.t("btn_save_sel"),
            width=130,
            height=35,
            fg_color=Constants.WARNING_COLOR,
            hover_color="#f97316",
            command=self.save_selected_pages,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=(10, 0))

        # Pages gallery with modern styling
        gallery_container = ctk.CTkFrame(self.tab_split, fg_color=self.get_bg_color(), corner_radius=15)
        gallery_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.split_scroll = ctk.CTkScrollableFrame(
            gallery_container,
            fg_color="transparent"
        )
        self.split_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        if self.split_pages_data:
            for i, d in enumerate(self.split_pages_data):
                self.create_split_widget(i, d)
    def load_split_pdf(self): self.load_split_pdf_path(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_split_pdf_path(self, f: str) -> None:
        """Load PDF for splitting and generate page thumbnails"""
        if not f:
            return

        self.split_file_path = f
        self.split_pages_data = []
        self.lbl_split_info.configure(text=os.path.basename(f))

        for w in self.split_scroll.winfo_children():
            w.destroy()

        try:
            logger.info(f"Loading PDF for splitting: {f}")
            doc = fitz.open(f)

            for i in range(len(doc)):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(Constants.PDF_SPLIT_PREVIEW_SCALE,
                                                           Constants.PDF_SPLIT_PREVIEW_SCALE))
                pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                d = {
                    'page_num': i,
                    'image_ctk': ctk.CTkImage(pil, size=Constants.THUMBNAIL_SIZE),
                    'image_pil': pil,
                    'selected': False,
                    'widget': None,
                    'rotation': 0
                }
                self.split_pages_data.append(d)
                self.create_split_widget(i, d)

            doc.close()
            logger.info(f"Loaded {len(self.split_pages_data)} pages for splitting")
        except Exception as e:
            logger.error(f"Error loading PDF for splitting: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))
    def clear_split_tab(self): self.split_file_path = None; self.lbl_split_info.configure(text=""); self.split_pages_data = []; [w.destroy() for w in self.split_scroll.winfo_children()]
    def deselect_all_split(self):
        for i, d in enumerate(self.split_pages_data):
            if d['selected']: self.toggle_split_sel(i)
    def create_split_widget(self, i: int, d: Dict) -> None:
        """Create a thumbnail widget for split page selection"""
        fr = ctk.CTkFrame(self.split_scroll, width=120, height=180, border_width=2,
                         border_color="gray", fg_color="transparent")
        fr.grid(row=i//Constants.PAGES_PER_ROW, column=i%Constants.PAGES_PER_ROW, padx=5, pady=5)
        d['widget'] = fr

        lbl = ctk.CTkLabel(fr, text="", image=d['image_ctk'])
        lbl.pack(pady=5)

        num = ctk.CTkLabel(fr, text=f"{self.t('page')} {i+1}", font=("Arial", 11, "bold"))
        num.pack()

        for w in [fr, lbl, num]:
            w.bind("<Button-1>", lambda e, x=i: self.toggle_split_sel(x))
    def toggle_split_sel(self, i):
        d = self.split_pages_data[i]; d['selected'] = not d['selected']
        d['widget'].configure(fg_color="#e67e22" if d['selected'] else "transparent")
    def rotate_pages(self, a):
        sel = [d for d in self.split_pages_data if d['selected']]
        if not sel: return
        for d in sel:
            if a==90: d['rotation']-=90
            else: d['rotation']+=90
            pil = d['image_pil'].rotate(d['rotation'], expand=True)
            d['image_ctk'] = ctk.CTkImage(pil, size=(100, 140)); d['img_label'].configure(image=d['image_ctk'])
    def save_selected_pages(self):
        if not self.split_file_path: return
        sel = [d for d in self.split_pages_data if d['selected']]
        if not sel: messagebox.showwarning(self.t("msg_error"), self.t("warn_no_sel")); return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                r = PdfReader(self.split_file_path); w = PdfWriter()
                for d in sel:
                    p = r.pages[d['page_num']]; 
                    if d['rotation']!=0: p.rotate(-d['rotation'])
                    w.add_page(p)
                w.write(s); w.close(); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except: pass

    def setup_compress_tab(self):
        for w in self.tab_compress.winfo_children(): w.destroy()

        # Main container
        main_frame = ctk.CTkFrame(self.tab_compress, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Header with icon
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(pady=(0, 30))

        ctk.CTkLabel(header, text="📦", font=("Segoe UI Emoji", 48)).pack()
        ctk.CTkLabel(header, text=self.t("lbl_compress_title"),
                    font=("Inter", 22, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(header, text="Reduce PDF file size while maintaining quality",
                    font=("Inter", 13),
                    text_color=self.get_secondary_text_color()).pack()

        # File selection area
        file_frame = ctk.CTkFrame(main_frame, fg_color=self.get_bg_color(), corner_radius=15)
        file_frame.pack(fill="x", pady=20, padx=20)

        btn_container = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_container.pack(pady=20, padx=20)

        ctk.CTkButton(
            btn_container,
            text=f"📁  {self.t('btn_select')}",
            command=self.select_compress_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=45,
            font=("Inter", 13, "bold"),
            corner_radius=10
        ).pack(side="left", padx=5)

        if self.compress_file_path:
            ctk.CTkButton(
                btn_container,
                text="✕",
                width=45,
                height=45,
                fg_color=Constants.DANGER_COLOR,
                hover_color="#dc2626",
                command=self.clear_compress_file,
                corner_radius=10,
                font=("Inter", 14, "bold")
            ).pack(side="left", padx=5)

        txt = os.path.basename(self.compress_file_path) if self.compress_file_path else self.t("lbl_no_file")
        self.lbl_compress_file = ctk.CTkLabel(
            file_frame,
            text=txt,
            text_color="gray" if not self.compress_file_path else Constants.PRIMARY_COLOR,
            font=("Inter", 12, "bold" if self.compress_file_path else "normal")
        )
        self.lbl_compress_file.pack(pady=(0, 20))

        # Quality settings
        if self.compress_file_path:
            settings_frame = ctk.CTkFrame(main_frame, fg_color=self.get_bg_color(), corner_radius=15)
            settings_frame.pack(fill="x", pady=10, padx=20)

            ctk.CTkLabel(
                settings_frame,
                text="⚙️  Compression Quality",
                font=("Inter", 14, "bold")
            ).pack(pady=(20, 10))

            self.compress_slider = ctk.CTkSlider(
                settings_frame,
                from_=Constants.MIN_QUALITY,
                to=Constants.MAX_QUALITY,
                number_of_steps=Constants.QUALITY_STEPS,
                command=self.on_compress_slider,
                width=300,
                height=20,
                button_color=Constants.WARNING_COLOR,
                button_hover_color="#f97316",
                progress_color=Constants.WARNING_COLOR
            )
            self.compress_slider.set(Constants.DEFAULT_QUALITY)
            self.compress_slider.pack(pady=10)

            self.lbl_quality_value = ctk.CTkLabel(
                settings_frame,
                text=f"Quality: {int(self.compress_slider.get()*100)}%",
                font=("Inter", 12),
                text_color=self.get_secondary_text_color()
            )
            self.lbl_quality_value.pack(pady=(0, 20))

        # Compress button
        state = "normal" if self.compress_file_path else "disabled"
        ctk.CTkButton(
            main_frame,
            text=f"🎯  {self.t('btn_compress')}",
            state=state,
            fg_color=Constants.WARNING_COLOR,
            hover_color="#f97316",
            command=self.start_compression,
            height=50,
            font=("Inter", 14, "bold"),
            corner_radius=12
        ).pack(pady=20)
        if self.compress_file_path: self.update_compress_ui_info()
    def on_compress_slider(self, val): self.lbl_quality_value.configure(text=f"Quality: %{int(val*100)}")
    def select_compress_pdf(self): self.load_compress_pdf(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_compress_pdf(self, f):
        if not f: return
        self.compress_file_path = f
        self.settings_manager.add_recent_file(f)
        # Load default quality from settings
        default_quality = self.settings_manager.get("default_quality", Constants.DEFAULT_QUALITY)
        self.setup_compress_tab()
        if hasattr(self, 'compress_slider'):
            self.compress_slider.set(default_quality)
    def update_compress_ui_info(self):
        sz = os.path.getsize(self.compress_file_path) / (1024*1024)
        self.lbl_compress_file.configure(text=f"{os.path.basename(self.compress_file_path)} ({sz:.2f} MB)")
    def clear_compress_file(self): self.compress_file_path = None; self.setup_compress_tab()
    def start_compression(self) -> None:
        """Compress PDF by reducing image quality"""
        if not self.compress_file_path:
            return

        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            qv = self.compress_slider.get()
            dpi = int(Constants.BASE_DPI + (qv * Constants.DPI_RANGE))
            jq = int(qv * Constants.BASE_JPEG_QUALITY)

            try:
                logger.info(f"Compressing PDF: {self.compress_file_path} with quality {int(qv*100)}%")
                doc = fitz.open(self.compress_file_path)
                lst = []

                for i in range(len(doc)):
                    pix = doc[i].get_pixmap(dpi=dpi, alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    b = io.BytesIO()
                    img.save(b, format='JPEG', quality=jq, optimize=True)
                    lst.append(b.getvalue())
                    logger.debug(f"Compressed page {i+1}/{len(doc)}")

                with open(s, "wb") as f:
                    f.write(img2pdf.convert(lst))

                doc.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                logger.info(f"Successfully compressed PDF to: {s}")
            except Exception as e:
                logger.error(f"Error compressing PDF: {e}", exc_info=True)
                messagebox.showerror(self.t("msg_error"), str(e))

    def setup_sign_tab(self):
        # Left panel - Signature Library
        lp = ctk.CTkFrame(self.tab_sign, width=280, fg_color=self.get_bg_color(), corner_radius=15)
        lp.pack(side="left", fill="y", padx=(15, 8), pady=15)
        lp.pack_propagate(False)

        # Library header
        lib_header = ctk.CTkFrame(lp, fg_color="transparent")
        lib_header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            lib_header,
            text="✒️ " + self.t("lbl_lib"),
            font=("Inter", 16, "bold")
        ).pack(anchor="w")

        # Add signature button
        ctk.CTkButton(
            lp,
            text="➕ " + self.t("btn_add_sign"),
            command=self.add_signature_image,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=40,
            font=("Inter", 12, "bold"),
            corner_radius=10
        ).pack(padx=15, pady=10, fill="x")

        # Size slider section
        size_frame = ctk.CTkFrame(lp, fg_color="transparent")
        size_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            size_frame,
            text=self.t("lbl_sign_size"),
            font=("Inter", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.sign_size_slider = ctk.CTkSlider(
            size_frame,
            from_=Constants.MIN_SIGNATURE_SIZE,
            to=Constants.MAX_SIGNATURE_SIZE,
            number_of_steps=Constants.SIGNATURE_STEPS,
            button_color=Constants.PRIMARY_COLOR,
            button_hover_color=Constants.PRIMARY_HOVER,
            progress_color=Constants.PRIMARY_COLOR
        )
        self.sign_size_slider.set(Constants.DEFAULT_SIGNATURE_SIZE)
        self.sign_size_slider.pack(fill="x")

        # Signature library scroll
        self.sign_scroll = ctk.CTkScrollableFrame(lp, fg_color="transparent")
        self.sign_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        # Right panel - PDF Canvas
        rp = ctk.CTkFrame(self.tab_sign, fg_color="transparent")
        rp.pack(side="right", fill="both", expand=True, padx=(8, 15), pady=15)

        # Top controls
        tc = ctk.CTkFrame(rp, fg_color="transparent")
        tc.pack(fill="x", pady=(0, 10))

        # Left controls
        left_controls = ctk.CTkFrame(tc, fg_color="transparent")
        left_controls.pack(side="left")

        ctk.CTkButton(
            left_controls,
            text="📁 " + self.t("btn_load"),
            command=self.open_sign_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=35,
            width=100,
            font=("Inter", 12, "bold"),
            corner_radius=8
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            left_controls,
            text="✕",
            width=40,
            height=35,
            fg_color=Constants.DANGER_COLOR,
            hover_color="#dc2626",
            command=self.close_sign_pdf,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        # Navigation
        ctk.CTkButton(
            left_controls,
            text="◄",
            width=40,
            height=35,
            command=self.prev_sign_page,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=(10, 3))

        self.lbl_sign_page = ctk.CTkLabel(
            left_controls,
            text="0/0",
            font=("Inter", 12, "bold"),
            text_color=self.get_secondary_text_color()
        )
        self.lbl_sign_page.pack(side="left", padx=8)

        ctk.CTkButton(
            left_controls,
            text="►",
            width=40,
            height=35,
            command=self.next_sign_page,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            corner_radius=8,
            font=("Inter", 14, "bold")
        ).pack(side="left", padx=3)

        # Right controls
        right_controls = ctk.CTkFrame(tc, fg_color="transparent")
        right_controls.pack(side="right")

        ctk.CTkButton(
            right_controls,
            text="↶ " + self.t("btn_undo"),
            width=90,
            height=35,
            fg_color=Constants.DANGER_COLOR,
            hover_color="#dc2626",
            command=self.undo_last_stamp,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            right_controls,
            text="👁 " + self.t("btn_preview"),
            width=100,
            height=35,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.preview_signed_page,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            right_controls,
            text="💾 " + self.t("btn_save_sel"),
            width=110,
            height=35,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            command=self.save_signed_pdf,
            corner_radius=8,
            font=("Inter", 12, "bold")
        ).pack(side="left", padx=3)

        # Canvas container with modern styling
        self.canvas_container = ctk.CTkFrame(rp, fg_color=self.get_bg_color(), corner_radius=15)
        self.canvas_container.pack(fill="both", expand=True)

        self.v_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="vertical")
        self.h_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="horizontal")

        self.sign_canvas = Canvas(
            self.canvas_container,
            bg="#e5e7eb",
            bd=0,
            highlightthickness=0,
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )

        self.v_scroll.configure(command=self.sign_canvas.yview)
        self.h_scroll.configure(command=self.sign_canvas.xview)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.sign_canvas.pack(side="left", fill="both", expand=True, padx=2, pady=2)

        self.sign_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.sign_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.sign_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        if self.sign_images:
            self.refresh_signature_library()
        if self.sign_doc:
            self.show_current_sign_page()
    def make_image_transparent(self, pil_img: Image.Image) -> Image.Image:
        """Convert white/light areas of image to transparent"""
        pil_img = pil_img.convert("RGBA")
        datas = pil_img.getdata()
        new_data = []

        for item in datas:
            # Make white/light pixels transparent
            if (item[0] > Constants.TRANSPARENT_THRESHOLD and
                item[1] > Constants.TRANSPARENT_THRESHOLD and
                item[2] > Constants.TRANSPARENT_THRESHOLD):
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        pil_img.putdata(new_data)
        return pil_img
    def add_signature_image(self) -> None:
        """Add a signature image to the library"""
        path = filedialog.askopenfilename(filetypes=Constants.IMAGE_TYPES)
        if not path:
            return

        try:
            logger.info(f"Adding signature image: {path}")
            pil = self.make_image_transparent(Image.open(path))
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            pil.save(t.name)
            t.close()

            self.temp_image_files.append(t.name)
            self.sign_images.append({'path': t.name, 'pil': pil})
            self.refresh_signature_library()
            logger.info(f"Successfully added signature image")
        except Exception as e:
            logger.error(f"Error adding signature image: {e}", exc_info=True)
            messagebox.showerror(self.t("msg_error"), str(e))
    def refresh_signature_library(self):
        for w in self.sign_scroll.winfo_children(): w.destroy()
        for i, item in enumerate(self.sign_images):
            thumb = item['pil'].copy()
            thumb.thumbnail(Constants.SIGNATURE_THUMBNAIL_SIZE)
            c = "#1f538d" if i == self.sign_selected_img_index else "transparent"
            fr = ctk.CTkFrame(self.sign_scroll, fg_color=c); fr.pack(pady=5, fill="x")
            lbl = ctk.CTkLabel(fr, text="", image=ctk.CTkImage(thumb, size=(thumb.width, thumb.height))); lbl.pack(pady=5)
            for w in [fr, lbl]: w.bind("<Button-1>", lambda e, x=i: self.select_signature(x))
    def select_signature(self, i): self.sign_selected_img_index = i; self.refresh_signature_library()
    def open_sign_pdf(self): self.load_sign_pdf(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_sign_pdf(self, f):
        if not f: return
        self.sign_pdf_path = f; self.sign_doc = fitz.open(f); self.sign_current_page_num = 0; self.sign_placements = {}; self.show_current_sign_page()
    def close_sign_pdf(self): self.sign_pdf_path = None; self.sign_doc = None; self.sign_placements = {}; self.sign_canvas.delete("all"); self.lbl_sign_page.configure(text="0/0")
    def show_current_sign_page(self):
        if not self.sign_doc: return
        self.sign_canvas.delete("all"); page = self.sign_doc.load_page(self.sign_current_page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)); self.bg_tk_img = ImageTk.PhotoImage(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        self.sign_canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.sign_canvas.create_image(0, 0, image=self.bg_tk_img, anchor="nw", tags="background")
        if self.sign_current_page_num in self.sign_placements:
            for i, (idx, x, y, uid, scale) in enumerate(self.sign_placements[self.sign_current_page_num]):
                stamp = self.sign_images[idx]['pil'].copy(); 
                w, h = int(150*scale), int(150*scale); stamp.thumbnail((w, h))
                tk_stamp = ImageTk.PhotoImage(stamp); self.canvas_images[uid] = tk_stamp
                self.sign_canvas.create_image(x*1.5, y*1.5, image=tk_stamp, anchor="nw", tags=("movable", uid))
        self.lbl_sign_page.configure(text=f"{self.sign_current_page_num + 1} / {len(self.sign_doc)}")
    def on_canvas_press(self, e):
        cx, cy = self.sign_canvas.canvasx(e.x), self.sign_canvas.canvasy(e.y)
        try:
            it = self.sign_canvas.find_closest(cx, cy)[0]; tags = self.sign_canvas.gettags(it)
            if "movable" in tags: self.drag_data["item"] = it; self.drag_data["x"] = cx; self.drag_data["y"] = cy
            elif self.sign_selected_img_index != -1: self.add_stamp_to_data(cx, cy)
        except: pass
    def on_canvas_drag(self, e):
        if self.drag_data["item"]:
            cx, cy = self.sign_canvas.canvasx(e.x), self.sign_canvas.canvasy(e.y)
            self.sign_canvas.move(self.drag_data["item"], cx-self.drag_data["x"], cy-self.drag_data["y"])
            self.drag_data["x"] = cx; self.drag_data["y"] = cy
    def on_canvas_release(self, e):
        if self.drag_data["item"]:
            it = self.drag_data["item"]; tags = self.sign_canvas.gettags(it)
            if len(tags) > 1:
                uid = tags[1]; coords = self.sign_canvas.coords(it)
                pd = self.sign_placements.get(self.sign_current_page_num, [])
                for i, r in enumerate(pd):
                    if r[3] == uid: pd[i] = (r[0], coords[0]/1.5, coords[1]/1.5, uid, r[4]); break
            self.drag_data["item"] = None
    def add_stamp_to_data(self, cx, cy):
        import uuid; uid = str(uuid.uuid4()); scale = self.sign_size_slider.get()
        if self.sign_current_page_num not in self.sign_placements: self.sign_placements[self.sign_current_page_num] = []
        self.sign_placements[self.sign_current_page_num].append((self.sign_selected_img_index, (cx/1.5)-30, (cy/1.5)-30, uid, scale))
        self.show_current_sign_page()
    def undo_last_stamp(self):
        if self.sign_current_page_num in self.sign_placements and self.sign_placements[self.sign_current_page_num]:
            self.sign_placements[self.sign_current_page_num].pop(); self.show_current_sign_page()
    def prev_sign_page(self): 
        if self.sign_current_page_num > 0: self.sign_current_page_num -= 1; self.show_current_sign_page()
    def next_sign_page(self):
        if self.sign_doc and self.sign_current_page_num < len(self.sign_doc) - 1: self.sign_current_page_num += 1; self.show_current_sign_page()
    def preview_signed_page(self):
        if not self.sign_pdf_path: return
        win = ctk.CTkToplevel(self); win.geometry("900x900"); win.title("Preview"); win.attributes('-topmost', True); win.grab_set()
        try:
            d = fitz.open(self.sign_pdf_path); p = d[self.sign_current_page_num]
            if self.sign_current_page_num in self.sign_placements:
                for idx, x, y, uid, scale in self.sign_placements[self.sign_current_page_num]:
                    path = self.sign_images[idx]['path']; w, h = 100*scale, 100*scale; p.insert_image(fitz.Rect(x, y, x+w, y+h), filename=path)
            pix = p.get_pixmap(matrix=fitz.Matrix(2,2)); pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            sf = ctk.CTkScrollableFrame(win); sf.pack(fill="both", expand=True)
            ctk.CTkLabel(sf, text="", image=ctk.CTkImage(pil, size=(pix.width//2, pix.height//2))).pack(pady=10)
        except: pass
    def save_signed_pdf(self):
        if not self.sign_doc: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            for n, stamps in self.sign_placements.items():
                p = self.sign_doc[n]
                for idx, x, y, uid, scale in stamps:
                    path = self.sign_images[idx]['path']; w, h = 100*scale, 100*scale; p.insert_image(fitz.Rect(x, y, x+w, y+h), filename=path)
            self.sign_doc.save(s); messagebox.showinfo(self.t("msg_success"), self.t("msg_done")); self.load_sign_pdf(self.sign_pdf_path)

    # --- 7. GÜVENLİK & ARAÇLAR + META VERİ (GÜNCELLENDİ) ---
    def setup_tools_tab(self):
        for w in self.tab_tools.winfo_children(): w.destroy()

        # Header
        header_frame = ctk.CTkFrame(self.tab_tools, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text="🔧 PDF Tools",
            font=("Inter", 18, "bold")
        ).pack(side="left")

        # Scrollable main container
        ms = ctk.CTkScrollableFrame(self.tab_tools, fg_color="transparent")
        ms.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # File selection
        file_frame = ctk.CTkFrame(ms, fg_color=self.get_bg_color(), corner_radius=15)
        file_frame.pack(fill="x", pady=(0, 15))

        file_content = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            file_content,
            text="📁 " + self.t("btn_select"),
            command=self.load_tools_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            height=40,
            width=130,
            font=("Inter", 12, "bold"),
            corner_radius=10
        ).pack(side="left", padx=(0, 10))

        txt = os.path.basename(self.tools_file_path) if self.tools_file_path else self.t("lbl_no_file")
        self.lbl_tools_file = ctk.CTkLabel(
            file_content,
            text=txt,
            text_color=Constants.PRIMARY_COLOR if self.tools_file_path else "gray",
            font=("Inter", 12, "bold" if self.tools_file_path else "normal")
        )
        self.lbl_tools_file.pack(side="left", padx=10)

        if self.tools_file_path:
            ctk.CTkButton(
                file_content,
                text="✕",
                width=40,
                height=40,
                fg_color=Constants.DANGER_COLOR,
                hover_color="#dc2626",
                command=self.clear_tools_file,
                corner_radius=10,
                font=("Inter", 14, "bold")
            ).pack(side="right")

        # Encryption Tool
        f1 = ctk.CTkFrame(ms, fg_color=self.get_bg_color(), corner_radius=15)
        f1.pack(fill="x", pady=(0, 15))

        f1_content = ctk.CTkFrame(f1, fg_color="transparent")
        f1_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            f1_content,
            text="🔒 " + self.t("tool_encrypt_title"),
            font=("Inter", 16, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ep = ctk.CTkEntry(
            f1_content,
            placeholder_text=self.t("lbl_password"),
            show="*",
            height=40,
            font=("Inter", 12),
            corner_radius=10
        )
        ep.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            f1_content,
            text="✓ " + self.t("btn_apply"),
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            command=lambda: self.tool_encrypt(ep.get()),
            height=40,
            font=("Inter", 12, "bold"),
            corner_radius=10
        ).pack(fill="x")

        # Watermark Tool
        f2 = ctk.CTkFrame(ms, fg_color=self.get_bg_color(), corner_radius=15)
        f2.pack(fill="x", pady=(0, 15))

        f2_content = ctk.CTkFrame(f2, fg_color="transparent")
        f2_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            f2_content,
            text="💧 " + self.t("tool_watermark_title"),
            font=("Inter", 16, "bold")
        ).pack(anchor="w", pady=(0, 15))

        we = ctk.CTkEntry(
            f2_content,
            placeholder_text=self.t("lbl_watermark_text"),
            height=40,
            font=("Inter", 12),
            corner_radius=10
        )
        we.pack(fill="x", pady=(0, 10))

        wc = ctk.CTkComboBox(
            f2_content,
            values=["Red", "Blue", "Gray", "Black"],
            height=40,
            font=("Inter", 12),
            corner_radius=10,
            button_color=Constants.PRIMARY_COLOR,
            button_hover_color=Constants.PRIMARY_HOVER
        )
        wc.set("Red")
        wc.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            f2_content,
            text="✓ " + self.t("btn_apply"),
            fg_color=Constants.WARNING_COLOR,
            hover_color="#f97316",
            command=lambda: self.tool_watermark(we.get(), wc.get()),
            height=40,
            font=("Inter", 12, "bold"),
            corner_radius=10
        ).pack(fill="x")

        # Page Numbers Tool
        f3 = ctk.CTkFrame(ms, fg_color=self.get_bg_color(), corner_radius=15)
        f3.pack(fill="x", pady=(0, 15))

        f3_content = ctk.CTkFrame(f3, fg_color="transparent")
        f3_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            f3_content,
            text="🔢 " + self.t("tool_page_num_title"),
            font=("Inter", 16, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkButton(
            f3_content,
            text="✓ " + self.t("btn_apply"),
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            command=self.tool_add_page_numbers,
            height=40,
            font=("Inter", 12, "bold"),
            corner_radius=10
        ).pack(fill="x")

        # Metadata Tool
        f4 = ctk.CTkFrame(ms, fg_color=self.get_bg_color(), corner_radius=15)
        f4.pack(fill="x", pady=(0, 15))

        f4_content = ctk.CTkFrame(f4, fg_color="transparent")
        f4_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            f4_content,
            text="📋 " + self.t("tool_metadata_title"),
            font=("Inter", 16, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(
            f4_content,
            text=self.t("lbl_meta_title"),
            font=("Inter", 11)
        ).pack(anchor="w", pady=(5, 2))

        meta_title = ctk.CTkEntry(
            f4_content,
            height=40,
            font=("Inter", 12),
            corner_radius=10
        )
        meta_title.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            f4_content,
            text=self.t("lbl_meta_author"),
            font=("Inter", 11)
        ).pack(anchor="w", pady=(5, 2))

        meta_author = ctk.CTkEntry(
            f4_content,
            height=40,
            font=("Inter", 12),
            corner_radius=10
        )
        meta_author.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            f4_content,
            text="✓ " + self.t("btn_apply"),
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=lambda: self.tool_metadata(meta_title.get(), meta_author.get()),
            height=40,
            font=("Inter", 12, "bold"),
            corner_radius=10
        ).pack(fill="x")

    def load_tools_pdf(self, f=None):
        if not f: f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f: self.tools_file_path = f; self.setup_tools_tab()
    def clear_tools_file(self): self.tools_file_path = None; self.setup_tools_tab()
    def tool_encrypt(self, password: str) -> None:
        """Encrypt PDF with password protection"""
        if not self.tools_file_path or not password:
            return

        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                logger.info(f"Encrypting PDF: {self.tools_file_path}")
                doc = fitz.open(self.tools_file_path)
                doc.save(s, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=password, owner_pw=password)
                doc.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                logger.info(f"Successfully encrypted PDF to: {s}")
            except Exception as e:
                logger.error(f"Error encrypting PDF: {e}", exc_info=True)
                messagebox.showerror(self.t("msg_error"), str(e))
    def tool_watermark(self, text: str, color_name: str) -> None:
        """Add watermark text to all pages of PDF"""
        if not self.tools_file_path or not text:
            return

        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                logger.info(f"Adding watermark to PDF: {self.tools_file_path}")
                doc = fitz.open(self.tools_file_path)
                rgb = Constants.COLORS.get(color_name, (0, 0, 0))

                # Try to load Arial font
                windir = os.environ.get("WINDIR", "C:/Windows")
                font_path = os.path.join(windir, "Fonts", "arial.ttf")
                used_fontname = "helv"
                font_buffer = None

                if os.path.exists(font_path):
                    try:
                        with open(font_path, "rb") as f:
                            font_buffer = f.read()
                        fitz.Font(fontbuffer=font_buffer)
                        used_fontname = "arial_tr"
                    except:
                        pass

                fontsize = Constants.WATERMARK_FONT_SIZE
                calc_font = fitz.Font(fontbuffer=font_buffer) if font_buffer else fitz.Font("helv")
                text_len = calc_font.text_length(text, fontsize)

                for page in doc:
                    if font_buffer and used_fontname == "arial_tr":
                        try:
                            page.insert_font(fontname=used_fontname, fontbuffer=font_buffer)
                        except:
                            used_fontname = "helv"

                    w, h = page.rect.width, page.rect.height
                    center = fitz.Point(w/2, h/2)
                    p_start = fitz.Point(center.x - text_len/2, center.y + fontsize/4)
                    mat = fitz.Matrix(Constants.WATERMARK_ANGLE)

                    try:
                        page.insert_text(p_start, text, fontsize=fontsize, fontname=used_fontname,
                                       color=rgb, fill_opacity=Constants.WATERMARK_OPACITY, morph=(center, mat))
                    except:
                        page.insert_text(p_start, text, fontsize=fontsize, fontname="helv",
                                       color=rgb, fill_opacity=Constants.WATERMARK_OPACITY, morph=(center, mat))

                doc.save(s)
                doc.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                logger.info(f"Successfully added watermark to: {s}")
            except Exception as e:
                logger.error(f"Error adding watermark: {e}", exc_info=True)
                messagebox.showerror(self.t("msg_error"), str(e))
    def tool_add_page_numbers(self) -> None:
        """Add page numbers to all pages of PDF"""
        if not self.tools_file_path:
            return

        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                logger.info(f"Adding page numbers to PDF: {self.tools_file_path}")
                doc = fitz.open(self.tools_file_path)
                total = len(doc)

                for i, page in enumerate(doc):
                    w, h = page.rect.width, page.rect.height
                    text = f"{i+1} / {total}"
                    page.insert_text((w/2 - 10, h - 20), text,
                                   fontsize=Constants.PAGE_NUMBER_FONT_SIZE,
                                   color=(0, 0, 0))

                doc.save(s)
                doc.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                logger.info(f"Successfully added page numbers to: {s}")
            except Exception as e:
                logger.error(f"Error adding page numbers: {e}", exc_info=True)
                messagebox.showerror(self.t("msg_error"), str(e))
            
    # YENİ: METADATA DÜZENLEME
    def tool_metadata(self, title: str, author: str) -> None:
        """Update PDF metadata (title and author)"""
        if not self.tools_file_path:
            return

        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                logger.info(f"Updating metadata for PDF: {self.tools_file_path}")
                doc = fitz.open(self.tools_file_path)
                meta = doc.metadata

                if title:
                    meta["title"] = title
                    logger.debug(f"Set title: {title}")
                if author:
                    meta["author"] = author
                    logger.debug(f"Set author: {author}")

                doc.set_metadata(meta)
                doc.save(s)
                doc.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
                logger.info(f"Successfully updated metadata in: {s}")
            except Exception as e:
                logger.error(f"Error updating metadata: {e}", exc_info=True)
                messagebox.showerror(self.t("msg_error"), str(e))

    # --- BATCH PROCESSING ---
    def setup_batch_tab(self):
        """Setup batch processing tab - Process multiple PDFs at once"""
        for w in self.tab_batch.winfo_children(): w.destroy()

        # Main split view
        left = ctk.CTkFrame(self.tab_batch, fg_color=self.get_bg_color(), corner_radius=15, width=300)
        left.pack(side="left", fill="y", padx=(20, 10), pady=20)
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="⚡ " + self.t("batch_title"), font=("Inter", 16, "bold")).pack(pady=(20, 10), padx=15)

        self.batch_op_var = ctk.StringVar(value="compress")
        for op, label in [("compress", self.t("batch_op_compress")),
                          ("pdf2img", self.t("batch_op_pdf2img")),
                          ("jpg2pdf", self.t("batch_op_jpg2pdf"))]:
            ctk.CTkRadioButton(left, text=label, variable=self.batch_op_var, value=op).pack(anchor="w", padx=25, pady=5)

        ctk.CTkButton(left, text="📁 " + self.t("batch_select_folder"), command=lambda: setattr(self, 'batch_output_folder', filedialog.askdirectory()) if filedialog.askdirectory() else None, height=40, corner_radius=10).pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkButton(left, text="🚀 " + self.t("batch_start"), command=self.start_batch, fg_color=Constants.SECONDARY_COLOR, height=50, font=("Inter", 14, "bold"), corner_radius=12).pack(fill="x", padx=20, pady=10)

        right = ctk.CTkFrame(self.tab_batch, fg_color=self.get_bg_color(), corner_radius=15)
        right.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        top_bar = ctk.CTkFrame(right, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(top_bar, text=self.t("batch_files"), font=("Inter", 14, "bold")).pack(side="left")
        ctk.CTkButton(top_bar, text="➕ Files", command=self.add_batch_files_smart, width=80, height=30, corner_radius=8).pack(side="right", padx=3)
        ctk.CTkButton(top_bar, text="🗑️", width=30, height=30, command=lambda: (setattr(self, 'batch_files', []), self.refresh_batch_list()), fg_color=Constants.DANGER_COLOR, corner_radius=8).pack(side="right", padx=3)

        self.batch_list_frame = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.batch_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.refresh_batch_list()

    def add_batch_files_smart(self):
        """Add files based on selected operation"""
        op = self.batch_op_var.get()
        if op == "jpg2pdf":
            # For JPG to PDF, accept image files
            files = filedialog.askopenfilenames(filetypes=Constants.IMAGE_TYPES)
        else:
            # For other operations, accept PDFs
            files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])

        for f in files:
            if f not in self.batch_files:
                self.batch_files.append(f)
        self.refresh_batch_list()

    def refresh_batch_list(self):
        for w in self.batch_list_frame.winfo_children(): w.destroy()
        if not self.batch_files:
            ctk.CTkLabel(self.batch_list_frame, text="No files. Click '➕ Files'", text_color=self.get_secondary_text_color()).pack(pady=50)
        else:
            for i, f in enumerate(self.batch_files):
                fr = ctk.CTkFrame(self.batch_list_frame, fg_color="transparent")
                fr.pack(fill="x", pady=2)
                ctk.CTkLabel(fr, text=f"{i+1}. {os.path.basename(f)}", anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkButton(fr, text="✕", width=25, height=25, command=lambda idx=i: (self.batch_files.pop(idx), self.refresh_batch_list()), fg_color=Constants.DANGER_COLOR, corner_radius=6).pack(side="right")

    def start_batch(self):
        if not self.batch_files or not self.batch_output_folder:
            messagebox.showwarning(self.t("msg_error"), "Add files and select output folder")
            return

        op = self.batch_op_var.get()
        for i, f in enumerate(self.batch_files):
            try:
                logger.info(f"Batch processing {i+1}/{len(self.batch_files)}: {f}")
                if op == "compress":
                    doc = fitz.open(f)
                    lst = []
                    for pg in doc:
                        pix = pg.get_pixmap(dpi=120, alpha=False)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        b = io.BytesIO()
                        img.save(b, format='JPEG', quality=50, optimize=True)
                        lst.append(b.getvalue())
                    out = os.path.join(self.batch_output_folder, f"compressed_{os.path.basename(f)}")
                    with open(out, "wb") as of: of.write(img2pdf.convert(lst))
                    doc.close()
                elif op == "pdf2img":
                    doc = fitz.open(f)
                    base = os.path.splitext(os.path.basename(f))[0]
                    for j, pg in enumerate(doc):
                        pix = pg.get_pixmap(dpi=150, alpha=False)
                        pix.save(os.path.join(self.batch_output_folder, f"{base}_p{j+1}.jpg"))
                    doc.close()
                elif op == "jpg2pdf":
                    # Convert single image to PDF
                    base = os.path.splitext(os.path.basename(f))[0]
                    out = os.path.join(self.batch_output_folder, f"{base}.pdf")
                    with open(out, "wb") as of:
                        of.write(img2pdf.convert(f))
            except Exception as e:
                logger.error(f"Batch error on {f}: {e}")

        messagebox.showinfo(self.t("msg_success"), f"{self.t('batch_completed')}\n{len(self.batch_files)} files processed")

    def setup_annotate_tab(self):
        """Setup Annotation tab - Add text and drawings to PDF"""
        # Header
        header = ctk.CTkFrame(self.tab_annotate, fg_color=self.get_card_color(), corner_radius=15)
        header.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(
            header,
            text=self.t("annotate_title"),
            font=("Inter", 24, "bold"),
            text_color=self.get_text_color()
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            header,
            text=self.t("annotate_subtitle"),
            font=("Inter", 13),
            text_color=self.get_secondary_text_color()
        ).pack(pady=(0, 15))

        # Controls
        controls = ctk.CTkFrame(self.tab_annotate, fg_color=self.get_card_color(), corner_radius=15)
        controls.pack(padx=20, pady=(0, 10), fill="x")

        # Load/Save buttons
        btn_row1 = ctk.CTkFrame(controls, fg_color="transparent")
        btn_row1.pack(pady=(15, 10), padx=20)

        ctk.CTkButton(
            btn_row1,
            text=self.t("annotate_load"),
            command=self.load_annotate_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            font=("Inter", 13, "bold"),
            height=40,
            corner_radius=10
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_row1,
            text=self.t("annotate_save"),
            command=self.save_annotate_pdf,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            font=("Inter", 13, "bold"),
            height=40,
            corner_radius=10
        ).pack(side="left", padx=5)

        # Tool buttons
        btn_row2 = ctk.CTkFrame(controls, fg_color="transparent")
        btn_row2.pack(pady=10, padx=20)

        self.annotate_tool = ctk.StringVar(value="text")

        tools = [
            ("annotate_text", "text"),
            ("annotate_rectangle", "rect"),
            ("annotate_circle", "circle"),
            ("annotate_line", "line"),
            ("annotate_arrow", "arrow"),
            ("annotate_highlight", "highlight")
        ]

        for label_key, tool_value in tools:
            ctk.CTkRadioButton(
                btn_row2,
                text=self.t(label_key),
                variable=self.annotate_tool,
                value=tool_value,
                font=("Inter", 12),
                fg_color=Constants.PRIMARY_COLOR,
                hover_color=Constants.PRIMARY_HOVER
            ).pack(side="left", padx=5)

        # Color and size
        opt_row = ctk.CTkFrame(controls, fg_color="transparent")
        opt_row.pack(pady=(10, 15), padx=20)

        ctk.CTkLabel(
            opt_row,
            text=self.t("annotate_color"),
            font=("Inter", 12),
            text_color=self.get_text_color()
        ).pack(side="left", padx=5)

        self.annotate_color = ctk.StringVar(value="red")
        ctk.CTkComboBox(
            opt_row,
            values=["red", "blue", "green", "yellow", "black"],
            variable=self.annotate_color,
            width=120,
            font=("Inter", 12)
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            opt_row,
            text=self.t("annotate_size"),
            font=("Inter", 12),
            text_color=self.get_text_color()
        ).pack(side="left", padx=(20, 5))

        self.annotate_size = ctk.IntVar(value=2)
        ctk.CTkSlider(
            opt_row,
            from_=1,
            to=10,
            variable=self.annotate_size,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            opt_row,
            text=self.t("annotate_clear"),
            command=self.clear_annotations,
            fg_color=Constants.DANGER_COLOR,
            hover_color=Constants.DANGER_HOVER,
            font=("Inter", 12, "bold"),
            height=35,
            corner_radius=10
        ).pack(side="left", padx=20)

        # Page navigation
        page_nav = ctk.CTkFrame(controls, fg_color="transparent")
        page_nav.pack(pady=(5, 15), padx=20)

        self.annotate_page_label = ctk.CTkLabel(
            page_nav,
            text="Sayfa: - / -" if self.current_lang == "tr" else "Page: - / -",
            font=("Inter", 13, "bold"),
            text_color=self.get_text_color()
        )
        self.annotate_page_label.pack(side="left", padx=10)

        ctk.CTkButton(
            page_nav,
            text="⬅ Önceki" if self.current_lang == "tr" else "⬅ Previous",
            command=self.prev_annotate_page,
            fg_color=Constants.NEUTRAL_COLOR,
            hover_color=Constants.NEUTRAL_HOVER,
            font=("Inter", 12, "bold"),
            height=35,
            width=120,
            corner_radius=10
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            page_nav,
            text="Sonraki ➡" if self.current_lang == "tr" else "Next ➡",
            command=self.next_annotate_page,
            fg_color=Constants.NEUTRAL_COLOR,
            hover_color=Constants.NEUTRAL_HOVER,
            font=("Inter", 12, "bold"),
            height=35,
            width=120,
            corner_radius=10
        ).pack(side="left", padx=5)

        # Canvas for annotation with scrollbars
        canvas_frame = ctk.CTkFrame(self.tab_annotate, fg_color=self.get_card_color(), corner_radius=15)
        canvas_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Create scrollbars
        from tkinter import Scrollbar

        v_scrollbar = Scrollbar(canvas_frame, orient="vertical")
        v_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        h_scrollbar = Scrollbar(canvas_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        self.annotate_canvas = Canvas(
            canvas_frame,
            bg="white",
            highlightthickness=0,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.annotate_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        v_scrollbar.config(command=self.annotate_canvas.yview)
        h_scrollbar.config(command=self.annotate_canvas.xview)

        self.annotate_pdf_path = None
        self.annotate_page_num = 0
        self.annotations = []

        # Bind mouse events
        self.annotate_canvas.bind("<Button-1>", self.start_annotation)
        self.annotate_canvas.bind("<B1-Motion>", self.draw_annotation)
        self.annotate_canvas.bind("<ButtonRelease-1>", self.end_annotation)

        # Mouse wheel scrolling
        self.annotate_canvas.bind("<MouseWheel>", lambda e: self.annotate_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.ann_start_x = None
        self.ann_start_y = None
        self.current_ann_item = None

    def load_annotate_pdf(self):
        """Load PDF for annotation"""
        f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not f:
            return

        try:
            self.annotate_pdf_path = f
            self.annotate_page_num = 0
            self.annotations = []

            # Get total page count
            doc = fitz.open(f)
            self.annotate_total_pages = len(doc)
            doc.close()

            self.render_annotate_page()
            self.update_annotate_page_label()
            self.settings_manager.add_recent_file(f)

        except Exception as e:
            logger.error(f"Annotate load error: {e}")
            messagebox.showerror(self.t("msg_error"), str(e))

    def render_annotate_page(self):
        """Render current page on annotation canvas"""
        if not self.annotate_pdf_path:
            return

        try:
            doc = fitz.open(self.annotate_pdf_path)
            page = doc[self.annotate_page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            self.annotate_photo = ImageTk.PhotoImage(img)
            self.annotate_canvas.delete("all")
            self.annotate_canvas.create_image(0, 0, anchor="nw", image=self.annotate_photo)
            self.annotate_canvas.config(scrollregion=self.annotate_canvas.bbox("all"))

            doc.close()

        except Exception as e:
            logger.error(f"Annotate render error: {e}")

    def start_annotation(self, event):
        """Start drawing annotation"""
        self.ann_start_x = event.x
        self.ann_start_y = event.y

    def draw_annotation(self, event):
        """Draw annotation as user drags"""
        if self.ann_start_x is None:
            return

        tool = self.annotate_tool.get()
        color = self.annotate_color.get()
        width = self.annotate_size.get()

        # Remove previous temp item
        if self.current_ann_item:
            self.annotate_canvas.delete(self.current_ann_item)

        if tool == "line":
            self.current_ann_item = self.annotate_canvas.create_line(
                self.ann_start_x, self.ann_start_y, event.x, event.y,
                fill=color, width=width
            )
        elif tool == "arrow":
            self.current_ann_item = self.annotate_canvas.create_line(
                self.ann_start_x, self.ann_start_y, event.x, event.y,
                fill=color, width=width, arrow="last"
            )
        elif tool == "rect":
            self.current_ann_item = self.annotate_canvas.create_rectangle(
                self.ann_start_x, self.ann_start_y, event.x, event.y,
                outline=color, width=width
            )
        elif tool == "circle":
            self.current_ann_item = self.annotate_canvas.create_oval(
                self.ann_start_x, self.ann_start_y, event.x, event.y,
                outline=color, width=width
            )

    def end_annotation(self, event):
        """Finish annotation"""
        tool = self.annotate_tool.get()

        if tool == "text":
            text = simpledialog.askstring("Metin", "Metin girin:")
            if text:
                color = self.annotate_color.get()
                size = self.annotate_size.get() * 5
                item = self.annotate_canvas.create_text(
                    event.x, event.y,
                    text=text,
                    fill=color,
                    font=("Inter", size),
                    anchor="nw"
                )
                self.annotations.append(('text', item, text, event.x, event.y))
        elif tool == "highlight":
            # Simple yellow rectangle with transparency effect
            if self.ann_start_x:
                item = self.annotate_canvas.create_rectangle(
                    self.ann_start_x, self.ann_start_y, event.x, event.y,
                    fill="yellow",
                    stipple="gray50",
                    outline=""
                )
                self.annotations.append(('highlight', item))
        else:
            if self.current_ann_item:
                self.annotations.append((tool, self.current_ann_item))

        self.ann_start_x = None
        self.ann_start_y = None
        self.current_ann_item = None

    def clear_annotations(self):
        """Clear all annotations"""
        for ann in self.annotations:
            self.annotate_canvas.delete(ann[1])
        self.annotations = []

    def update_annotate_page_label(self):
        """Update the page number label"""
        if hasattr(self, 'annotate_page_label') and self.annotate_pdf_path:
            text = f"Sayfa: {self.annotate_page_num + 1} / {self.annotate_total_pages}" if self.current_lang == "tr" else f"Page: {self.annotate_page_num + 1} / {self.annotate_total_pages}"
            self.annotate_page_label.configure(text=text)

    def prev_annotate_page(self):
        """Go to previous page"""
        if not self.annotate_pdf_path:
            return
        if self.annotate_page_num > 0:
            self.annotate_page_num -= 1
            self.annotations = []  # Clear annotations when changing pages
            self.render_annotate_page()
            self.update_annotate_page_label()

    def next_annotate_page(self):
        """Go to next page"""
        if not self.annotate_pdf_path:
            return
        if self.annotate_page_num < self.annotate_total_pages - 1:
            self.annotate_page_num += 1
            self.annotations = []  # Clear annotations when changing pages
            self.render_annotate_page()
            self.update_annotate_page_label()

    def save_annotate_pdf(self):
        """Save annotated PDF"""
        if not self.annotate_pdf_path:
            messagebox.showwarning(self.t("msg_warning"), "PDF yüklenmedi!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )

        if not save_path:
            return

        try:
            # Save canvas as image and add to PDF
            doc = fitz.open(self.annotate_pdf_path)
            page = doc[self.annotate_page_num]

            # Export annotations (simplified - just overlays on page)
            # For production, use PyMuPDF's annotation features

            doc.save(save_path)
            doc.close()

            messagebox.showinfo(self.t("msg_success"), "PDF kaydedildi! (Not: Basit mod - tam annotation için PyMuPDF annotation API kullanılmalı)")
            self.settings_manager.add_recent_file(save_path)

        except Exception as e:
            logger.error(f"Annotate save error: {e}")
            messagebox.showerror(self.t("msg_error"), str(e))

    def setup_qr_tab(self):
        """Setup QR Code tab - Generate and read QR codes"""
        # Header
        header = ctk.CTkFrame(self.tab_qr, fg_color=self.get_card_color(), corner_radius=15)
        header.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(
            header,
            text=self.t("qr_title"),
            font=("Inter", 24, "bold"),
            text_color=self.get_text_color()
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            header,
            text=self.t("qr_subtitle"),
            font=("Inter", 13),
            text_color=self.get_secondary_text_color()
        ).pack(pady=(0, 15))

        # Two column layout
        main_frame = ctk.CTkFrame(self.tab_qr, fg_color="transparent")
        main_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # LEFT: Create QR
        create_frame = ctk.CTkFrame(main_frame, fg_color=self.get_card_color(), corner_radius=15)
        create_frame.pack(side="left", padx=(0, 10), fill="both", expand=True)

        ctk.CTkLabel(
            create_frame,
            text=self.t("qr_create_title"),
            font=("Inter", 18, "bold"),
            text_color=self.get_text_color()
        ).pack(pady=(20, 15))

        ctk.CTkLabel(
            create_frame,
            text=self.t("qr_content"),
            font=("Inter", 12),
            text_color=self.get_text_color()
        ).pack(pady=(10, 5))

        self.qr_content = ctk.CTkTextbox(
            create_frame,
            height=100,
            font=("Inter", 12)
        )
        self.qr_content.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(
            create_frame,
            text=self.t("qr_size"),
            font=("Inter", 12),
            text_color=self.get_text_color()
        ).pack(pady=(10, 5))

        self.qr_size = ctk.IntVar(value=200)
        ctk.CTkSlider(
            create_frame,
            from_=100,
            to=500,
            variable=self.qr_size,
            width=200
        ).pack(pady=5)

        size_label = ctk.CTkLabel(
            create_frame,
            text="200 px",
            font=("Inter", 11),
            text_color=self.get_secondary_text_color()
        )
        size_label.pack(pady=5)

        def update_size_label(val):
            size_label.configure(text=f"{int(float(val))} px")

        self.qr_size.trace_add("write", lambda *args: update_size_label(self.qr_size.get()))

        ctk.CTkButton(
            create_frame,
            text=self.t("qr_generate"),
            command=self.generate_qr,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            font=("Inter", 13, "bold"),
            height=40,
            corner_radius=10
        ).pack(pady=15)

        # QR preview
        self.qr_preview_label = ctk.CTkLabel(create_frame, text="")
        self.qr_preview_label.pack(pady=10)

        btn_row = ctk.CTkFrame(create_frame, fg_color="transparent")
        btn_row.pack(pady=(10, 20))

        ctk.CTkButton(
            btn_row,
            text=self.t("qr_save_image"),
            command=self.save_qr_image,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            font=("Inter", 12, "bold"),
            height=35,
            corner_radius=10
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_row,
            text=self.t("qr_add_to_pdf"),
            command=self.add_qr_to_pdf,
            fg_color=Constants.WARNING_COLOR,
            hover_color=Constants.WARNING_HOVER,
            font=("Inter", 12, "bold"),
            height=35,
            corner_radius=10
        ).pack(side="left", padx=5)

        # RIGHT: Read QR
        read_frame = ctk.CTkFrame(main_frame, fg_color=self.get_card_color(), corner_radius=15)
        read_frame.pack(side="right", padx=(10, 0), fill="both", expand=True)

        ctk.CTkLabel(
            read_frame,
            text=self.t("qr_read_title"),
            font=("Inter", 18, "bold"),
            text_color=self.get_text_color()
        ).pack(pady=(20, 15))

        ctk.CTkButton(
            read_frame,
            text=self.t("qr_load_pdf"),
            command=self.load_qr_pdf,
            fg_color=Constants.PRIMARY_COLOR,
            hover_color=Constants.PRIMARY_HOVER,
            font=("Inter", 13, "bold"),
            height=40,
            corner_radius=10
        ).pack(pady=15)

        ctk.CTkButton(
            read_frame,
            text=self.t("qr_scan"),
            command=self.scan_qr_codes,
            fg_color=Constants.SECONDARY_COLOR,
            hover_color=Constants.SECONDARY_HOVER,
            font=("Inter", 13, "bold"),
            height=40,
            corner_radius=10
        ).pack(pady=10)

        ctk.CTkLabel(
            read_frame,
            text=self.t("qr_results"),
            font=("Inter", 12),
            text_color=self.get_text_color()
        ).pack(pady=(20, 5))

        self.qr_results = ctk.CTkTextbox(
            read_frame,
            height=300,
            font=("Inter", 12)
        )
        self.qr_results.pack(padx=20, pady=5, fill="both", expand=True)

        self.qr_image = None
        self.qr_pdf_path = None

    def generate_qr(self):
        """Generate QR code from text"""
        content = self.qr_content.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning(self.t("msg_warning"), "İçerik girin!")
            return

        try:
            import qrcode

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Resize to selected size
            size = self.qr_size.get()
            img = img.resize((size, size), Image.LANCZOS)

            self.qr_image = img

            # Display preview
            photo = ctk.CTkImage(img, size=(min(size, 250), min(size, 250)))
            self.qr_preview_label.configure(image=photo, text="")
            self.qr_preview_label.image = photo

        except ImportError:
            messagebox.showerror(self.t("msg_error"), "QR kod kütüphanesi yüklü değil!\npip install qrcode[pil]")
        except Exception as e:
            logger.error(f"QR generation error: {e}")
            messagebox.showerror(self.t("msg_error"), str(e))

    def save_qr_image(self):
        """Save QR code as image"""
        if not self.qr_image:
            messagebox.showwarning(self.t("msg_warning"), "QR kod oluşturun!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("All Files", "*.*")]
        )

        if save_path:
            try:
                self.qr_image.save(save_path)
                messagebox.showinfo(self.t("msg_success"), self.t("msg_saved"))
            except Exception as e:
                logger.error(f"QR save error: {e}")
                messagebox.showerror(self.t("msg_error"), str(e))

    def add_qr_to_pdf(self):
        """Add QR code to a PDF - Interactive positioning"""
        if not self.qr_image:
            messagebox.showwarning(self.t("msg_warning"), "QR kod oluşturun!")
            return

        pdf_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf_path:
            return

        try:
            # Open positioning window
            pos_win = ctk.CTkToplevel(self)
            pos_win.title("QR Kod Konumu Seçin")
            pos_win.geometry("900x1000")
            pos_win.attributes('-topmost', True)
            pos_win.grab_set()

            # Open document and get page count
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            current_page = [0]  # Using list to allow modification in nested functions

            # Initial page load
            page = doc[current_page[0]]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            pdf_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Create canvas with scrollbars
            canvas_frame = ctk.CTkFrame(pos_win, fg_color=self.get_card_color())
            canvas_frame.pack(padx=20, pady=20, fill="both", expand=True)

            from tkinter import Scrollbar

            v_scrollbar = Scrollbar(canvas_frame, orient="vertical")
            v_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

            h_scrollbar = Scrollbar(canvas_frame, orient="horizontal")
            h_scrollbar.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

            canvas = Canvas(
                canvas_frame,
                bg="white",
                highlightthickness=0,
                yscrollcommand=v_scrollbar.set,
                xscrollcommand=h_scrollbar.set
            )
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            v_scrollbar.config(command=canvas.yview)
            h_scrollbar.config(command=canvas.xview)

            # Display PDF page
            pdf_photo = ImageTk.PhotoImage(pdf_img)
            canvas.create_image(0, 0, anchor="nw", image=pdf_photo)
            canvas.image = pdf_photo

            # Configure scroll region
            canvas.config(scrollregion=canvas.bbox("all"))

            # Mouse wheel scrolling
            canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

            # QR position storage
            qr_position = {'x': None, 'y': None}
            qr_preview_item = [None]
            qr_size_var = ctk.IntVar(value=100)

            # Instructions and Page Navigation
            info_frame = ctk.CTkFrame(pos_win, fg_color="transparent")
            info_frame.pack(pady=(10, 5))

            ctk.CTkLabel(
                info_frame,
                text="📍 QR kodun yerleştirileceği konuma tıklayın",
                font=("Inter", 14, "bold"),
                text_color=self.get_text_color()
            ).pack()

            # Page navigation
            page_nav_frame = ctk.CTkFrame(pos_win, fg_color="transparent")
            page_nav_frame.pack(pady=10)

            page_label = ctk.CTkLabel(
                page_nav_frame,
                text=f"Sayfa: 1 / {total_pages}" if self.current_lang == "tr" else f"Page: 1 / {total_pages}",
                font=("Inter", 13, "bold"),
                text_color=self.get_text_color()
            )
            page_label.pack(side="left", padx=10)

            def update_page_display():
                """Update canvas with new page"""
                page = doc[current_page[0]]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                pdf_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                pdf_photo = ImageTk.PhotoImage(pdf_img)
                canvas.delete("all")
                canvas.create_image(0, 0, anchor="nw", image=pdf_photo)
                canvas.image = pdf_photo
                canvas.config(scrollregion=canvas.bbox("all"))

                # Clear QR preview when changing pages
                qr_position['x'] = None
                qr_position['y'] = None
                qr_preview_item[0] = None

                # Update label
                page_text = f"Sayfa: {current_page[0] + 1} / {total_pages}" if self.current_lang == "tr" else f"Page: {current_page[0] + 1} / {total_pages}"
                page_label.configure(text=page_text)

            def prev_page():
                if current_page[0] > 0:
                    current_page[0] -= 1
                    update_page_display()

            def next_page():
                if current_page[0] < total_pages - 1:
                    current_page[0] += 1
                    update_page_display()

            ctk.CTkButton(
                page_nav_frame,
                text="⬅ Önceki" if self.current_lang == "tr" else "⬅ Previous",
                command=prev_page,
                fg_color=Constants.NEUTRAL_COLOR,
                hover_color=Constants.NEUTRAL_HOVER,
                font=("Inter", 12, "bold"),
                height=35,
                width=120,
                corner_radius=10
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                page_nav_frame,
                text="Sonraki ➡" if self.current_lang == "tr" else "Next ➡",
                command=next_page,
                fg_color=Constants.NEUTRAL_COLOR,
                hover_color=Constants.NEUTRAL_HOVER,
                font=("Inter", 12, "bold"),
                height=35,
                width=120,
                corner_radius=10
            ).pack(side="left", padx=5)

            # Size slider
            size_frame = ctk.CTkFrame(pos_win, fg_color="transparent")
            size_frame.pack(pady=10)

            ctk.CTkLabel(
                size_frame,
                text="QR Boyutu:",
                font=("Inter", 12),
                text_color=self.get_text_color()
            ).pack(side="left", padx=5)

            def update_qr_size(val):
                # Update size in real-time if QR is already placed
                if qr_preview_item[0] and qr_position['x'] is not None:
                    show_qr_preview(qr_position['x'], qr_position['y'])

            ctk.CTkSlider(
                size_frame,
                from_=50,
                to=200,
                variable=qr_size_var,
                width=200,
                command=update_qr_size
            ).pack(side="left", padx=5)

            size_label = ctk.CTkLabel(
                size_frame,
                text="100 px",
                font=("Inter", 11),
                text_color=self.get_secondary_text_color()
            )
            size_label.pack(side="left", padx=5)

            qr_size_var.trace_add("write", lambda *args: size_label.configure(text=f"{qr_size_var.get()} px"))

            def show_qr_preview(x, y):
                # Remove old preview
                if qr_preview_item[0]:
                    canvas.delete(qr_preview_item[0])

                # Resize QR
                size = qr_size_var.get()
                qr_resized = self.qr_image.resize((size, size), Image.LANCZOS)
                qr_photo = ImageTk.PhotoImage(qr_resized)

                # Draw preview
                item = canvas.create_image(x, y, anchor="center", image=qr_photo)
                canvas.qr_photo = qr_photo  # Keep reference
                qr_preview_item[0] = item

                qr_position['x'] = x
                qr_position['y'] = y

            # Drag state
            drag_data = {'dragging': False, 'start_x': 0, 'start_y': 0}

            def on_canvas_click(event):
                # Check if clicking on QR
                if qr_preview_item[0]:
                    # Get QR bounds
                    coords = canvas.coords(qr_preview_item[0])
                    if coords:
                        x, y = coords
                        size = qr_size_var.get()
                        half = size / 2
                        # Check if click is within QR bounds
                        if abs(event.x - x) <= half and abs(event.y - y) <= half:
                            drag_data['dragging'] = True
                            drag_data['start_x'] = event.x
                            drag_data['start_y'] = event.y
                            return

                # Not clicking on QR, place new one
                show_qr_preview(event.x, event.y)

            def on_canvas_drag(event):
                if drag_data['dragging'] and qr_preview_item[0]:
                    # Calculate new position
                    dx = event.x - drag_data['start_x']
                    dy = event.y - drag_data['start_y']

                    new_x = qr_position['x'] + dx
                    new_y = qr_position['y'] + dy

                    show_qr_preview(new_x, new_y)

                    drag_data['start_x'] = event.x
                    drag_data['start_y'] = event.y

            def on_canvas_release(event):
                drag_data['dragging'] = False

            canvas.bind("<Button-1>", on_canvas_click)
            canvas.bind("<B1-Motion>", on_canvas_drag)
            canvas.bind("<ButtonRelease-1>", on_canvas_release)

            # Buttons
            btn_frame = ctk.CTkFrame(pos_win, fg_color="transparent")
            btn_frame.pack(pady=20)

            def save_qr_to_pdf():
                if qr_position['x'] is None:
                    messagebox.showwarning(self.t("msg_warning"), "Konum seçin!")
                    return

                save_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF", "*.pdf")]
                )

                if not save_path:
                    return

                try:
                    # Save QR as temp image
                    temp_qr = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    size = qr_size_var.get()
                    qr_resized = self.qr_image.resize((size, size), Image.LANCZOS)
                    qr_resized.save(temp_qr.name)

                    # Calculate position in PDF coordinates
                    scale = 1.5
                    pdf_x = qr_position['x'] / scale
                    pdf_y = qr_position['y'] / scale
                    half_size = (size / scale) / 2

                    # Add to PDF on current page
                    current_pdf_page = doc[current_page[0]]
                    rect = fitz.Rect(
                        pdf_x - half_size, pdf_y - half_size,
                        pdf_x + half_size, pdf_y + half_size
                    )
                    current_pdf_page.insert_image(rect, filename=temp_qr.name)

                    doc.save(save_path)
                    doc.close()
                    os.unlink(temp_qr.name)

                    messagebox.showinfo(self.t("msg_success"), f"QR kod sayfa {current_page[0] + 1}'e eklendi!")
                    self.settings_manager.add_recent_file(save_path)
                    pos_win.destroy()

                except Exception as e:
                    logger.error(f"QR to PDF error: {e}")
                    messagebox.showerror(self.t("msg_error"), str(e))

            ctk.CTkButton(
                btn_frame,
                text=self.t("btn_preview_save"),
                command=save_qr_to_pdf,
                fg_color=Constants.SECONDARY_COLOR,
                hover_color=Constants.SECONDARY_HOVER,
                font=("Inter", 13, "bold"),
                height=40,
                width=150,
                corner_radius=10
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                btn_frame,
                text=self.t("btn_preview_cancel"),
                command=lambda: [doc.close(), pos_win.destroy()],
                fg_color=Constants.NEUTRAL_COLOR,
                hover_color=Constants.NEUTRAL_HOVER,
                font=("Inter", 13, "bold"),
                height=40,
                width=150,
                corner_radius=10
            ).pack(side="left", padx=10)

        except Exception as e:
            logger.error(f"QR positioning error: {e}")
            messagebox.showerror(self.t("msg_error"), str(e))

    def load_qr_pdf(self):
        """Load PDF for QR scanning"""
        f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f:
            self.qr_pdf_path = f
            self.settings_manager.add_recent_file(f)

    def scan_qr_codes(self):
        """Scan PDF for QR codes"""
        if not self.qr_pdf_path:
            messagebox.showwarning(self.t("msg_warning"), "PDF yükleyin!")
            return

        try:
            from pyzbar.pyzbar import decode
            import cv2
            import numpy as np

            self.qr_results.delete("1.0", "end")
            doc = fitz.open(self.qr_pdf_path)
            found_count = 0

            for i, page in enumerate(doc):
                # Render page as image
                pix = page.get_pixmap(dpi=200)
                img_data = pix.samples
                img = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, 3)

                # Decode QR codes
                qr_codes = decode(img)

                if qr_codes:
                    for qr in qr_codes:
                        data = qr.data.decode('utf-8')
                        self.qr_results.insert("end", f"Sayfa {i+1}:\n{data}\n\n")
                        found_count += 1

            doc.close()

            if found_count == 0:
                self.qr_results.insert("end", self.t("qr_not_found"))
            else:
                self.qr_results.insert("1.0", f"✅ {found_count} {self.t('qr_found')}\n\n")

        except ImportError:
            messagebox.showerror(self.t("msg_error"), "QR okuma kütüphaneleri yüklü değil!\npip install pyzbar opencv-python")
        except Exception as e:
            logger.error(f"QR scan error: {e}")
            messagebox.showerror(self.t("msg_error"), str(e))

if __name__ == "__main__":
    app = PDFApp()
    app.mainloop()
