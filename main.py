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

# --- DİL SÖZLÜĞÜ ---
TEXTS = {
    "app_title": {"tr": "Süper PDF Stüdyosu - Ultimate", "en": "Super PDF Studio - Ultimate"},
    "header": {"tr": "PDF Ofis Stüdyosu", "en": "PDF Office Studio"},
    "hint": {"tr": "💡 İpucu: Dosyaları pencereye sürükleyebilirsiniz!", "en": "💡 Hint: You can drag & drop files here!"},
    "tab_jpg": {"tr": "JPG > PDF", "en": "JPG to PDF"},
    "tab_word": {"tr": "Word > PDF", "en": "Word to PDF"},
    "tab_merge": {"tr": "PDF Birleştir", "en": "Merge PDF"},
    "tab_split": {"tr": "PDF Ayrıştır/Döndür", "en": "Split/Rotate PDF"},
    "tab_compress": {"tr": "PDF Sıkıştır", "en": "Compress PDF"},
    "tab_sign": {"tr": "Kaşe & İmza (Hareketli)", "en": "Stamp & Sign (Movable)"},
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
    "btn_del": {"tr": "Sil", "en": "Del"},
    "btn_merge": {"tr": "BİRLEŞTİR", "en": "MERGE"},
    "lbl_queue": {"tr": "Sıra", "en": "Queue"},
    "btn_load": {"tr": "📂 Yükle", "en": "📂 Load"},
    "btn_reset": {"tr": "Sıfırla", "en": "Reset"},
    "btn_clear": {"tr": "Temizle", "en": "Clear"},
    "lbl_rotate": {"tr": "| Çevir:", "en": "| Rotate:"},
    "btn_save_sel": {"tr": "Kaydet", "en": "Save"},
    "lbl_pages": {"tr": "Sayfalar", "en": "Pages"},
    "warn_no_sel": {"tr": "Sayfa seçmediniz!", "en": "No pages selected!"},
    "lbl_compress_title": {"tr": "SIKIŞTIRMA", "en": "COMPRESSION"},
    "btn_select": {"tr": "Seç", "en": "Select"},
    "btn_compress": {"tr": "SIKIŞTIR", "en": "COMPRESS"},
    "msg_compressed": {"tr": "Sıkıştırıldı!", "en": "Compressed!"},
    "lbl_lib": {"tr": "İmza Kütüphanesi", "en": "Signature Lib"},
    "btn_add_sign": {"tr": "+ Kaşe/İmza Ekle", "en": "+ Add Stamp/Sign"},
    "btn_preview": {"tr": "🔍 Önizle", "en": "🔍 Preview"},
    "btn_undo": {"tr": "Son Ekleneni Sil", "en": "Remove Last"},
    "lbl_preview_area": {"tr": "Çalışma Alanı (Tıkla=Ekle / Sürükle=Taşı)", "en": "Workspace (Click=Add / Drag=Move)"},
    "lbl_no_pdf": {"tr": "Lütfen PDF Yükleyin", "en": "Please Load PDF"},
    "warn_sign": {"tr": "PDF ve İmza seçin.", "en": "Select PDF and Signature."},
    "page": {"tr": "Sayfa", "en": "Page"},
    "imza": {"tr": "İmza", "en": "Sign"}
}

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PDFApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.current_lang = "tr"
        self.geometry("1250x850")

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
        
        # İmza Yerleşimi: {sayfa_no: [ {'img_index': 0, 'x': 100, 'y': 200, 'uuid': 'uniq_id'}, ... ]}
        self.sign_placements = {} 
        self.temp_image_files = []
        
        # Sürükleme (Drag) Verileri
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # Referansları tutmak için (Garbage Collection önlemek için)
        self.canvas_images = {} # {canvas_item_id: PhotoImage}

        self.create_ui_elements()
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event_handler)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def t(self, key): return TEXTS.get(key, {}).get(self.current_lang, key)
    
    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "tr" else "tr"
        self.create_ui_elements()
        if self.sign_images: self.refresh_signature_library()

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
        self.setup_jpg_tab(); self.setup_word_tab(); self.setup_merge_tab()
        self.setup_split_tab(); self.setup_compress_tab(); self.setup_sign_tab()

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

    # --- ESKİ SEKMELERİN KODLARI (KISALTILMIŞ) ---
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

    def setup_merge_tab(self):
        f = ctk.CTkFrame(self.tab_merge, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(f, text=self.t("btn_add"), width=80, command=self.add_merge_pdf).pack(side="left")
        ctk.CTkButton(f, text=self.t("btn_del"), width=60, fg_color="#d32f2f", command=self.remove_merge_pdf).pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t("btn_merge"), fg_color="green", command=self.merge_execute).pack(side="right")
        self.merge_gallery = ctk.CTkScrollableFrame(self.tab_merge, orientation="horizontal", height=250); self.merge_gallery.pack(fill="both", expand=True, padx=10)
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
            ctk.CTkLabel(fr, text="", image=item['thumb']).pack(pady=5)
            ctk.CTkLabel(fr, text=os.path.basename(item['path'])[:10]).pack()
    def select_merge_card(self, i): self.merge_selected_index = i; self.refresh_merge_gallery()
    def remove_merge_pdf(self):
        if self.merge_selected_index != -1: self.merge_cards.pop(self.merge_selected_index); self.merge_selected_index = -1; self.refresh_merge_gallery()
    def move_merge_left(self): pass 
    def move_merge_right(self): pass
    def merge_execute(self):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            m = PdfWriter(); [m.append(c['path']) for c in self.merge_cards]; m.write(s); m.close()
            messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))

    def setup_split_tab(self):
        f = ctk.CTkFrame(self.tab_split, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(f, text=self.t("btn_load"), command=self.load_split_pdf).pack(side="left")
        ctk.CTkButton(f, text=self.t("btn_save_sel"), fg_color="orange", command=self.save_selected_pages).pack(side="right")
        self.split_scroll = ctk.CTkScrollableFrame(self.tab_split); self.split_scroll.pack(fill="both", expand=True, padx=10)
    def load_split_pdf(self): self.load_split_pdf_path(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_split_pdf_path(self, f):
        if not f: return
        self.split_file_path = f; self.split_pages_data = []
        for w in self.split_scroll.winfo_children(): w.destroy()
        doc = fitz.open(f)
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(0.15, 0.15)); pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            d = {'page_num': i, 'image_ctk': ctk.CTkImage(pil, size=(100, 140)), 'image_pil': pil, 'selected': False, 'widget': None, 'rotation': 0}
            self.split_pages_data.append(d); self.create_split_widget(i, d)
    def create_split_widget(self, i, d):
        fr = ctk.CTkFrame(self.split_scroll, width=120, height=180, border_width=2, border_color="gray", fg_color="transparent")
        fr.grid(row=i//6, column=i%6, padx=5, pady=5); d['widget'] = fr
        lbl = ctk.CTkLabel(fr, text="", image=d['image_ctk']); lbl.pack(pady=5)
        lbl.bind("<Button-1>", lambda e, x=i: self.toggle_split_sel(x))
    def toggle_split_sel(self, i):
        d = self.split_pages_data[i]; d['selected'] = not d['selected']
        d['widget'].configure(fg_color="#e67e22" if d['selected'] else "transparent")
    def save_selected_pages(self):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s:
            r = PdfReader(self.split_file_path); w = PdfWriter()
            [w.add_page(r.pages[d['page_num']]) for d in self.split_pages_data if d['selected']]
            w.write(s); w.close(); messagebox.showinfo(self.t("msg_success"), self.t("msg_done"))

    def setup_compress_tab(self):
        f = ctk.CTkFrame(self.tab_compress); f.pack(fill="both", expand=True, padx=50, pady=50)
        ctk.CTkLabel(f, text=self.t("lbl_compress_title"), font=("Arial", 20)).pack(pady=20)
        ctk.CTkButton(f, text=self.t("btn_select"), command=self.select_compress_pdf).pack()
        self.compress_slider = ctk.CTkSlider(f, from_=0.2, to=1.0); self.compress_slider.set(0.6); self.compress_slider.pack(pady=20)
        ctk.CTkButton(f, text=self.t("btn_compress"), fg_color="green", command=self.start_compression).pack()
    def select_compress_pdf(self): self.load_compress_pdf(filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]))
    def load_compress_pdf(self, f): self.compress_file_path = f
    def start_compression(self):
        s = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if s and self.compress_file_path:
            doc = fitz.open(self.compress_file_path); lst = []
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(dpi=int(72 + self.compress_slider.get()*150))
                b = io.BytesIO(); Image.frombytes("RGB", [pix.width, pix.height], pix.samples).save(b, 'JPEG', quality=int(self.compress_slider.get()*80)); lst.append(b.getvalue())
            with open(s, "wb") as f: f.write(img2pdf.convert(lst))
            messagebox.showinfo(self.t("msg_success"), self.t("msg_compressed"))

    # -------------------------------------------------------------------------
    # 6. KAŞE VE İMZA (HAREKETLİ CANVAS SİSTEMİ)
    # -------------------------------------------------------------------------
    def setup_sign_tab(self):
        left_panel = ctk.CTkFrame(self.tab_sign, width=250); left_panel.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(left_panel, text=self.t("lbl_lib"), font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkButton(left_panel, text=self.t("btn_add_sign"), command=self.add_signature_image).pack(pady=5)
        self.sign_scroll = ctk.CTkScrollableFrame(left_panel); self.sign_scroll.pack(fill="both", expand=True, pady=10)
        
        right_panel = ctk.CTkFrame(self.tab_sign); right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        top_ctrl = ctk.CTkFrame(right_panel, fg_color="transparent"); top_ctrl.pack(fill="x", pady=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_load"), command=self.open_sign_pdf).pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text="<", width=40, command=self.prev_sign_page).pack(side="left", padx=5)
        self.lbl_sign_page = ctk.CTkLabel(top_ctrl, text="0/0"); self.lbl_sign_page.pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text=">", width=40, command=self.next_sign_page).pack(side="left", padx=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_preview"), width=80, fg_color="#1f538d", command=self.preview_signed_page).pack(side="right", padx=10)
        ctk.CTkButton(top_ctrl, text=self.t("btn_save_sel"), fg_color="green", command=self.save_signed_pdf).pack(side="right", padx=5)
        ctk.CTkButton(top_ctrl, text=self.t("btn_undo"), fg_color="#d32f2f", command=self.undo_last_stamp).pack(side="right", padx=5)
        
        # --- DEĞİŞİKLİK: CTKScrollableFrame yerine CANVAS kullanıyoruz ---
        # Canvas, nesnelerin hareket etmesine izin verir.
        self.canvas_container = ctk.CTkFrame(right_panel)
        self.canvas_container.pack(fill="both", expand=True, pady=5)
        
        # Scroll barlar (Büyük PDF'ler için)
        self.v_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="vertical")
        self.h_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="horizontal")
        
        # Standart Tkinter Canvas (Hareket için en iyisi)
        self.sign_canvas = Canvas(self.canvas_container, bg="gray", bd=0, highlightthickness=0,
                                  yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        self.v_scroll.configure(command=self.sign_canvas.yview)
        self.h_scroll.configure(command=self.sign_canvas.xview)
        
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.sign_canvas.pack(side="left", fill="both", expand=True)

        # Canvas Olayları (Tıkla, Sürükle, Bırak)
        self.sign_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.sign_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.sign_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        if self.sign_images: self.refresh_signature_library()

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

    def show_current_sign_page(self):
        if not self.sign_doc: return
        # Canvas temizle
        self.sign_canvas.delete("all")
        
        page = self.sign_doc.load_page(self.sign_current_page_num)
        zoom = 1.5; mat = fitz.Matrix(zoom, zoom); pix = page.get_pixmap(matrix=mat)
        base_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # PDF Arka Planını Canvas'a çiz
        self.bg_tk_img = ImageTk.PhotoImage(base_img) # CTKImage değil, standart TK PhotoImage kullanıyoruz Canvas için
        self.sign_canvas.config(scrollregion=(0, 0, base_img.width, base_img.height))
        self.sign_canvas.create_image(0, 0, image=self.bg_tk_img, anchor="nw", tags="background")
        
        # Mevcut İmzaları Çiz
        if self.sign_current_page_num in self.sign_placements:
            for i, (img_idx, x, y, uid) in enumerate(self.sign_placements[self.sign_current_page_num]):
                stamp_pil = self.sign_images[img_idx]['pil'].copy()
                stamp_pil.thumbnail((150, 150))
                tk_stamp = ImageTk.PhotoImage(stamp_pil)
                
                # Referansı sakla (yoksa silinir)
                self.canvas_images[uid] = tk_stamp
                
                # Canvas'a ekle (PDF coord -> Screen coord)
                screen_x = x * zoom
                screen_y = y * zoom
                
                # "movable" tag'i ile bu objenin hareket edebilir olduğunu belirtiyoruz
                self.sign_canvas.create_image(screen_x, screen_y, image=tk_stamp, anchor="nw", tags=("movable", uid))
        
        self.lbl_sign_page.configure(text=f"{self.sign_current_page_num + 1} / {len(self.sign_doc)}")

    # --- CANVAS HAREKET MANTIĞI ---
    def on_canvas_press(self, event):
        # Tıklanan noktadaki objeyi bul (Canvas kaydırmasını hesaba kat)
        canvas_x = self.sign_canvas.canvasx(event.x)
        canvas_y = self.sign_canvas.canvasy(event.y)
        
        item = self.sign_canvas.find_closest(canvas_x, canvas_y)[0]
        tags = self.sign_canvas.gettags(item)
        
        if "movable" in tags:
            # Var olan imzayı tuttu
            self.drag_data["item"] = item
            self.drag_data["x"] = canvas_x
            self.drag_data["y"] = canvas_y
        else:
            # Boşluğa tıkladı -> Yeni İmza Ekle
            if self.sign_selected_img_index == -1: return
            self.add_stamp_to_data(canvas_x, canvas_y)

    def on_canvas_drag(self, event):
        if self.drag_data["item"]:
            # Ne kadar sürüklendi?
            canvas_x = self.sign_canvas.canvasx(event.x)
            canvas_y = self.sign_canvas.canvasy(event.y)
            
            delta_x = canvas_x - self.drag_data["x"]
            delta_y = canvas_y - self.drag_data["y"]
            
            # Objeyi hareket ettir
            self.sign_canvas.move(self.drag_data["item"], delta_x, delta_y)
            
            # Yeni konumu kaydet
            self.drag_data["x"] = canvas_x
            self.drag_data["y"] = canvas_y

    def on_canvas_release(self, event):
        if self.drag_data["item"]:
            # Sürükleme bitti, son konumu veritabanına (self.sign_placements) kaydet
            item = self.drag_data["item"]
            tags = self.sign_canvas.gettags(item)
            # tags[1] bizim unique id'miz (uid)
            if len(tags) > 1:
                uid = tags[1]
                # Canvas koordinatını al
                coords = self.sign_canvas.coords(item)
                new_x, new_y = coords[0], coords[1]
                
                # PDF koordinatına çevir (Screen -> PDF)
                zoom = 1.5
                pdf_x = new_x / zoom
                pdf_y = new_y / zoom
                
                # Listeyi güncelle
                page_data = self.sign_placements.get(self.sign_current_page_num, [])
                for i, record in enumerate(page_data):
                    if record[3] == uid: # record = (img_idx, x, y, uid)
                        page_data[i] = (record[0], pdf_x, pdf_y, uid)
                        break
            
            self.drag_data["item"] = None

    def add_stamp_to_data(self, canvas_x, canvas_y):
        zoom = 1.5
        # Tıklanan nokta merkez olsun diye biraz kaydır
        pdf_x = (canvas_x / zoom) - 30
        pdf_y = (canvas_y / zoom) - 30
        
        import uuid
        uid = str(uuid.uuid4())
        
        if self.sign_current_page_num not in self.sign_placements:
            self.sign_placements[self.sign_current_page_num] = []
        
        self.sign_placements[self.sign_current_page_num].append((self.sign_selected_img_index, pdf_x, pdf_y, uid))
        self.show_current_sign_page() # Ekranı yenile (yeni imza çizilsin)

    def undo_last_stamp(self):
        if self.sign_current_page_num in self.sign_placements and self.sign_placements[self.sign_current_page_num]:
            self.sign_placements[self.sign_current_page_num].pop()
            self.show_current_sign_page()
            
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

if __name__ == "__main__":
    app = PDFApp()
    app.mainloop()