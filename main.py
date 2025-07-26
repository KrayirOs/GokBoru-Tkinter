import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import os
from ultralytics import YOLO
import numpy as np
from datetime import datetime
import subprocess
import sys 


MODERN_FONT = ("Segoe UI", 11)
MODERN_FONT_BOLD = ("Segoe UI", 13, "bold")
MODERN_FONT_TITLE = ("Segoe UI", 18, "bold")

class GokboruApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.cap = None
        self.camera_active = False
        self.current_input_image = None
        self.model = None

        self.title("GökBörü")
        self.geometry("1200x700")
        self.configure(bg="#23272a")
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except Exception:
                pass

        # ttk stilini uygula
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=("Segoe UI", 12, "bold"), background="#7289da", foreground="#fff", borderwidth=0, focusthickness=3, focuscolor='none', padding=8)
        self.style.map('TButton', background=[('active', '#5b6eae')], foreground=[('active', '#e0e0e0')])
        self.style.configure('TFrame', background="#2c2f33")
        self.style.configure('TLabel', background="#2c2f33", foreground="#fff", font=("Segoe UI", 12))
        self.style.configure('Title.TLabel', font=("Segoe UI", 18, "bold"), background="#23272a", foreground="#fff")
        self.style.configure('PanelTitle.TLabel', font=("Segoe UI", 13, "bold"), background="#2c2f33", foreground="#fff")
        self.style.configure('DataText.TFrame', background="#23272a")

        # Kayıt klasörünü tanımla
        # GUI klasörünün bir üst dizinine kaydetmek isterseniz:
        self.save_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Gokboru_Scans")
        # Eğer GUI klasörünün içine kaydetmek isterseniz:
        # self.save_directory = os.path.join(os.path.dirname(__file__), "Gokboru_Scans")

        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        self.STYLE = {
            "font_bold": ("Segoe UI", 13, "bold"),
            "font_normal": ("Segoe UI", 11),
            "font_title": ("Segoe UI", 18, "bold"),
            "bg_primary": "#23272a",
            "bg_secondary": "#2c2f33",
            "bg_accent": "#7289da",
            "bg_accent_hover": "#5b6eae",
            "fg_light": "#ffffff",
            "fg_dark": "#99aab5",
            "border_color": "#444857",
            "panel_light": "#36393f",
            "panel_dark": "#23272a"
        }

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._load_yolo_model()

    def _load_yolo_model(self):
        """YOLO modelini yükler."""
        # best.pt dosyası main.py ile aynı dizinde (GUI klasörü içinde)
        model_path = os.path.join(os.path.dirname(__file__), "best.pt")

        if not os.path.exists(model_path):
            messagebox.showerror("Model Hatası", f"Model dosyası bulunamadı: {model_path}\nLütfen doğru yolu kontrol edin.")
            self.model = None
            return
        try:
            self.model = YOLO(model_path)
            print("YOLO modeli başarıyla yüklendi.")
        except Exception as e:
            messagebox.showerror("Model Yükleme Hatası", f"YOLO modeli yüklenirken bir hata oluştu: {e}")
            self.model = None

    def _create_widgets(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Başlık kısmı ve alt gölge
        frame_ust = tk.Frame(self, bg=self.STYLE["bg_primary"], bd=0, highlightthickness=0)
        frame_ust.grid(row=0, column=0, columnspan=3, sticky="ew")
        baslik = ttk.Label(frame_ust, text="🦅 GökBörü", style='Title.TLabel')
        baslik.pack(side="left", padx=25, pady=18)
        # Alt gölge efekti kaldırıldı
        # tk.Frame(self, height=6, bg="#181a1b", bd=0).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,0))

        self._create_input_panel()
        self._create_output_panel()
        self._create_control_panel()

    def _create_input_panel(self):
        frame_input = ttk.Frame(self, style='TFrame')
        frame_input.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20, ipadx=8, ipady=8)
        frame_input.grid_rowconfigure(1, weight=1)
        frame_input.grid_columnconfigure(0, weight=1)

        ttk.Label(frame_input, text="📷 Girdi", style='PanelTitle.TLabel').grid(row=0, column=0, sticky="n", pady=(0,10))
        self.input_image_label = tk.Label(frame_input, bg=self.STYLE["panel_light"], bd=1, relief="solid")
        self.input_image_label.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _create_output_panel(self):
        frame_output = ttk.Frame(self, style='TFrame')
        frame_output.grid(row=1, column=1, sticky="nsew", padx=10, pady=20, ipadx=8, ipady=8)
        frame_output.grid_rowconfigure(1, weight=1)
        frame_output.grid_columnconfigure(0, weight=1)

        ttk.Label(frame_output, text="🖼️ Çıktı", style='PanelTitle.TLabel').grid(row=0, column=0, sticky="n", pady=(0,10))
        self.output_image_label = tk.Label(frame_output, bg=self.STYLE["panel_light"], bd=1, relief="solid")
        self.output_image_label.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _create_control_panel(self):
        frame_control = ttk.Frame(self, style='TFrame')
        frame_control.grid(row=1, column=2, sticky="nsew", padx=(10, 20), pady=20, ipadx=8, ipady=8)
        frame_control.grid_columnconfigure(0, weight=1)

        button_frame = ttk.Frame(frame_control, style='TFrame')
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        button_frame.grid_columnconfigure(0, weight=1)

        # ttk butonlar ve hover efekti
        def add_hover(btn):
            btn.bind("<Enter>", lambda e: btn.configure(style='Hover.TButton'))
            btn.bind("<Leave>", lambda e: btn.configure(style='TButton'))

        self.style.configure('Hover.TButton', background=self.STYLE["bg_accent_hover"], foreground="#e0e0e0")

        btn1 = ttk.Button(button_frame, text="📁 Fotoğraf Yükle", command=self.load_image, style='TButton')
        btn1.grid(row=0, column=0, pady=4, sticky="ew")
        add_hover(btn1)
        btn2 = ttk.Button(button_frame, text="📷 Kamerayı Aç", command=self.start_camera_feed, style='TButton')
        btn2.grid(row=1, column=0, pady=4, sticky="ew")
        add_hover(btn2)
        btn3 = ttk.Button(button_frame, text="🔍 Tara", command=self.trigger_scan_and_update_text, style='TButton')
        btn3.grid(row=2, column=0, pady=4, sticky="ew")
        add_hover(btn3)
        btn4 = ttk.Button(button_frame, text="📂 Kaydedilen Verileri Aç", command=self.open_save_directory, style='TButton')
        btn4.grid(row=3, column=0, pady=12, sticky="ew")
        add_hover(btn4)

        data_frame = ttk.Frame(frame_control, style='DataText.TFrame')
        data_frame.grid(row=1, column=0, sticky="nsew")
        frame_control.grid_rowconfigure(1, weight=1)

        ttk.Label(data_frame, text="📊 Algılanan Veri", style='PanelTitle.TLabel').pack(pady=(0,10))

        # Placeholder efektli Text
        self.data_text = tk.Text(data_frame, bg=self.STYLE["panel_dark"], fg=self.STYLE["fg_dark"],
                                 font=self.STYLE["font_normal"], relief="flat", height=8, bd=2, highlightbackground=self.STYLE["border_color"], highlightthickness=1)
        self.data_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.data_text.insert("1.0", "Tarama sonrası veriler burada görünecektir.")
        self.data_text.bind("<FocusIn>", self._clear_placeholder)
        self.data_text.bind("<FocusOut>", self._add_placeholder)
        self._placeholder_active = True

    def _clear_placeholder(self, event):
        if self._placeholder_active:
            self.data_text.delete("1.0", "end")
            self._placeholder_active = False

    def _add_placeholder(self, event):
        if not self.data_text.get("1.0", "end").strip():
            self.data_text.insert("1.0", "Tarama sonrası veriler burada görünecektir.")
            self._placeholder_active = True

    def load_image(self):
        """Bilgisayardan bir görüntü dosyası seçer ve girdi panelinde gösterir."""
        self.stop_camera_feed()

        file_path = filedialog.askopenfilename(
            title="Bir fotoğraf seçin",
            filetypes=[("Görüntü Dosyaları", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        try:
            image = Image.open(file_path)
            self.current_input_image = image
            self.show_image(image, self.input_image_label)
            self.output_image_label.config(image='')
            self.output_image_label.image = None
            self.data_text.delete("1.0", "end")
            self.data_text.insert("1.0", "Tarama için 'Tara' butonuna basın.")
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü yüklenemedi: {e}")

    def start_camera_feed(self):
        """Kamerayı başlatır ve girdi panelinde canlı akışı gösterir."""
        if self.camera_active:
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Kamera Hatası", "Kamera bulunamadı veya açılamadı.")
            return

        self.camera_active = True
        self.data_text.delete("1.0", "end")
        self.data_text.insert("1.0", "Kamera akışı aktif. Canlı tarama başlıyor...\n")
        self.current_input_image = None
        self._update_camera_feed()

    def _update_camera_feed(self):
        """Kameradan bir kare okur, girdi ve çıktı panellerini günceller."""
        if not self.camera_active:
            return

        ret, frame = self.cap.read()
        if ret:
            frame_rgb_input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_input = Image.fromarray(frame_rgb_input)
            self.show_image(image_input, self.input_image_label) 

            try:
                detected_info, output_frame_with_boxes = self._perform_yolo_scan(frame)
                output_pil_image = Image.fromarray(cv2.cvtColor(output_frame_with_boxes, cv2.COLOR_BGR2RGB))
                self.show_image(output_pil_image, self.output_image_label)
            except FileNotFoundError as e:
                print(f"Model dosyası hatası (canlı akış): {e}")
                self.data_text.delete("1.0", "end")
                self.data_text.insert("end", f"Hata: {e}\n")
            except Exception as e:
                print(f"Canlı tarama hatası: {e}")
                self.data_text.delete("1.0", "end")
                self.data_text.insert("end", f"Canlı Tarama Hatası: {e}\n")

            self.after(15, self._update_camera_feed)
        else:
            self.stop_camera_feed()
            messagebox.showerror("Kamera Hatası", "Kamera akışı kesildi.")

    def stop_camera_feed(self):
        """Kamera akışını durdurur ve kaynakları serbest bırakır."""
        if self.cap:
            self.camera_active = False
            self.cap.release()
            self.cap = None
            self.current_input_image = None
            self.input_image_label.config(image='')
            self.input_image_label.image = None
            self.output_image_label.config(image='')
            self.output_image_label.image = None
            self.data_text.delete("1.0", "end")
            self.data_text.insert("1.0", "Kamera akışı durduruldu.")

    def show_image(self, pil_image, label_widget):
        """Verilen PIL görüntüsünü, belirtilen etiket widget'ında gösterecek şekilde yeniden boyutlandırır."""
        widget_w = label_widget.winfo_width()
        widget_h = label_widget.winfo_height()

        if widget_w == 0 or widget_h == 0:
            widget_w, widget_h = 400, 400

        img_copy = pil_image.copy()
        img_copy.thumbnail((widget_w, widget_h), Image.Resampling.LANCZOS)

        photo_image = ImageTk.PhotoImage(img_copy)

        label_widget.config(image=photo_image)
        label_widget.image = photo_image

    def _perform_yolo_scan(self, opencv_image):
        """YOLO modelini kullanarak bir OpenCV görüntüsünü tarar ve sonuçları döner."""
        if self.model is None:
            return [], opencv_image

        results = self.model(opencv_image, verbose=False)

        detected_info = []
        output_image_with_boxes = opencv_image.copy()

        if results and results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                label = f"{self.model.names.get(class_id, 'Bilinmeyen')} {confidence:.2f}"
                detected_info.append(f"Sınıf: {self.model.names.get(class_id, 'Bilinmeyen')}, Güven: {confidence:.2f}")
                
                cv2.rectangle(output_image_with_boxes, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(output_image_with_boxes, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        return detected_info, output_image_with_boxes

    def save_scan_results(self, detected_info, processed_image_np):
        """Tarama sonuçlarını ve işlenmiş görüntüyü bir klasöre kaydeder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename_base = f"scan_{timestamp}"
        image_path = os.path.join(self.save_directory, f"{filename_base}.png")
        text_path = os.path.join(self.save_directory, f"{filename_base}.txt")

        try:
            if processed_image_np is not None:
                cv2.imwrite(image_path, processed_image_np)
                print(f"İşlenmiş görüntü kaydedildi: {image_path}")

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(f"Tarama Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                if detected_info:
                    f.write("Algılanan Nesneler:\n")
                    for info in detected_info:
                        f.write(f"- {info}\n")
                else:
                    f.write("Hiçbir nesne algılanamadı.\n")
            print(f"Algılanan veriler kaydedildi: {text_path}")
            messagebox.showinfo("Kayıt Başarılı", f"Tarama sonuçları '{filename_base}' adıyla kaydedildi.")

        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Veriler kaydedilirken bir hata oluştu: {e}")

    def open_save_directory(self):
        """Tarama verilerinin kaydedildiği klasörü açar."""
        try:
            if sys.platform == "win32":
                os.startfile(self.save_directory)
            elif sys.platform == "darwin": # macOS
                subprocess.Popen(["open", self.save_directory])
            else: # linux variants
                subprocess.Popen(["xdg-open", self.save_directory])
        except Exception as e:
            messagebox.showerror("Klasör Açma Hatası", f"Klasör açılamadı: {e}\nLütfen yolu manuel olarak kontrol edin: {self.save_directory}")

    def trigger_scan_and_update_text(self):
        """'Tara' butonuna basıldığında çalışır."""
        opencv_image_to_scan = None
        
        if self.camera_active:
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Kamera Hatası", "Kameradan kare alınamadı.")
                self.data_text.insert("end", "Hata: Kameradan kare alınamadı.")
                return
            opencv_image_to_scan = frame
        else:
            if self.current_input_image is None:
                messagebox.showwarning("Uyarı", "Lütfen önce bir fotoğraf yükleyin veya kamerayı açın.")
                return
            numpy_image_rgb = np.array(self.current_input_image.convert('RGB'))
            opencv_image_to_scan = cv2.cvtColor(numpy_image_rgb, cv2.COLOR_RGB2BGR)

        self.data_text.delete("1.0", "end")
        self.data_text.insert("1.0", "Tarama başlatıldı...\n")

        try:
            detected_info, output_frame_with_boxes = self._perform_yolo_scan(opencv_image_to_scan)

            if detected_info:
                self.data_text.insert("end", "Algılanan Nesneler:\n" + "\n".join(detected_info) + "\n")
            else:
                self.data_text.insert("end", "Hiçbir nesne algılanamadı.\n")

            self.data_text.insert("end", "Tarama tamamlandı.\n")

            # Statik görüntü taraması ise, işlenmiş görüntüyü çıktı panelinde göster
            if not self.camera_active:
                output_pil_image = Image.fromarray(cv2.cvtColor(output_frame_with_boxes, cv2.COLOR_BGR2RGB))
                self.show_image(output_pil_image, self.output_image_label)

            # Tarama sonuçlarını kaydet (hem statik hem de kamera modunda)
            self.save_scan_results(detected_info, output_frame_with_boxes)

        except Exception as e:
            messagebox.showerror("Tarama Hatası", f"Tarama işlemi sırasında bir hata oluştu: {e}")
            self.data_text.insert("end", f"Hata: {e}\n")

    def on_closing(self):
        """Pencere kapatıldığında tüm kaynakları temizler."""
        self.stop_camera_feed()
        self.destroy()

if __name__ == "__main__":
    app = GokboruApp()
    app.mainloop()
