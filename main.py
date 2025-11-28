import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
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
import datetime # Sohbet zamanı için

# --- DİL SÖZLÜĞÜ ---
TEXTS = {
    "app_title": {"tr": "Süper PDF Stüdyosu - Ultimate V1.5 (Smart AI)", "en": "Super PDF Studio - Ultimate V1.5 (Smart AI)"},
    "header": {"tr": "PDF Ofis Stüdyosu", "en": "PDF Office Studio"},
    "hint": {"tr": "💡 İpucu: Dosyaları pencereye sürükleyebilirsiniz!", "en": "💡 Hint: You can drag & drop files here!"},
    "tab_jpg": {"tr": "JPG > PDF", "en": "JPG to PDF"},
    "tab_word": {"tr": "Word > PDF", "en": "Word to PDF"},
    "tab_merge": {"tr": "PDF Birleştir", "en": "Merge PDF"},
    "tab_split": {"tr": "PDF Ayrıştır/Döndür", "en": "Split/Rotate PDF"},
    "tab_compress": {"tr": "PDF Sıkıştır", "en": "Compress PDF"},
    "tab_sign": {"tr": "Kaşe & İmza", "en": "Stamp & Sign"},
    "tab_ai": {"tr": "AI Asistan 🤖", "en": "AI Assistant 🤖"},
    
    "btn_select": {"tr": "Seç", "en": "Select"},
    "btn_remove": {"tr": "Kaldır", "en": "Remove"},
    "btn_close_file": {"tr": "Dosyayı Kapat", "en": "Close File"},
    "btn_clear_all": {"tr": "Tümünü Temizle", "en": "Clear All"},
    "jpg_label": {"tr": "JPG Seç/Sürükle", "en": "Select/Drag JPG"},
    "btn_select_img": {"tr": "Resim Seç", "en": "Select Image"},
    "msg_success": {"tr": "Başarılı", "en": "Success"},
    "msg_done": {"tr": "İşlem Tamamlandı!", "en": "Operation Completed!"},
    "msg_error": {"tr": "Hata", "en": "Error"},
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
    "btn_clear": {"tr": "Temizle", "en": "Clear"},
    "lbl_rotate": {"tr": "| Çevir:", "en": "| Rotate:"},
    "btn_save_sel": {"tr": "Kaydet", "en": "Save"},
    "lbl_pages": {"tr": "Sayfalar", "en": "Pages"},
    "warn_no_sel": {"tr": "Sayfa seçmediniz!", "en": "No pages selected!"},
    "lbl_compress_title": {"tr": "SIKIŞTIRMA", "en": "COMPRESSION"},
    "btn_compress": {"tr": "SIKIŞTIR VE KAYDET", "en": "COMPRESS AND SAVE"},
    "msg_compressed": {"tr": "Sıkıştırıldı!", "en": "Compressed!"},
    "lbl_lib": {"tr": "İmza Kütüphanesi", "en": "Signature Lib"},
    "btn_add_sign": {"tr": "+ Kaşe/İmza Ekle", "en": "+ Add Stamp/Sign"},
    "btn_preview": {"tr": "🔍 Önizle", "en": "🔍 Preview"},
    "btn_undo": {"tr": "Son Ekleneni Sil", "en": "Remove Last"},
    "lbl_preview_area": {"tr": "Çalışma Alanı (Tıkla=Ekle / Sürükle=Taşı)", "en": "Workspace (Click=Add / Drag=Move)"},
    "lbl_no_pdf": {"tr": "Lütfen PDF Yükleyin", "en": "Please Load PDF"},
    "warn_sign": {"tr": "PDF ve İmza seçin.", "en": "Select PDF and Signature."},
    "page": {"tr": "Sayfa", "en": "Page"},
    "imza": {"tr": "İmza", "en": "Sign"},
    
    # AI Bot - Hazır Sorular
    "ai_welcome": {"tr": "Merhaba! Aşağıdaki konulardan hangisinde yardıma ihtiyacınız var?", "en": "Hello! Which topic do you need help with?"},
    "q_merge": {"tr": "🔗 PDF Nasıl Birleştirilir?", "en": "🔗 How to Merge PDFs?"},
    "q_sign": {"tr": "✍️ Nasıl İmza Eklenir?", "en": "✍️ How to Add Signature?"},
    "q_compress": {"tr": "📉 Dosya Nasıl Sıkıştırılır?", "en": "📉 How to Compress File?"},
    "q_rotate": {"tr": "🔄 Sayfa Nasıl Döndürülür?", "en": "🔄 How to Rotate Pages?"},
    "q_word": {"tr": "📄 Word'den PDF'e Çevirme", "en": "📄 Convert Word to PDF"},
    "q_jpg": {"tr": "🖼️ Resimden PDF Yapma", "en": "🖼️ Convert Image to PDF"},
    "q_status": {"tr": "❓ Şu An Hangi Dosya Yüklü?", "en": "❓ Which File is Loaded?"},
    "bot_name": {"tr": "Bot", "en": "Bot"},
    "user_name": {"tr": "Sen", "en": "You"}
}

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PDFApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.current_lang = "tr"
        
        # --- EKRAN AYARLARI ---
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        app_width = int(screen_width * 0.80)
        app_height = int(screen_height * 0.80)
        x_pos = int((screen_width - app_width) / 2)
        y_pos = int((screen_height - app_height) / 2)
        self.geometry(f"{app_width}x{app_height}+{x_pos}+{y_pos}")

        # --- Veri Yapıları ---
        self.merge_cards = []
        self.merge_selected_index = -1
        self.split_file_path = None
        self.split_pages_data = []
        self.compress_file_path = None
        
        self.sign_pdf_path = None
        self.sign_doc = None
        self.sign_current_page_num = 0
        self.sign_images = [] 
        self.sign_selected_img_index = -1
        self.sign_placements = {} 
        self.temp_image_files = []
        
        self.drag_data = {"item": None, "x": 0, "y": 0}
        self.canvas_images = {}

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

    def create_ui_elements(self):
        for widget in self.winfo_children(): widget.destroy()
        self.title(self.t("app_title"))
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10, fill="x", padx=20)
        self.header_label = ctk.CTkLabel(header_frame, text=self.t("header"), font=("Roboto", 24, "bold"))
        self.header_label.pack(side="left", expand=True)
        lang_btn_text = "🇹🇷 TR" if self.current_lang == "en" else "🇬🇧 EN"
        self.btn_lang = ctk.CTkButton(header_frame, text=lang_btn_text, width=60, command=self.toggle_language, fg_color="#555")
        self.btn_lang.pack(side="right")
        self.info_dnd = ctk.CTkLabel(self, text=self.t("hint"), text_color="#4a90e2")
        self.info_dnd.pack(pady=0)
        self.tabview = ctk.CTkTabview(self, width=1150, height=700)
        self.tabview.pack(padx=20, pady=10)
        
        self.tab_jpg = self.tabview.add(self.t("tab_jpg"))
        self.tab_word = self.tabview.add(self.t("tab_word"))
        self.tab_merge = self.tabview.add(self.t("tab_merge"))
        self.tab_split = self.tabview.add(self.t("tab_split"))
        self.tab_compress = self.tabview.add(self.t("tab_compress"))
        self.tab_sign = self.tabview.add(self.t("tab_sign"))
        self.tab_ai = self.tabview.add(self.t("tab_ai"))

        self.setup_jpg_tab(); self.setup_word_tab(); self.setup_merge_tab()
        self.setup_split_tab(); self.setup_compress_tab(); self.setup_sign_tab()
        self.setup_ai_tab()

    def on_closing(self):
        for temp_file in self.temp_image_files:
            try: os.remove(temp_file)
            except: pass
        self.quit()

    def drop_event_handler(self, event):
        raw_data = event.data
        if raw_data.startswith('{') and raw_data.endswith('}'): files = [f.strip('{}') for f in raw_data.split('} {')]
        else: files = raw_data.split()
        active = self.tabview.get()
        if active == self.t("tab_jpg"): self.convert_dropped_jpgs(files)
        elif active == self.t("tab_word"): self.convert_dropped_word(files[0])
        elif active == self.t("tab_merge"): self.add_merge_pdf_from_list(files)
        elif active == self.t("tab_split"): self.load_split_pdf_path(files[0])
        elif active == self.t("tab_compress"): self.load_compress_pdf(files[0])
        elif active == self.t("tab_sign"): self.load_sign_pdf(files[0])

    # --- 1. JPG ---
    def setup_jpg_tab(self):
        ctk.CTkLabel(self.tab_jpg, text=self.t("jpg_label"), font=("Arial", 14)).pack(pady=20)
        ctk.CTkButton(self.tab_jpg, text=self.t("btn_select_img"), command=self.convert_jpg_to_pdf).pack(pady=10)
    def convert_jpg_to_pdf(self):
        fs = filedialog.askopenfilenames(filetypes=[("Resim", "*.jpg;*.png")]); 
        if fs: self.convert_dropped_jpgs(list(fs))
    def convert_dropped_jpgs(self, fs):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s: 
            with open(s, "wb") as f: f.write(img2pdf.convert(fs))
            messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))

    # --- 2. WORD ---
    def setup_word_tab(self):
        ctk.CTkLabel(self.tab_word, text=self.t("word_label"), font=("Arial", 14)).pack(pady=20)
        ctk.CTkButton(self.tab_word, text=self.t("btn_select_word"), command=self.convert_word_to_pdf, fg_color="green").pack(pady=10)
    def convert_word_to_pdf(self):
        f = filedialog.askopenfilename(filetypes=[("Word", "*.docx")]); 
        if f: self.convert_dropped_word(f)
    def convert_dropped_word(self, f):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            pythoncom.CoInitialize(); w = win32com.client.Dispatch("Word.Application"); w.Visible = False
            d = w.Documents.Open(os.path.abspath(f)); d.SaveAs(os.path.abspath(s), FileFormat=17)
            d.Close(); w.Quit(); pythoncom.CoUninitialize(); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))

    # --- 3. MERGE ---
    def setup_merge_tab(self):
        f = ctk.CTkFrame(self.tab_merge, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(f, text=self.t("btn_add"), width=80, command=self.add_merge_pdf).pack(side="left")
        ctk.CTkButton(f, text=self.t("btn_del"), width=80, fg_color="#d32f2f", command=self.remove_merge_pdf).pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t("btn_clear_all"), width=80, fg_color="#555", command=self.clear_all_merge).pack(side="left", padx=5)
        ctk.CTkButton(f, text="<", width=40, command=self.move_merge_left).pack(side="left", padx=5)
        ctk.CTkButton(f, text=">", width=40, command=self.move_merge_right).pack(side="left", padx=2)
        ctk.CTkButton(f, text=self.t("btn_merge"), fg_color="green", command=self.merge_execute).pack(side="right")
        self.merge_gallery = ctk.CTkScrollableFrame(self.tab_merge, orientation="horizontal", height=250); self.merge_gallery.pack(fill="both", expand=True, padx=10)
        if self.merge_cards: self.refresh_merge_gallery()
    def add_merge_pdf(self):
        fs = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")]); 
        if fs: self.add_merge_pdf_from_list(fs)
    def add_merge_pdf_from_list(self, fs):
        for f in fs:
            try:
                doc = fitz.open(f); pix = doc[0].get_pixmap(matrix=fitz.Matrix(0.15, 0.15))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 140))
                self.merge_cards.append({'path': f, 'thumb': ctk_img})
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
        if len(self.merge_cards) < 2: messagebox.showwarning(self.t("msg_error"), "En az 2 dosya gerekli!"); return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            try:
                m = PdfWriter(); [m.append(c['path']) for c in self.merge_cards]; m.write(s); m.close()
                messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    # --- 4. SPLIT ---
    def setup_split_tab(self):
        f = ctk.CTkFrame(self.tab_split, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(f, text=self.t("btn_load"), command=self.load_split_pdf).pack(side="left")
        ctk.CTkButton(f, text=self.t("btn_reset"), width=80, fg_color="#555", command=self.deselect_all_split).pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t("btn_close_file"), width=90, fg_color="#d32f2f", command=self.clear_split_tab).pack(side="left", padx=5)
        ctk.CTkLabel(f, text=self.t("lbl_rotate"), text_color="gray").pack(side="left", padx=5)
        ctk.CTkButton(f, text="⟲", width=40, command=lambda: self.rotate_pages(90)).pack(side="left", padx=2)
        ctk.CTkButton(f, text="⟳", width=40, command=lambda: self.rotate_pages(-90)).pack(side="left", padx=2)
        txt = os.path.basename(self.split_file_path) if self.split_file_path else ""
        self.lbl_split_info = ctk.CTkLabel(f, text=txt, text_color="gray"); self.lbl_split_info.pack(side="left", padx=10)
        ctk.CTkButton(f, text=self.t("btn_save_sel"), fg_color="orange", command=self.save_selected_pages).pack(side="right", padx=10)
        self.split_scroll = ctk.CTkScrollableFrame(self.tab_split, label_text=self.t("lbl_pages")); self.split_scroll.pack(fill="both", expand=True, padx=10)
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
                ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(100, 140))
                d = {'page_num': i, 'image_ctk': ctk_img, 'image_pil': pil, 'selected': False, 'widget': None, 'rotation': 0}
                self.split_pages_data.append(d); self.create_split_widget(i, d)
        except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))
    def clear_split_tab(self):
        self.split_file_path = None; self.lbl_split_info.configure(text="")
        for w in self.split_scroll.winfo_children(): w.destroy()
        self.split_pages_data = []
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
            ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(100, 140))
            d['image_ctk'] = ctk_img; d['img_label'].configure(image=ctk_img)
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
            except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    # --- 5. COMPRESS ---
    def setup_compress_tab(self):
        for w in self.tab_compress.winfo_children(): w.destroy()
        f = ctk.CTkFrame(self.tab_compress); f.pack(fill="both", expand=True, padx=50, pady=50)
        ctk.CTkLabel(f, text=self.t("lbl_compress_title"), font=("Arial", 20, "bold")).pack(pady=20)
        file_frame = ctk.CTkFrame(f, fg_color="transparent"); file_frame.pack(pady=10)
        ctk.CTkButton(file_frame, text=self.t("btn_select"), command=self.select_compress_pdf).pack(side="left", padx=5)
        if self.compress_file_path:
            ctk.CTkButton(file_frame, text="X", width=30, fg_color="red", command=self.clear_compress_file).pack(side="left", padx=5)
        txt = os.path.basename(self.compress_file_path) if self.compress_file_path else ""
        self.lbl_compress_file = ctk.CTkLabel(f, text=txt, text_color="gray"); self.lbl_compress_file.pack()
        self.compress_slider = ctk.CTkSlider(f, from_=0.2, to=1.0, number_of_steps=8, command=self.on_compress_slider)
        self.compress_slider.set(0.6); self.compress_slider.pack(pady=10)
        self.lbl_quality_value = ctk.CTkLabel(f, text="Hedef Kalite: %60 (Orta)", font=("Arial", 12, "bold")); self.lbl_quality_value.pack(pady=(5, 20))
        state = "normal" if self.compress_file_path else "disabled"
        self.btn_compress = ctk.CTkButton(f, text=self.t("btn_compress"), state=state, fg_color="green", command=self.start_compression, height=40); self.btn_compress.pack(pady=20)
        if self.compress_file_path: self.update_compress_ui_info()
    def on_compress_slider(self, value):
        val_int = int(value * 100); desc = "Düşük" if val_int < 40 else ("Orta" if val_int < 75 else "Yüksek")
        self.lbl_quality_value.configure(text=f"Hedef Kalite: %{val_int} ({desc})")
    def select_compress_pdf(self): self.load_compress_pdf(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_compress_pdf(self, f): 
        if not f: return
        self.compress_file_path = f; self.setup_compress_tab() 
    def update_compress_ui_info(self):
        if not self.compress_file_path: return
        size_bytes = os.path.getsize(self.compress_file_path); size_mb = size_bytes / (1024 * 1024)
        self.lbl_compress_file.configure(text=f"{os.path.basename(self.compress_file_path)} ({size_mb:.2f} MB)")
    def clear_compress_file(self): self.compress_file_path = None; self.setup_compress_tab()
    def start_compression(self):
        if not self.compress_file_path: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not s: return
        quality_val = self.compress_slider.get(); target_dpi = int(72 + (quality_val * 150)); jpeg_quality = int(quality_val * 80)
        try:
            doc = fitz.open(self.compress_file_path); lst = []
            for i in range(len(doc)):
                page = doc.load_page(i); pix = page.get_pixmap(dpi=target_dpi, alpha=False) 
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                b = io.BytesIO(); img.save(b, format='JPEG', quality=jpeg_quality, optimize=True); lst.append(b.getvalue())
            with open(s, "wb") as f: f.write(img2pdf.convert(lst))
            messagebox.showinfo(self.t("msg_success"), self.t("msg_compressed"))
        except Exception as e: messagebox.showerror(self.t("msg_error"), str(e))

    # --- 6. KAŞE VE İMZA ---
    def setup_sign_tab(self):
        left_panel = ctk.CTkFrame(self.tab_sign, width=250); left_panel.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(left_panel, text=self.t("lbl_lib"), font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkButton(left_panel, text=self.t("btn_add_sign"), command=self.add_signature_image).pack(pady=5)
        self.sign_scroll = ctk.CTkScrollableFrame(left_panel); self.sign_scroll.pack(fill="both", expand=True, pady=10)
        right_panel = ctk.CTkFrame(self.tab_sign); right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        top_ctrl = ctk.CTkFrame(right_panel, fg_color="transparent"); top_ctrl.pack(fill="x", pady=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_load"), command=self.open_sign_pdf).pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_close_file"), width=90, fg_color="#d32f2f", command=self.close_sign_pdf).pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text="<", width=40, command=self.prev_sign_page).pack(side="left", padx=5)
        pg_txt = f"{self.sign_current_page_num + 1} / {len(self.sign_doc)}" if self.sign_doc else "0/0"
        self.lbl_sign_page = ctk.CTkLabel(top_ctrl, text=pg_txt); self.lbl_sign_page.pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text=">", width=40, command=self.next_sign_page).pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_preview"), width=80, fg_color="#1f538d", command=self.preview_signed_page).pack(side="right", padx=10)
        ctk.CTkButton(top_ctrl, text=self.t("btn_save_sel"), fg_color="green", command=self.save_signed_pdf).pack(side="right", padx=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_undo"), fg_color="#d32f2f", command=self.undo_last_stamp).pack(side="right", padx=5)
        self.canvas_container = ctk.CTkFrame(right_panel); self.canvas_container.pack(fill="both", expand=True, pady=5)
        self.v_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="vertical")
        self.h_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="horizontal")
        self.sign_canvas = Canvas(self.canvas_container, bg="gray", bd=0, highlightthickness=0, yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.v_scroll.configure(command=self.sign_canvas.yview); self.h_scroll.configure(command=self.sign_canvas.xview)
        self.v_scroll.pack(side="right", fill="y"); self.h_scroll.pack(side="bottom", fill="x"); self.sign_canvas.pack(side="left", fill="both", expand=True)
        self.sign_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.sign_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.sign_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        if self.sign_images: self.refresh_signature_library()
        if self.sign_doc: self.show_current_sign_page()
    def make_image_transparent(self, pil_img):
        pil_img = pil_img.convert("RGBA"); datas = pil_img.getdata(); new_data = []
        for item in datas:
            if item[0]>200 and item[1]>200 and item[2]>200: new_data.append((255,255,255,0))
            else: new_data.append(item)
        pil_img.putdata(new_data); return pil_img
    def add_signature_image(self):
        path = filedialog.askopenfilename(filetypes=[("Resim", "*.png;*.jpg;*.jpeg")])
        if not path: return
        try:
            pil = self.make_image_transparent(Image.open(path))
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); pil.save(t.name); t.close()
            self.temp_image_files.append(t.name)
            self.sign_images.append({'path': t.name, 'pil': pil})
            self.refresh_signature_library()
        except Exception as e: messagebox.showerror("Hata", str(e))
    def refresh_signature_library(self):
        for w in self.sign_scroll.winfo_children(): w.destroy()
        for i, item in enumerate(self.sign_images):
            thumb = item['pil'].copy(); thumb.thumbnail((100, 100))
            ctk_thumb = ctk.CTkImage(light_image=thumb, dark_image=thumb, size=(thumb.width, thumb.height))
            c = "#1f538d" if i == self.sign_selected_img_index else "transparent"
            card = ctk.CTkFrame(self.sign_scroll, fg_color=c, border_width=1, border_color="gray"); card.pack(pady=5, fill="x")
            lbl = ctk.CTkLabel(card, text="", image=ctk_thumb); lbl.pack(pady=5)
            ctk.CTkLabel(card, text=f"{self.t('imza')}-{i+1}", font=("Arial", 10)).pack(pady=2)
            for w in [card, lbl]: w.bind("<Button-1>", lambda e, x=i: self.select_signature(x))
    def select_signature(self, i): self.sign_selected_img_index = i; self.refresh_signature_library()
    def open_sign_pdf(self): self.load_sign_pdf(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_sign_pdf(self, path):
        if not path: return
        self.sign_pdf_path = path; self.sign_doc = fitz.open(path); self.sign_current_page_num = 0; self.sign_placements = {}
        self.show_current_sign_page()
    def close_sign_pdf(self):
        self.sign_pdf_path = None; self.sign_doc = None; self.sign_placements = {}; self.sign_canvas.delete("all")
        self.lbl_sign_page.configure(text="0/0")
    def show_current_sign_page(self):
        if not self.sign_doc: return
        self.sign_canvas.delete("all")
        page = self.sign_doc.load_page(self.sign_current_page_num)
        zoom = 1.5; mat = fitz.Matrix(zoom, zoom); pix = page.get_pixmap(matrix=mat)
        base_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.bg_tk_img = ImageTk.PhotoImage(base_img)
        self.sign_canvas.config(scrollregion=(0, 0, base_img.width, base_img.height))
        self.sign_canvas.create_image(0, 0, image=self.bg_tk_img, anchor="nw", tags="background")
        if self.sign_current_page_num in self.sign_placements:
            for i, (img_idx, x, y, uid) in enumerate(self.sign_placements[self.sign_current_page_num]):
                stamp_pil = self.sign_images[img_idx]['pil'].copy(); stamp_pil.thumbnail((150, 150))
                tk_stamp = ImageTk.PhotoImage(stamp_pil); self.canvas_images[uid] = tk_stamp
                screen_x = x * zoom; screen_y = y * zoom
                self.sign_canvas.create_image(screen_x, screen_y, image=tk_stamp, anchor="nw", tags=("movable", uid))
        self.lbl_sign_page.configure(text=f"{self.sign_current_page_num + 1} / {len(self.sign_doc)}")
    def on_canvas_press(self, event):
        canvas_x = self.sign_canvas.canvasx(event.x); canvas_y = self.sign_canvas.canvasy(event.y)
        try:
            item = self.sign_canvas.find_closest(canvas_x, canvas_y)[0]; tags = self.sign_canvas.gettags(item)
            if "movable" in tags: self.drag_data["item"] = item; self.drag_data["x"] = canvas_x; self.drag_data["y"] = canvas_y
            else:
                if self.sign_selected_img_index == -1: return
                self.add_stamp_to_data(canvas_x, canvas_y)
        except: pass
    def on_canvas_drag(self, event):
        if self.drag_data["item"]:
            canvas_x = self.sign_canvas.canvasx(event.x); canvas_y = self.sign_canvas.canvasy(event.y)
            delta_x = canvas_x - self.drag_data["x"]; delta_y = canvas_y - self.drag_data["y"]
            self.sign_canvas.move(self.drag_data["item"], delta_x, delta_y)
            self.drag_data["x"] = canvas_x; self.drag_data["y"] = canvas_y
    def on_canvas_release(self, event):
        if self.drag_data["item"]:
            item = self.drag_data["item"]; tags = self.sign_canvas.gettags(item)
            if len(tags) > 1:
                uid = tags[1]; coords = self.sign_canvas.coords(item); new_x, new_y = coords[0], coords[1]
                zoom = 1.5; pdf_x = new_x / zoom; pdf_y = new_y / zoom
                page_data = self.sign_placements.get(self.sign_current_page_num, [])
                for i, record in enumerate(page_data):
                    if record[3] == uid: page_data[i] = (record[0], pdf_x, pdf_y, uid); break
            self.drag_data["item"] = None
    def add_stamp_to_data(self, canvas_x, canvas_y):
        zoom = 1.5; pdf_x = (canvas_x / zoom) - 30; pdf_y = (canvas_y / zoom) - 30
        import uuid; uid = str(uuid.uuid4())
        if self.sign_current_page_num not in self.sign_placements: self.sign_placements[self.sign_current_page_num] = []
        self.sign_placements[self.sign_current_page_num].append((self.sign_selected_img_index, pdf_x, pdf_y, uid))
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
        win = ctk.CTkToplevel(self); win.geometry("900x900"); win.title("Preview")
        try:
            doc = fitz.open(self.sign_pdf_path); p = doc[self.sign_current_page_num]
            if self.sign_current_page_num in self.sign_placements:
                for img_idx, x, y, uid in self.sign_placements[self.sign_current_page_num]:
                    path = self.sign_images[img_idx]['path']; r = fitz.Rect(x, y, x+100, y+100); p.insert_image(r, filename=path)
            zoom = 2.0; pix = p.get_pixmap(matrix=fitz.Matrix(zoom, zoom)); pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ctk_img = ctk.CTkImage(pil, size=(pix.width//2, pix.height//2))
            sf = ctk.CTkScrollableFrame(win); sf.pack(fill="both", expand=True)
            ctk.CTkLabel(sf, text="", image=ctk_img).pack(pady=10)
        except Exception as e: messagebox.showerror("Hata", str(e))
    def save_signed_pdf(self):
        if not self.sign_doc: return
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            for p_num, stamps in self.sign_placements.items():
                page = self.sign_doc[p_num]
                for img_idx, x, y, uid in stamps:
                    path = self.sign_images[img_idx]['path']; r = fitz.Rect(x, y, x+100, y+100); page.insert_image(r, filename=path)
            self.sign_doc.save(s); messagebox.showinfo(self.t("msg_success"), self.t("msg_done")); self.load_sign_pdf(self.sign_pdf_path)

    # -------------------------------------------------------------------------
    # 7. AI ASİSTAN (HAZIR SORU BUTONLU)
    # -------------------------------------------------------------------------
    def setup_ai_tab(self):
        main_frame = ctk.CTkFrame(self.tab_ai, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sohbet Geçmişi
        self.chat_history = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        self.chat_history.pack(fill="both", expand=True, pady=(0, 10))

        self.send_bot_message(self.t("ai_welcome"))

        # Soru Butonları Çerçevesi (Izgara)
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", side="bottom")
        
        # Buton Listesi (Key, Row, Col)
        buttons = [
            ("q_merge", 0, 0), ("q_sign", 0, 1), 
            ("q_compress", 1, 0), ("q_rotate", 1, 1),
            ("q_word", 2, 0), ("q_jpg", 2, 1),
            ("q_status", 3, 0)
        ]
        
        for key, r, c in buttons:
            # Butonlar 2 sütun halinde dizilir
            btn = ctk.CTkButton(btn_frame, text=self.t(key), height=40, 
                                command=lambda k=key: self.ask_question(k))
            # Sütun 3'e status butonunu ortalamak için colspan yapabiliriz ama
            # basitlik için 0. indexe weight vererek yayalım.
            if key == "q_status":
                btn.grid(row=r, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
            else:
                btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

    def ask_question(self, key):
        question_text = self.t(key)
        self.display_message(question_text, is_user=True)
        self.after(300, lambda: self.process_bot_response(key))

    def send_bot_message(self, msg):
        self.display_message(msg, is_user=False)

    def display_message(self, msg, is_user):
        bubble_color = "#1f538d" if is_user else "#333333"
        align = "e" if is_user else "w"
        sender_name = self.t("user_name") if is_user else self.t("bot_name")
        
        msg_frame = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        msg_frame.pack(fill="x", pady=5)
        
        bubble = ctk.CTkFrame(msg_frame, fg_color=bubble_color, corner_radius=15)
        bubble.pack(side="right" if is_user else "left", padx=10)
        
        time_str = datetime.datetime.now().strftime("%H:%M")
        ctk.CTkLabel(bubble, text=f"{sender_name} • {time_str}", font=("Arial", 10, "bold"), text_color="gray").pack(anchor=align, padx=10, pady=(5,0))
        ctk.CTkLabel(bubble, text=msg, font=("Arial", 13), wraplength=400, justify="left").pack(padx=10, pady=5)
        
        self.chat_history._parent_canvas.yview_moveto(1.0)

    def process_bot_response(self, question_key):
        response = ""
        
        if question_key == "q_merge":
            response = "'PDF Birleştir' sekmesine gidin, dosyalarınızı sürükleyip bırakın ve 'BİRLEŞTİR' butonuna basın. Ok tuşlarıyla sırayı değiştirebilirsiniz." if self.current_lang == "tr" else "Go to 'Merge PDF' tab, drag & drop your files and click 'MERGE'. You can reorder files using arrow buttons."
            
        elif question_key == "q_sign":
            response = "'Kaşe & İmza' sekmesinde önce imzanızın fotoğrafını (JPG/PNG) ekleyin. Sonra PDF yükleyip imzanıza tıklayarak belgeye yerleştirin. İmzanın arka planı otomatik temizlenir!" if self.current_lang == "tr" else "In 'Stamp & Sign' tab, first add your signature image (JPG/PNG). Then load a PDF and click on your signature to place it. Background is removed automatically!"
            
        elif question_key == "q_compress":
            response = "'PDF Sıkıştır' sekmesinde dosyanızı seçin. Kaydırma çubuğu ile kaliteyi ayarlayın (Sola çekerseniz boyut küçülür). Sonra 'SIKIŞTIR'a basın." if self.current_lang == "tr" else "Select your file in 'Compress PDF' tab. Adjust quality with the slider (Move left for smaller size). Then click 'COMPRESS'."
            
        elif question_key == "q_rotate":
            response = "'PDF Ayrıştır/Döndür' sekmesinde dosyayı yükleyin. Döndürmek istediğiniz sayfaları seçip yukarıdaki '⟲' veya '⟳' butonlarına basın." if self.current_lang == "tr" else "Load file in 'Split/Rotate PDF'. Select the pages you want to rotate and click '⟲' or '⟳' buttons at the top."
            
        elif question_key == "q_word":
            response = "Word dosyanızı 'Word > PDF' sekmesine sürükleyin ve 'Word Seç' butonuna basın. Bilgisayarınızda Microsoft Word yüklü olmalıdır." if self.current_lang == "tr" else "Drag your Word file to 'Word > PDF' tab and click 'Select Word'. Microsoft Word must be installed on your PC."
            
        elif question_key == "q_jpg":
            response = "'JPG > PDF' sekmesine birden fazla resim sürükleyebilirsiniz. Hepsi tek bir PDF dosyasında birleştirilir." if self.current_lang == "tr" else "You can drag multiple images to 'JPG > PDF' tab. They will be combined into a single PDF."
            
        elif question_key == "q_status":
            if self.sign_pdf_path:
                f_name = os.path.basename(self.sign_pdf_path)
                response = f"Şu an İmza sekmesinde '{f_name}' yüklü." if self.current_lang == "tr" else f"Currently '{f_name}' is loaded in Sign tab."
            elif self.split_file_path:
                f_name = os.path.basename(self.split_file_path)
                response = f"Ayrıştırma sekmesinde '{f_name}' üzerinde çalışıyorsunuz." if self.current_lang == "tr" else f"You are working on '{f_name}' in Split tab."
            else:
                response = "Şu an işlem yapılan aktif bir dosya görünmüyor." if self.current_lang == "tr" else "No active file is currently loaded."

        self.send_bot_message(response)

if __name__ == "__main__":
    app = PDFApp()
    app.mainloop()
