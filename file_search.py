import os
import threading
import tkinter as tk
from tkinter import messagebox

# Global bir listeye erişim için senkronizasyon
result_lock = threading.Lock()
results = []

# Metin dosyalarını kontrol etmek için geçerli uzantılar
text_extensions = ['.txt', '.md', '.html', '.css', '.js', '.json', '.xml', '.py']

# Dosyada anahtar kelimeyi arayan fonksiyon
def search_in_file(file_name, keyword):
    # Dosya uzantısını kontrol et
    if not any(file_name.endswith(ext) for ext in text_extensions):
        with result_lock:
            results.append(f"Skipping non-text file: {file_name}")  # Metin olmayan dosyalar geçilir
        return

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if keyword in line:  # Anahtar kelime bulunduğunda
                    with result_lock:
                        results.append(f'Found "{keyword}" in {file_name} on line {line_num}')  # Sonuçları ekle
    except Exception as e:
        # Dosya okuma hatası durumunda
        with result_lock:
            results.append(f'Error reading {file_name}: {e}')

# Dizin içinde anahtar kelimeyi arama fonksiyonu
def search_directory(directory, keyword):
    for root, dirs, files in os.walk(directory):  # Dizin içindeki tüm dosyaları dolaş
        for file in files:
            full_path = os.path.join(root, file)  # Dosyanın tam yolu
            search_in_file(full_path, keyword)  # Dosyada arama yap

# Thread fonksiyonu
def thread_task(directory, keyword):
    search_directory(directory, keyword)  # Her dizin için arama işlemini başlat

# Arama başlatma fonksiyonu
def start_search():
    keyword = entry_keyword.get()  # Kullanıcıdan anahtar kelime al
    directories = entry_directories.get().split(',')  # Kullanıcıdan dizinleri al

    # Gerekli inputların boş olup olmadığını kontrol et
    if not keyword or not directories:
        messagebox.showerror("Input Error", "Both fields must be filled out!")  # Hata mesajı göster
        return

    global results
    results = []  # Her arama için sonuçları sıfırla

    threads = []  # İş parçacıkları listesi

    # Her dizin için iş parçacığı oluştur
    for dir in directories:
        dir = dir.strip()  # Yoldaki boşlukları temizle
        if os.path.isdir(dir):  # Geçerli dizin olup olmadığını kontrol et
            t = threading.Thread(target=thread_task, args=(dir, keyword))  # Yeni iş parçacığı başlat
            threads.append(t)
            t.start()
        else:
            results.append(f"Warning: {dir} is not a valid directory.")  # Geçersiz dizin uyarısı
    
    # Tüm iş parçacıklarının tamamlanmasını bekle
    for t in threads:
        t.join()

    # Sonuçları GUI üzerinde göster
    display_results()

# Sonuçları ekranda gösterme fonksiyonu
def display_results():
    results_text.delete(1.0, tk.END)  # Önceki sonuçları temizle
    if results:
        for result in results:
            results_text.insert(tk.END, result + '\n')  # Sonuçları ekle
    else:
        results_text.insert(tk.END, "No matches found.")  # Eğer hiç sonuç yoksa

# GUI'yi oluşturma
root = tk.Tk()
root.title("File Search Application")  # Başlık
root.configure(bg="#f0f0f0")  # Arka plan rengini ayarla

# GUI'deki font ve renk seçeneklerini ayarla
root.option_add("*Font", "Helvetica 12")  # Yazı tipi ve boyutunu ayarla
root.geometry("800x600")  # Uygulamanın boyutunu ayarla

# Başlık ve açıklama etiketi
header_frame = tk.Frame(root, bg="#4CAF50")
header_frame.pack(fill="x", pady=10)
tk.Label(header_frame, text="File Search Application", font=("Helvetica", 16, "bold"), fg="white", bg="#4CAF50").pack(padx=20, pady=10)

# Anahtar kelime girişi
keyword_frame = tk.Frame(root, bg="#f0f0f0")
keyword_frame.pack(fill="x", padx=20, pady=10)
tk.Label(keyword_frame, text="Enter Keyword:", bg="#f0f0f0", anchor="w").pack(fill="x", padx=10, pady=5)
entry_keyword = tk.Entry(keyword_frame, width=50, bg="#ffffff")
entry_keyword.pack(padx=10, pady=5)

# Dizin girişi
directory_frame = tk.Frame(root, bg="#f0f0f0")
directory_frame.pack(fill="x", padx=20, pady=10)
tk.Label(directory_frame, text="Enter Directories (comma-separated):", bg="#f0f0f0", anchor="w").pack(fill="x", padx=10, pady=5)
entry_directories = tk.Entry(directory_frame, width=50, bg="#ffffff")
entry_directories.pack(padx=10, pady=5)

# Arama butonu
search_button = tk.Button(root, text="Start Search", command=start_search, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
search_button.pack(pady=20)

# Sonuçları gösterecek alan
results_text = tk.Text(root, width=80, height=20, bg="#f9f9f9", fg="#333333", wrap="word")
results_text.pack(padx=10, pady=10)

# Uygulamayı başlat
root.mainloop()
