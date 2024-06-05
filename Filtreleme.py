import numpy as np  # NumPy kütüphanesini içe aktarıyoruz, temel bilimsel hesaplamalar ve dizi işlemleri için kullanılır.
import cv2  # OpenCV kütüphanesini içe aktarıyoruz, görüntü işleme için kullanılır.
from tkinter import *  # Tkinter kütüphanesini içe aktarıyoruz, GUI oluşturmak için kullanılır.
from tkinter import filedialog  # Tkinter'den dosya diyaloglarını içe aktarıyoruz.
from PIL import Image, ImageTk  # PIL kütüphanesini içe aktarıyoruz, görüntü işleme ve Tkinter ile uyumlu hale getirmek için kullanılır.

# Temel görüntü işleme fonksiyonları

def convert_to_gray(image):
    if len(image.shape) == 3:  # Eğer resim RGB ise
        # Renkli resmi gri tonlamaya dönüştürmek için kanalları ağırlıklı olarak topluyoruz.
        return np.dot(image[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    return image  # Resim zaten gri tonlamalıysa, doğrudan geri döndür.

def sharpen(image):
    # Keskinleştirme işlemi için kullanılacak çekirdek matrisi.
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return apply_kernel(image, kernel)  # Çekirdek matrisini resme uygula.

def blur(image):
    # Bulanıklaştırma işlemi için kullanılacak çekirdek matrisi.
    kernel = np.ones((5, 5)) / 25
    return apply_kernel(image, kernel)  # Çekirdek matrisini resme uygula.

def enhance_contrast(image):
    # Kontrastı artırmak için piksel değerlerini ayarlıyoruz.
    return np.clip(1.5 * image - 100, 0, 255).astype(np.uint8)

def red_filter(image):
    result = image.copy()  # Resmin bir kopyasını oluştur.
    result[:, :, 1] = 0  # Yeşil kanalı sıfırla.
    result[:, :, 2] = 0  # Mavi kanalı sıfırla.
    return result  # Sadece kırmızı kanalını bırak.

def green_filter(image):
    result = image.copy()  # Resmin bir kopyasını oluştur.
    result[:, :, 0] = 0  # Kırmızı kanalı sıfırla.
    result[:, :, 2] = 0  # Mavi kanalı sıfırla.
    return result  # Sadece yeşil kanalını bırak.

def blue_filter(image):
    result = image.copy()  # Resmin bir kopyasını oluştur.
    result[:, :, 0] = 0  # Kırmızı kanalı sıfırla.
    result[:, :, 1] = 0  # Yeşil kanalı sıfırla.
    return result  # Sadece mavi kanalını bırak.

def apply_kernel(image, kernel):
    height, width = image.shape[:2]  # Resmin yüksekliği ve genişliğini al.
    if len(image.shape) == 3:  # Eğer resim renkli ise
        result = np.zeros((height, width, 3), dtype=np.uint8)  # Sonuç için boş bir resim oluştur.
        for c in range(3):  # Her renk kanalı için
            result[:, :, c] = convolve2d(image[:, :, c], kernel)  # Çekirdek matrisini uygula.
        return result
    else:
        return convolve2d(image, kernel)  # Gri tonlamalı resim için çekirdek matrisini uygula.

def convolve2d(image, kernel):
    kernel_height, kernel_width = kernel.shape  # Çekirdek matrisinin boyutlarını al.
    pad_height, pad_width = kernel_height // 2, kernel_width // 2  # Dolgu boyutlarını hesapla.
    # Resmi dolgu ekleyerek genişlet.
    padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='constant')
    output = np.zeros_like(image)  # Sonuç için boş bir resim oluştur.
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Çekirdek matrisini uygula ve sonucu hesapla.
            output[i, j] = np.sum(padded_image[i:i+kernel_height, j:j+kernel_width] * kernel)
    return np.clip(output, 0, 255).astype(np.uint8)  # Sonuç resmini geri döndür.

def convert_to_rgb(image):
    if len(image.shape) == 2:  # Eğer resim gri tonlamalı ise
        return np.stack((image,) * 3, axis=-1)  # Renkli resme dönüştür.
    return image  # Resim zaten renkli ise, doğrudan geri döndür.

def equalize_histogram(image):
    if len(image.shape) == 3:  # Eğer resim renkli ise
        # Renkli resmi YUV renk uzayına dönüştür.
        img_to_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        # Y kanalında histogram eşitleme uygula.
        img_to_yuv[:, :, 0] = cv2.equalizeHist(img_to_yuv[:, :, 0])
        # Resmi geri RGB renk uzayına dönüştür.
        return cv2.cvtColor(img_to_yuv, cv2.COLOR_YUV2RGB)
    else:
        return cv2.equalizeHist(image)  # Gri tonlamalı resim için histogram eşitleme uygula.

# Arayüz oluşturma

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Görüntü İşleme Arayüzü")  # Pencere başlığını ayarla.
        self.root.geometry("1200x800")  # Pencere boyutunu ayarla.
        self.root.configure(bg='#f0f0f0')  # Arka plan rengini ayarla.

        self.panel = Label(self.root, bg='#f0f0f0')  # Görüntü panelini oluştur.
        self.panel.pack(pady=20)  # Paneli yerleştir ve biraz boşluk bırak.

        control_frame = Frame(self.root, bg='#f0f0f0')  # Kontrol düğmeleri için çerçeve oluştur.
        control_frame.pack(fill="both", expand=True)  # Çerçeveyi yerleştir ve genişlemesini sağla.

        # Resim yükleme düğmesini oluştur ve yerleştir.
        self.upload_button = Button(control_frame, text="Fotoğraf Yükle", command=self.upload_image, 
                                    bg='#4CAF50', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.upload_button.grid(row=0, column=0, padx=10, pady=10)

        # Gri tonlama düğmesini oluştur ve yerleştir.
        self.gray_button = Button(control_frame, text="Gri Tonlama", command=self.convert_to_gray, 
                                  bg='#FFC107', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.gray_button.grid(row=0, column=1, padx=10, pady=10)

        # Keskinleştirme düğmesini oluştur ve yerleştir.
        self.sharpen_button = Button(control_frame, text="Keskinleştirme", command=self.sharpen, 
                                     bg='#9C27B0', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.sharpen_button.grid(row=0, column=2, padx=10, pady=10)

        # Bulanıklaştırma düğmesini oluştur ve yerleştir.
        self.blur_button = Button(control_frame, text="Bulanıklaştırma", command=self.blur, 
                                  bg='#2196F3', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.blur_button.grid(row=0, column=3, padx=10, pady=10)

        # Kontrast geliştirme düğmesini oluştur ve yerleştir.
        self.contrast_button = Button(control_frame, text="Contrast Geliştirme", command=self.enhance_contrast, 
                                      bg='#FF5722', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.contrast_button.grid(row=0, column=4, padx=10, pady=10)

        # Kırmızı filtre düğmesini oluştur ve yerleştir.
        self.red_button = Button(control_frame, text="Kırmızı Filtre", command=self.red_filter, 
                                 bg='#F44336', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.red_button.grid(row=0, column=5, padx=10, pady=10)

        # Yeşil filtre düğmesini oluştur ve yerleştir.
        self.green_button = Button(control_frame, text="Yeşil Filtre", command=self.green_filter, 
                                   bg='#4CAF50', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.green_button.grid(row=1, column=0, padx=10, pady=10)

        # Mavi filtre düğmesini oluştur ve yerleştir.
        self.blue_button = Button(control_frame, text="Mavi Filtre", command=self.blue_filter, 
                                  bg='#2196F3', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.blue_button.grid(row=1, column=1, padx=10, pady=10)

        # Histogram eşitleme düğmesini oluştur ve yerleştir.
        self.hist_eq_button = Button(control_frame, text="Histogram Eşitleme", command=self.equalize_histogram, 
                                     bg='#607D8B', fg='white', font=('Helvetica', 12, 'bold'), borderwidth=2, relief='raised')
        self.hist_eq_button.grid(row=1, column=2, padx=10, pady=10)

        self.image = None  # Başlangıçta resim yok.

    def upload_image(self):
        file_path = filedialog.askopenfilename()  # Dosya diyaloguyla resim seç.
        if len(file_path) > 0:
            self.image = np.array(Image.open(file_path))  # Resmi oku ve numpy dizisine dönüştür.
            self.display_image(self.image)  # Resmi göster.

    def display_image(self, img):
        max_height, max_width = 600, 800  # Maksimum boyutları ayarla.
        height, width = img.shape[:2]  # Resmin boyutlarını al.
        scaling_factor = min(max_width/width, max_height/height)  # Ölçekleme faktörünü hesapla.
        new_size = (int(width * scaling_factor), int(height * scaling_factor))  # Yeni boyutları hesapla.
        resized_img = np.array(Image.fromarray(img).resize(new_size))  # Resmi yeniden boyutlandır.

        img = Image.fromarray(resized_img)  # Resmi PIL formatına dönüştür.
        img = ImageTk.PhotoImage(img)  # Tkinter ile uyumlu hale getir.

        self.panel.configure(image=img)  # Paneli güncelle.
        self.panel.image = img  # Panelde resmi sakla.

    def convert_to_gray(self):
        if self.image is not None:  # Eğer resim varsa
            gray_image = convert_to_gray(self.image)  # Gri tonlamaya dönüştür.
            self.display_image(gray_image)  # Yeni resmi göster.

    def sharpen(self):
        if self.image is not None:  # Eğer resim varsa
            sharpened_image = sharpen(self.image)  # Keskinleştir.
            self.display_image(sharpened_image)  # Yeni resmi göster.

    def blur(self):
        if self.image is not None:  # Eğer resim varsa
            blurred_image = blur(self.image)  # Bulanıklaştır.
            self.display_image(blurred_image)  # Yeni resmi göster.

    def enhance_contrast(self):
        if self.image is not None:  # Eğer resim varsa
            contrast_image = enhance_contrast(self.image)  # Kontrastı artır.
            self.display_image(contrast_image)  # Yeni resmi göster.

    def red_filter(self):
        if self.image is not None:  # Eğer resim varsa
            red_image = red_filter(self.image)  # Kırmızı filtre uygula.
            self.display_image(red_image)  # Yeni resmi göster.

    def green_filter(self):
        if self.image is not None:  # Eğer resim varsa
            green_image = green_filter(self.image)  # Yeşil filtre uygula.
            self.display_image(green_image)  # Yeni resmi göster.

    def blue_filter(self):
        if self.image is not None:  # Eğer resim varsa
            blue_image = blue_filter(self.image)  # Mavi filtre uygula.
            self.display_image(blue_image)  # Yeni resmi göster.

    def equalize_histogram(self):
        if self.image is not None:  # Eğer resim varsa
            equalized_image = equalize_histogram(self.image)  # Histogram eşitleme uygula.
            self.display_image(equalized_image)  # Yeni resmi göster.

if __name__ == "__main__":
    root = Tk()  # Ana pencereyi oluştur.
    app = ImageProcessor(root)  # ImageProcessor sınıfını örnekle.
    root.mainloop()  # Ana döngüyü başlat.
