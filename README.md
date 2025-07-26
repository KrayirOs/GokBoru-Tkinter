# GökBörü - Görsel Algılama ve Tarama Arayüzü

GökBörü, canlı kamera görüntüleri veya yüklü resimler üzerinden nesne tespiti yapan, modern arayüze sahip bir masaüstü uygulamasıdır. YOLOv11 modeli ile entegre çalışır ve kullanıcı dostu bir grafik arayüz üzerinden gerçek zamanlı analiz sağlar.

Bu proje; yangın tespiti, güvenlik izleme, otonom sistemler ve görüntü işleme uygulamaları geliştirmek isteyen öğrenciler, araştırmacılar ve geliştiriciler için tasarlanmıştır.

## Özellikler:
* Kamera veya yerel görsel üzerinden analiz
* YOLOv11 destekli nesne tanıma sistemi
* Otomatik çıktı kaydetme (işlenmiş görsel ve tespit bilgileri içeren metin dosyası)
* Orijinal ve işlenmiş görüntülerin eş zamanlı gösterimi
* Kullanımı kolay Tkinter tabanlı GUI
* Tüm taramaların arşivlendiği özel kayıt klasörü (`output/` dizini altında)

## Kurulum
Python 3.8 veya üzeri bir sürüm kullanılması önerilir.

### 1. Projeyi GitHub üzerinden klonlayın
```bash
git clone [https://github.com/krayiros/GokBoru-Tkinter.git](https://github.com/krayiros/GokBoru-Tkinter.git)
# 1. Projeyi GitHub üzerinden klonlayın
git clone https://github.com/kullaniciadi/yolov11-projem.git

# 2. Proje klasörüne geçin
cd yolov11-projem

# 3. Gerekli bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Model dosyalarını indir (örneğin yolov11.pt gibi)
Dosyana dahil et


# 5. Projeyi çalıştırın (örnek komut)
python main.py
