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

# --- DİL SÖZLÜĞÜ ---
TEXTS = {
    "app_title": {"tr": "Süper PDF Stüdyosu - V2.6 (Text & Metadata)", "en": "Super PDF Studio - V2.6 (Text & Metadata)"},
    "header": {"tr": "PDF Ofis Stüdyosu", "en": "PDF Office Studio"},
    "hint": {"tr": "💡 İpucu: Dosyaları pencereye sürükleyebilirsiniz!", "en": "💡 Hint: You can drag & drop files here!"},
    
    # Sekmeler
    "tab_jpg": {"tr": "JPG > PDF", "en": "JPG to PDF"},
    "tab_word": {"tr": "Word > PDF", "en": "Word to PDF"},
    "tab_pdf2img": {"tr": "PDF > Resim", "en": "PDF to Image"},
    "tab_pdf2txt": {"tr": "PDF > Metin", "en": "PDF to Text"}, # YENİ
    "tab_merge": {"tr": "PDF Birleştir", "en": "Merge PDF"},
    "tab_split": {"tr": "PDF Ayrıştır", "en": "Split PDF"},
    "tab_compress": {"tr": "PDF Sıkıştır", "en": "Compress PDF"},
    "tab_sign": {"tr": "Kaşe & İmza", "en": "Stamp & Sign"},
    "tab_tools": {"tr": "Güvenlik & Araçlar", "en": "Security & Tools"},
    
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
    "page": {"tr": "Sayfa", "en": "Page"}
}

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PDFApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.current_lang = "tr"
        self.current_theme = "System"
        
        # Ekran Ayarı
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = int(sw*0.85), int(sh*0.85)
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")

        # Veriler
        self.merge_cards = []
        self.merge_selected_index = -1
        self.split_file_path = None
        self.split_pages_data = []
        self.compress_file_path = None
        self.pdf2img_file_path = None
        self.pdf2txt_file_path = None # YENİ
        
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

        self.create_ui_elements()
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event_handler)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def t(self, key): return TEXTS.get(key, {}).get(self.current_lang, key)
    
    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "tr" else "tr"
        self.create_ui_elements()
        if self.sign_images: self.refresh_signature_library()
        if self.merge_cards: self.refresh_merge_gallery()

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text="🌙")
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text="☀️")

    def create_ui_elements(self):
        for widget in self.winfo_children(): widget.destroy()
        self.title(self.t("app_title"))
        h_frame = ctk.CTkFrame(self, fg_color="transparent")
        h_frame.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(h_frame, text=self.t("header"), font=("Roboto", 24, "bold")).pack(side="left", expand=True)
        btn_frame = ctk.CTkFrame(h_frame, fg_color="transparent"); btn_frame.pack(side="right")
        theme_icon = "☀️" if ctk.get_appearance_mode() == "Dark" else "🌙"
        self.btn_theme = ctk.CTkButton(btn_frame, text=theme_icon, width=40, command=self.toggle_theme, fg_color="#444"); self.btn_theme.pack(side="left", padx=5)
        txt = "🇹🇷 TR" if self.current_lang == "en" else "🇬🇧 EN"
        ctk.CTkButton(btn_frame, text=txt, width=60, command=self.toggle_language, fg_color="#555").pack(side="left")
        ctk.CTkLabel(self, text=self.t("hint"), text_color="#4a90e2").pack(pady=0)

        self.tabview = ctk.CTkTabview(self, width=1150, height=700)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_jpg = self.tabview.add(self.t("tab_jpg"))
        self.tab_word = self.tabview.add(self.t("tab_word"))
        self.tab_pdf2img = self.tabview.add(self.t("tab_pdf2img"))
        self.tab_pdf2txt = self.tabview.add(self.t("tab_pdf2txt")) # YENİ
        self.tab_merge = self.tabview.add(self.t("tab_merge"))
        self.tab_split = self.tabview.add(self.t("tab_split"))
        self.tab_compress = self.tabview.add(self.t("tab_compress"))
        self.tab_sign = self.tabview.add(self.t("tab_sign"))
        self.tab_tools = self.tabview.add(self.t("tab_tools"))

        self.setup_jpg_tab(); self.setup_word_tab(); self.setup_merge_tab()
        self.setup_split_tab(); self.setup_compress_tab(); self.setup_sign_tab()
        self.setup_tools_tab(); self.setup_pdf2img_tab(); self.setup_pdf2txt_tab()

    def on_closing(self):
        for t in self.temp_image_files:
            try: os.remove(t)
            except: pass
        self.quit()

    def drop_event_handler(self, event):
        raw = event.data
        if raw.startswith('{') and raw.endswith('}'): files = [f.strip('{}') for f in raw.split('} {')]
        else: files = raw.split()
        act = self.tabview.get()
        f0 = files[0] if files else None
        
        if act == self.t("tab_jpg"): self.convert_dropped_jpgs(files)
        elif act == self.t("tab_word"): self.convert_dropped_word(f0)
        elif act == self.t("tab_pdf2img"): self.load_pdf2img_file(f0)
        elif act == self.t("tab_pdf2txt"): self.load_pdf2txt_file(f0) # YENİ
        elif act == self.t("tab_merge"): self.add_merge_pdf_from_list(files)
        elif act == self.t("tab_split"): self.load_split_pdf_path(f0)
        elif act == self.t("tab_compress"): self.load_compress_pdf(f0)
        elif act == self.t("tab_sign"): self.load_sign_pdf(f0)
        elif act == self.t("tab_tools"): self.load_tools_pdf(f0)

    # --- MEVCUTLAR (KISALTILMIŞ) ---
    def setup_jpg_tab(self):
        ctk.CTkLabel(self.tab_jpg, text=self.t("jpg_label"), font=("Arial", 14)).pack(pady=20)
        ctk.CTkButton(self.tab_jpg, text=self.t("btn_select_img"), command=self.convert_jpg_to_pdf).pack(pady=10)
    def convert_jpg_to_pdf(self):
        fs = filedialog.askopenfilenames(filetypes=[("IMG", "*.jpg;*.png")])
        if fs: self.convert_dropped_jpgs(list(fs))
    def convert_dropped_jpgs(self, fs):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s: 
            with open(s, "wb") as f: f.write(img2pdf.convert(fs))
            messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
    def setup_word_tab(self):
        ctk.CTkLabel(self.tab_word, text=self.t("word_label"), font=("Arial", 14)).pack(pady=20)
        ctk.CTkButton(self.tab_word, text=self.t("btn_select_word"), command=self.convert_word_to_pdf, fg_color="green").pack(pady=10)
    def convert_word_to_pdf(self):
        f = filedialog.askopenfilename(filetypes=[("Word", "*.docx")])
        if f: self.convert_dropped_word(f)
    def convert_dropped_word(self, f):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            pythoncom.CoInitialize(); w = win32com.client.Dispatch("Word.Application"); w.Visible = False
            d = w.Documents.Open(os.path.abspath(f)); d.SaveAs(os.path.abspath(s), FileFormat=17)
            d.Close(); w.Quit(); pythoncom.CoUninitialize(); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))

    # --- PDF TO IMAGE ---
    def setup_pdf2img_tab(self):
        for w in self.tab_pdf2img.winfo_children(): w.destroy()
        f = ctk.CTkFrame(self.tab_pdf2img); f.pack(fill="both", expand=True, padx=50, pady=50)
        ctk.CTkLabel(f, text=self.t("p2i_title"), font=("Arial", 20, "bold")).pack(pady=20)
        fr = ctk.CTkFrame(f, fg_color="transparent"); fr.pack(pady=10)
        ctk.CTkButton(fr, text=self.t("btn_select"), command=self.select_pdf2img_file).pack(side="left", padx=5)
        if self.pdf2img_file_path: ctk.CTkButton(fr, text="X", width=30, fg_color="red", command=self.clear_pdf2img_file).pack(side="left", padx=5)
        txt = os.path.basename(self.pdf2img_file_path) if self.pdf2img_file_path else self.t("lbl_no_file")
        self.lbl_pdf2img_file = ctk.CTkLabel(f, text=txt, text_color="gray"); self.lbl_pdf2img_file.pack()
        ctk.CTkLabel(f, text=self.t("lbl_dpi"), font=("Arial", 12)).pack(pady=(20, 5))
        self.p2i_slider = ctk.CTkSlider(f, from_=100, to=300, number_of_steps=4); self.p2i_slider.set(150); self.p2i_slider.pack(pady=5)
        state = "normal" if self.pdf2img_file_path else "disabled"
        ctk.CTkButton(f, text=self.t("btn_convert_jpg"), state=state, fg_color="green", command=self.start_pdf2img, height=40).pack(pady=30)
    def select_pdf2img_file(self): self.load_pdf2img_file(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_pdf2img_file(self, f):
        if not f: return
        self.pdf2img_file_path = f; self.setup_pdf2img_tab()
    def clear_pdf2img_file(self): self.pdf2img_file_path = None; self.setup_pdf2img_tab()
    def start_pdf2img(self):
        if not self.pdf2img_file_path: return
        folder = filedialog.askdirectory()
        if not folder: return
        try:
            doc = fitz.open(self.pdf2img_file_path); dpi = int(self.p2i_slider.get())
            base_name = os.path.splitext(os.path.basename(self.pdf2img_file_path))[0]
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                out_path = os.path.join(folder, f"{base_name}_page_{i+1}.jpg")
                pix.save(out_path)
            messagebox.showinfo(self.t("msg_success"), f"{len(doc)} {self.t('msg_done')}\n{folder}")
        except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    # --- YENİ: PDF TO TEXT (METİN ÇIKARMA) ---
    def setup_pdf2txt_tab(self):
        for w in self.tab_pdf2txt.winfo_children(): w.destroy()
        f = ctk.CTkFrame(self.tab_pdf2txt); f.pack(fill="both", expand=True, padx=50, pady=50)
        ctk.CTkLabel(f, text=self.t("p2t_title"), font=("Arial", 20, "bold")).pack(pady=20)
        
        fr = ctk.CTkFrame(f, fg_color="transparent"); fr.pack(pady=10)
        ctk.CTkButton(fr, text=self.t("btn_select"), command=self.select_pdf2txt_file).pack(side="left", padx=5)
        if self.pdf2txt_file_path: ctk.CTkButton(fr, text="X", width=30, fg_color="red", command=self.clear_pdf2txt_file).pack(side="left", padx=5)
        
        txt = os.path.basename(self.pdf2txt_file_path) if self.pdf2txt_file_path else self.t("lbl_no_file")
        self.lbl_pdf2txt_file = ctk.CTkLabel(f, text=txt, text_color="gray"); self.lbl_pdf2txt_file.pack()
        
        state = "normal" if self.pdf2txt_file_path else "disabled"
        ctk.CTkButton(f, text=self.t("btn_convert_txt"), state=state, fg_color="green", command=self.start_pdf2txt, height=40).pack(pady=30)
    
    def select_pdf2txt_file(self): self.load_pdf2txt_file(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_pdf2txt_file(self, f):
        if not f: return
        self.pdf2txt_file_path = f; self.setup_pdf2txt_tab()
    def clear_pdf2txt_file(self): self.pdf2txt_file_path = None; self.setup_pdf2txt_tab()
    
    def start_pdf2txt(self):
        if not self.pdf2txt_file_path: return
        s = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
        if not s: return
        try:
            doc = fitz.open(self.pdf2txt_file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n\n"
            
            with open(s, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
        except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    # --- MERGE ---
    def setup_merge_tab(self):
        f = ctk.CTkFrame(self.tab_merge, fg_color="transparent"); f.pack(fill="x", padx=10)
        ctk.CTkButton(f, text=self.t("btn_add"), width=80, command=self.add_merge_pdf).pack(side="left")
        ctk.CTkButton(f, text=self.t("btn_del"), width=80, fg_color="#d32f2f", command=self.remove_merge_pdf).pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t("btn_clear_all"), width=80, fg_color="#555", command=self.clear_all_merge).pack(side="left", padx=5)
        ctk.CTkButton(f, text="<", width=40, command=self.move_merge_left).pack(side="left", padx=5)
        ctk.CTkButton(f, text=">", width=40, command=self.move_merge_right).pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t("btn_merge"), fg_color="green", command=self.merge_execute).pack(side="right")
        self.merge_gallery = ctk.CTkScrollableFrame(self.tab_merge, orientation="horizontal", height=250); self.merge_gallery.pack(fill="both", expand=True, padx=10)
        if self.merge_cards: self.refresh_merge_gallery()
    def add_merge_pdf(self): self.add_merge_pdf_from_list(filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")]))
    def add_merge_pdf_from_list(self, fs):
        for f in fs:
            try:
                doc = fitz.open(f); pix = doc[0].get_pixmap(matrix=fitz.Matrix(0.15, 0.15))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.merge_cards.append({'path': f, 'thumb': ctk.CTkImage(img, size=(100, 140))})
            except: pass
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
    def merge_execute(self):
        if len(self.merge_cards) < 2: messagebox.showwarning(self.t("msg_error"), "2+ dosya gerekli"); return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                m = PdfWriter(); [m.append(c['path']) for c in self.merge_cards]; m.write(s); m.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    def setup_split_tab(self):
        f = ctk.CTkFrame(self.tab_split, fg_color="transparent"); f.pack(fill="x", padx=10)
        ctk.CTkButton(f, text=self.t("btn_load"), command=self.load_split_pdf).pack(side="left")
        ctk.CTkButton(f, text=self.t("btn_reset"), width=80, fg_color="#555", command=self.deselect_all_split).pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t("btn_close"), width=80, fg_color="#d32f2f", command=self.clear_split_tab).pack(side="left", padx=5)
        ctk.CTkLabel(f, text=self.t("lbl_rotate"), text_color="gray").pack(side="left", padx=5)
        ctk.CTkButton(f, text="⟲", width=40, command=lambda: self.rotate_pages(90)).pack(side="left", padx=2)
        ctk.CTkButton(f, text="⟳", width=40, command=lambda: self.rotate_pages(-90)).pack(side="left", padx=2)
        txt = os.path.basename(self.split_file_path) if self.split_file_path else ""
        self.lbl_split_info = ctk.CTkLabel(f, text=txt, text_color="gray"); self.lbl_split_info.pack(side="left", padx=10)
        ctk.CTkButton(f, text=self.t("btn_save_sel"), fg_color="orange", command=self.save_selected_pages).pack(side="right")
        self.split_scroll = ctk.CTkScrollableFrame(self.tab_split); self.split_scroll.pack(fill="both", expand=True, padx=10)
        if self.split_pages_data:
            for i, d in enumerate(self.split_pages_data): self.create_split_widget(i, d)
    def load_split_pdf(self): self.load_split_pdf_path(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_split_pdf_path(self, f):
        if not f: return
        self.split_file_path = f; self.split_pages_data = []; self.lbl_split_info.configure(text=os.path.basename(f))
        for w in self.split_scroll.winfo_children(): w.destroy()
        try:
            doc = fitz.open(f)
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(0.15, 0.15)); pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                d = {'page_num': i, 'image_ctk': ctk.CTkImage(pil, size=(100, 140)), 'image_pil': pil, 'selected': False, 'widget': None, 'rotation': 0}
                self.split_pages_data.append(d); self.create_split_widget(i, d)
        except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))
    def clear_split_tab(self): self.split_file_path = None; self.lbl_split_info.configure(text=""); self.split_pages_data = []; [w.destroy() for w in self.split_scroll.winfo_children()]
    def deselect_all_split(self):
        for i, d in enumerate(self.split_pages_data):
            if d['selected']: self.toggle_split_sel(i)
    def create_split_widget(self, i, d):
        fr = ctk.CTkFrame(self.split_scroll, width=120, height=180, border_width=2, border_color="gray", fg_color="transparent")
        fr.grid(row=i//6, column=i%6, padx=5, pady=5); d['widget'] = fr
        lbl = ctk.CTkLabel(fr, text="", image=d['image_ctk']); lbl.pack(pady=5)
        num = ctk.CTkLabel(fr, text=f"{self.t('page')} {i+1}", font=("Arial", 11, "bold")); num.pack()
        for w in [fr, lbl, num]: w.bind("<Button-1>", lambda e, x=i: self.toggle_split_sel(x))
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
        f = ctk.CTkFrame(self.tab_compress); f.pack(fill="both", expand=True, padx=50, pady=50)
        ctk.CTkLabel(f, text=self.t("lbl_compress_title"), font=("Arial", 20, "bold")).pack(pady=20)
        fr = ctk.CTkFrame(f, fg_color="transparent"); fr.pack(pady=10)
        ctk.CTkButton(fr, text=self.t("btn_select"), command=self.select_compress_pdf).pack(side="left", padx=5)
        if self.compress_file_path: ctk.CTkButton(fr, text="X", width=30, fg_color="red", command=self.clear_compress_file).pack(side="left", padx=5)
        txt = os.path.basename(self.compress_file_path) if self.compress_file_path else ""
        self.lbl_compress_file = ctk.CTkLabel(f, text=txt, text_color="gray"); self.lbl_compress_file.pack()
        self.compress_slider = ctk.CTkSlider(f, from_=0.2, to=1.0, number_of_steps=8, command=self.on_compress_slider); self.compress_slider.set(0.6); self.compress_slider.pack(pady=10)
        self.lbl_quality_value = ctk.CTkLabel(f, text="Quality: %60", font=("Arial", 12)); self.lbl_quality_value.pack()
        state = "normal" if self.compress_file_path else "disabled"
        ctk.CTkButton(f, text=self.t("btn_compress"), state=state, fg_color="green", command=self.start_compression).pack(pady=20)
        if self.compress_file_path: self.update_compress_ui_info()
    def on_compress_slider(self, val): self.lbl_quality_value.configure(text=f"Quality: %{int(val*100)}")
    def select_compress_pdf(self): self.load_compress_pdf(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_compress_pdf(self, f): 
        if not f: return
        self.compress_file_path = f; self.setup_compress_tab()
    def update_compress_ui_info(self):
        sz = os.path.getsize(self.compress_file_path) / (1024*1024)
        self.lbl_compress_file.configure(text=f"{os.path.basename(self.compress_file_path)} ({sz:.2f} MB)")
    def clear_compress_file(self): self.compress_file_path = None; self.setup_compress_tab()
    def start_compression(self):
        if not self.compress_file_path: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            qv = self.compress_slider.get(); dpi = int(72 + (qv * 150)); jq = int(qv * 80)
            try:
                doc = fitz.open(self.compress_file_path); lst = []
                for i in range(len(doc)):
                    pix = doc[i].get_pixmap(dpi=dpi, alpha=False); img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    b = io.BytesIO(); img.save(b, format='JPEG', quality=jq, optimize=True); lst.append(b.getvalue())
                with open(s, "wb") as f: f.write(img2pdf.convert(lst))
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    def setup_sign_tab(self):
        lp = ctk.CTkFrame(self.tab_sign, width=250); lp.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(lp, text=self.t("lbl_lib"), font=("Arial", 14)).pack(pady=10)
        ctk.CTkButton(lp, text=self.t("btn_add_sign"), command=self.add_signature_image).pack(pady=5)
        ctk.CTkLabel(lp, text=self.t("lbl_sign_size"), font=("Arial", 12)).pack(pady=(15, 5))
        self.sign_size_slider = ctk.CTkSlider(lp, from_=0.5, to=2.0, number_of_steps=15); self.sign_size_slider.set(1.0); self.sign_size_slider.pack(pady=5)
        self.sign_scroll = ctk.CTkScrollableFrame(lp); self.sign_scroll.pack(fill="both", expand=True, pady=10)
        rp = ctk.CTkFrame(self.tab_sign); rp.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        tc = ctk.CTkFrame(rp, fg_color="transparent"); tc.pack(fill="x", pady=5)
        ctk.CTkButton(tc, text=self.t("btn_load"), command=self.open_sign_pdf).pack(side="left")
        ctk.CTkButton(tc, text=self.t("btn_close"), width=50, fg_color="#d32f2f", command=self.close_sign_pdf).pack(side="left", padx=5)
        ctk.CTkButton(tc, text="<", width=40, command=self.prev_sign_page).pack(side="left", padx=5)
        self.lbl_sign_page = ctk.CTkLabel(tc, text="0/0"); self.lbl_sign_page.pack(side="left", padx=5)
        ctk.CTkButton(tc, text=">", width=40, command=self.next_sign_page).pack(side="left", padx=5)
        ctk.CTkButton(tc, text=self.t("btn_preview"), width=80, fg_color="#1f538d", command=self.preview_signed_page).pack(side="right", padx=10)
        ctk.CTkButton(tc, text=self.t("btn_save_sel"), fg_color="green", command=self.save_signed_pdf).pack(side="right")
        ctk.CTkButton(tc, text=self.t("btn_undo"), fg_color="#d32f2f", command=self.undo_last_stamp).pack(side="right", padx=5)
        self.canvas_container = ctk.CTkFrame(rp); self.canvas_container.pack(fill="both", expand=True, pady=5)
        self.v_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="vertical")
        self.h_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="horizontal")
        self.sign_canvas = Canvas(self.canvas_container, bg="gray", bd=0, highlightthickness=0, yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.v_scroll.configure(command=self.sign_canvas.yview); self.h_scroll.configure(command=self.sign_canvas.xview)
        self.v_scroll.pack(side="right", fill="y"); self.h_scroll.pack(side="bottom", fill="x"); self.sign_canvas.pack(side="left", fill="both", expand=True)
        self.sign_canvas.bind("<ButtonPress-1>", self.on_canvas_press); self.sign_canvas.bind("<B1-Motion>", self.on_canvas_drag); self.sign_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        if self.sign_images: self.refresh_signature_library()
        if self.sign_doc: self.show_current_sign_page()
    def make_image_transparent(self, pil_img):
        pil_img = pil_img.convert("RGBA"); datas = pil_img.getdata(); new_data = []
        for item in datas:
            if item[0]>200 and item[1]>200 and item[2]>200: new_data.append((255,255,255,0))
            else: new_data.append(item)
        pil_img.putdata(new_data); return pil_img
    def add_signature_image(self):
        path = filedialog.askopenfilename(filetypes=[("IMG", "*.png;*.jpg")])
        if not path: return
        try:
            pil = self.make_image_transparent(Image.open(path))
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); pil.save(t.name); t.close()
            self.temp_image_files.append(t.name); self.sign_images.append({'path': t.name, 'pil': pil})
            self.refresh_signature_library()
        except: pass
    def refresh_signature_library(self):
        for w in self.sign_scroll.winfo_children(): w.destroy()
        for i, item in enumerate(self.sign_images):
            thumb = item['pil'].copy(); thumb.thumbnail((100, 100))
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
        ms = ctk.CTkScrollableFrame(self.tab_tools, fg_color="transparent"); ms.pack(fill="both", expand=True, padx=10, pady=10)
        fr = ctk.CTkFrame(ms); fr.pack(fill="x", pady=10, padx=10)
        ctk.CTkButton(fr, text=self.t("btn_select"), command=self.load_tools_pdf).pack(side="left", padx=10, pady=10)
        txt = os.path.basename(self.tools_file_path) if self.tools_file_path else self.t("lbl_no_file")
        self.lbl_tools_file = ctk.CTkLabel(fr, text=txt, text_color="gray", font=("Arial", 12, "bold")); self.lbl_tools_file.pack(side="left", padx=10)
        if self.tools_file_path: ctk.CTkButton(fr, text="X", width=30, fg_color="red", command=self.clear_tools_file).pack(side="right", padx=10)
        
        # Şifreleme
        f1 = ctk.CTkFrame(ms); f1.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f1, text=self.t("tool_encrypt_title"), font=("Arial", 16, "bold")).pack(pady=5)
        ep = ctk.CTkEntry(f1, placeholder_text=self.t("lbl_password"), show="*"); ep.pack(pady=5)
        ctk.CTkButton(f1, text=self.t("btn_apply"), fg_color="#1f538d", command=lambda: self.tool_encrypt(ep.get())).pack(pady=10)
        
        # Filigran
        f2 = ctk.CTkFrame(ms); f2.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f2, text=self.t("tool_watermark_title"), font=("Arial", 16, "bold")).pack(pady=5)
        we = ctk.CTkEntry(f2, placeholder_text=self.t("lbl_watermark_text")); we.pack(pady=5)
        wc = ctk.CTkComboBox(f2, values=["Red", "Blue", "Gray", "Black"]); wc.set("Red"); wc.pack(pady=5)
        ctk.CTkButton(f2, text=self.t("btn_apply"), fg_color="#e67e22", command=lambda: self.tool_watermark(we.get(), wc.get())).pack(pady=10)
        
        # Sayfa Numarası
        f3 = ctk.CTkFrame(ms); f3.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f3, text=self.t("tool_page_num_title"), font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkButton(f3, text=self.t("btn_apply"), fg_color="green", command=self.tool_add_page_numbers).pack(pady=10)
        
        # YENİ: Meta Veri Düzenleme
        f4 = ctk.CTkFrame(ms); f4.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f4, text=self.t("tool_metadata_title"), font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(f4, text=self.t("lbl_meta_title")).pack(pady=2)
        meta_title = ctk.CTkEntry(f4); meta_title.pack(pady=2)
        ctk.CTkLabel(f4, text=self.t("lbl_meta_author")).pack(pady=2)
        meta_author = ctk.CTkEntry(f4); meta_author.pack(pady=2)
        ctk.CTkButton(f4, text=self.t("btn_apply"), fg_color="#555", command=lambda: self.tool_metadata(meta_title.get(), meta_author.get())).pack(pady=10)

    def load_tools_pdf(self, f=None):
        if not f: f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f: self.tools_file_path = f; self.setup_tools_tab()
    def clear_tools_file(self): self.tools_file_path = None; self.setup_tools_tab()
    def tool_encrypt(self, password):
        if not self.tools_file_path or not password: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                doc = fitz.open(self.tools_file_path); doc.save(s, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=password, owner_pw=password); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))
    def tool_watermark(self, text, color_name):
        if not self.tools_file_path or not text: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                doc = fitz.open(self.tools_file_path)
                colors = {"Red": (1, 0, 0), "Blue": (0, 0, 1), "Gray": (0.5, 0.5, 0.5), "Black": (0, 0, 0)}; rgb = colors.get(color_name, (0,0,0))
                windir = os.environ.get("WINDIR", "C:/Windows"); font_path = os.path.join(windir, "Fonts", "arial.ttf")
                used_fontname = "helv"; font_buffer = None
                if os.path.exists(font_path):
                    try:
                        with open(font_path, "rb") as f: font_buffer = f.read()
                        fitz.Font(fontbuffer=font_buffer); used_fontname = "arial_tr"
                    except: pass
                fontsize = 50
                calc_font = fitz.Font(fontbuffer=font_buffer) if font_buffer else fitz.Font("helv")
                text_len = calc_font.text_length(text, fontsize)
                for page in doc:
                    if font_buffer and used_fontname == "arial_tr":
                        try: page.insert_font(fontname=used_fontname, fontbuffer=font_buffer)
                        except: used_fontname = "helv"
                    w, h = page.rect.width, page.rect.height; center = fitz.Point(w/2, h/2)
                    p_start = fitz.Point(center.x - text_len/2, center.y + fontsize/4); mat = fitz.Matrix(45)
                    try: page.insert_text(p_start, text, fontsize=fontsize, fontname=used_fontname, color=rgb, fill_opacity=0.3, morph=(center, mat))
                    except: page.insert_text(p_start, text, fontsize=fontsize, fontname="helv", color=rgb, fill_opacity=0.3, morph=(center, mat))
                doc.save(s); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))
    def tool_add_page_numbers(self):
        if not self.tools_file_path: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                doc = fitz.open(self.tools_file_path); total = len(doc)
                for i, page in enumerate(doc):
                    w, h = page.rect.width, page.rect.height; text = f"{i+1} / {total}"
                    page.insert_text((w/2 - 10, h - 20), text, fontsize=12, color=(0,0,0))
                doc.save(s); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))
            
    # YENİ: METADATA DÜZENLEME
    def tool_metadata(self, title, author):
        if not self.tools_file_path: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                doc = fitz.open(self.tools_file_path)
                meta = doc.metadata
                if title: meta["title"] = title
                if author: meta["author"] = author
                doc.set_metadata(meta)
                doc.save(s)
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

if __name__ == "__main__":
    app = PDFApp()
    app.mainloop()
