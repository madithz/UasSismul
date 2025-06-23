import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import random
import hashlib

# Helper function: get pixel order based on password
def get_pixel_order(width, height, password):
    seed = int(hashlib.sha256(password.encode()).hexdigest(), 16) % (10 ** 8)
    coords = [(x, y) for y in range(height) for x in range(width)]
    random.seed(seed)
    random.shuffle(coords)
    return coords

# Encoding function
def embed_message(path, message, password):
    img = Image.open(path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    message_bin = ''.join(format(ord(c), '08b') for c in message)
    length_bin = format(len(message_bin), '032b')
    total_bin = length_bin + message_bin

    coords = get_pixel_order(width, height, password)
    if len(total_bin) > len(coords):
        raise ValueError("Pesan terlalu panjang untuk gambar ini.")

    for i, bit in enumerate(total_bin):
        x, y = coords[i]
        r, g, b = pixels[x, y]
        channel = random.choice([0, 1, 2])
        color = [r, g, b]

        current_lsb = color[channel] % 2
        bit = int(bit)
        if current_lsb != bit:
            color[channel] = color[channel] + 1 if color[channel] < 255 else color[channel] - 1
        pixels[x, y] = tuple(color)

    out_path = path.replace('.', '_stego.')
    img.save(out_path)
    return out_path

# Decoding function
def extract_message(path, password):
    img = Image.open(path).convert('RGB')
    pixels = img.load()
    width, height = img.size
    coords = get_pixel_order(width, height, password)

    bits = ""
    for i in range(32):
        x, y = coords[i]
        r, g, b = pixels[x, y]
        bits += str([r, g, b][random.choice([0, 1, 2])] % 2)
    msg_len = int(bits, 2)

    bits = ""
    for i in range(32, 32 + msg_len):
        x, y = coords[i]
        r, g, b = pixels[x, y]
        bits += str([r, g, b][random.choice([0, 1, 2])] % 2)

    chars = [chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# GUI Main Menu
def show_main_menu():
    clear_widgets()
    tk.Label(root, text="Pilih Mode:", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Button(root, text="Encoding", width=20, command=show_encoding_interface).pack(pady=5)
    tk.Button(root, text="Decoding", width=20, command=show_decoding_interface).pack(pady=5)

# GUI Encoding
def show_encoding_interface():
    clear_widgets()

    def browse_image():
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp")])
        if filepath:
            path_var.set(filepath)

    def do_embed():
        path = path_var.get()
        message = msg_entry.get()
        password = pass_entry.get()
        if not path or not message or not password:
            messagebox.showwarning("Input Missing", "Semua input harus diisi.")
            return
        try:
            result = embed_message(path, message, password)
            messagebox.showinfo("Berhasil", f"Pesan berhasil disisipkan ke: {result}")
            show_main_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(root, text="[ENCODING MODE]", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Label(root, text="Pilih Gambar:").pack()
    path_var = tk.StringVar()
    tk.Entry(root, textvariable=path_var, width=50).pack()
    tk.Button(root, text="Browse", command=browse_image).pack()

    tk.Label(root, text="Pesan untuk disisipkan:").pack()
    msg_entry = tk.Entry(root, width=50)
    msg_entry.pack()

    tk.Label(root, text="Password:").pack()
    pass_entry = tk.Entry(root, show='*', width=50)
    pass_entry.pack()

    tk.Button(root, text="Sisipkan Pesan", command=do_embed).pack(pady=10)
    tk.Button(root, text="Kembali ke Menu", command=show_main_menu).pack(pady=5)

# GUI Decoding
def show_decoding_interface():
    clear_widgets()

    def browse_image():
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp")])
        if filepath:
            path_var.set(filepath)

    def do_extract():
        path = path_var.get()
        password = pass_entry.get()
        if not path or not password:
            messagebox.showwarning("Input Missing", "Path dan password harus diisi.")
            return
        try:
            result = extract_message(path, password)
            messagebox.showinfo("Pesan Ditemukan", f"Pesan: {result}")
            show_main_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(root, text="[DECODING MODE]", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Label(root, text="Pilih Gambar:").pack()
    path_var = tk.StringVar()
    tk.Entry(root, textvariable=path_var, width=50).pack()
    tk.Button(root, text="Browse", command=browse_image).pack()

    tk.Label(root, text="Password:").pack()
    pass_entry = tk.Entry(root, show='*', width=50)
    pass_entry.pack()

    tk.Button(root, text="Ekstrak Pesan", command=do_extract).pack(pady=10)
    tk.Button(root, text="Kembali ke Menu", command=show_main_menu).pack(pady=5)

# Utility function to clear window
def clear_widgets():
    for widget in root.winfo_children():
        widget.destroy()

# Run GUI
root = tk.Tk()
root.title("LSB Matching Steganography")
show_main_menu()
root.mainloop()
