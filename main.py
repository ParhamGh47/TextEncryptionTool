import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


# --- Cipher Logic ---
def get_cipher_maps(seed, shift, iterations):
    random.seed(seed)

    letters = list(string.ascii_letters)
    others = list(string.punctuation + string.digits + " ")

    shuffled_letters = letters[:]
    shuffled_others = others[:]

    for _ in range(iterations):
        random.shuffle(shuffled_letters)
        shuffled_letters = [shuffled_letters[(i + shift) % len(shuffled_letters)] for i in range(len(shuffled_letters))]

        random.shuffle(shuffled_others)
        shuffled_others = [shuffled_others[(i + shift) % len(shuffled_others)] for i in range(len(shuffled_others))]

    original = letters + others
    shuffled = shuffled_letters + shuffled_others

    enc_map = {o: s for o, s in zip(original, shuffled)}
    dec_map = {s: o for o, s in zip(original, shuffled)}

    return enc_map, dec_map


def encrypt(text, provided_key=None):
    if provided_key:
        try:
            hex_key, shift, iterations = provided_key.split('-')
            seed = int(hex_key, 16)
            shift = int(shift)
            iterations = int(iterations)
        except ValueError:
            return None, "Invalid key format."
    else:
        seed = random.randint(0, 2**32 - 1)
        shift = random.randint(1, 10)
        iterations = random.randint(1, 5)

    enc_map, _ = get_cipher_maps(seed, shift, iterations)
    space_placeholder = "@"
    modified_text = text.replace(" ", space_placeholder)

    result = ''.join(enc_map.get(c, c) for c in modified_text)

    key = provided_key if provided_key else f"{hex(seed)}-{shift}-{iterations}"
    return result, key


def decrypt(text, key):
    try:
        hex_key, shift, iterations = key.split('-')
        seed = int(hex_key, 16)
        shift = int(shift)
        iterations = int(iterations)

        _, dec_map = get_cipher_maps(seed, shift, iterations)
        decrypted_text = ''.join(dec_map.get(c, c) for c in text)

        # Restore spaces
        space_placeholder = "@"
        restored_text = decrypted_text.replace(space_placeholder, " ")

        return restored_text
    except ValueError:
        return None


# --- GUI Setup ---
class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Encryption Tool")
        self.root.configure(bg="black")
        self.root.geometry("520x360")
        self.root.resizable(False, False)

        self.mode = tk.StringVar(value="Encrypt")
        self.dropdown = ttk.Combobox(root, values=["Encrypt", "Decrypt"], textvariable=self.mode, state="readonly", width=15)
        self.dropdown.pack(pady=(10, 5))
        self.dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_mode())

        self.setup_fields()
        self.update_mode()


    def setup_fields(self):
        style = {'bg': 'black', 'fg': 'lime', 'insertbackground': 'lime', 'font': ('Courier', 10)}
        label_style = {'bg': 'black', 'fg': 'lime', 'font': ('Courier', 10, 'bold')}

        self.input_label = tk.Label(self.root, text="Input Text:", **label_style)
        self.input_label.pack(pady=(5, 2))
        self.input_box = tk.Text(self.root, height=3, width=58, **style)
        self.input_box.pack(padx=10, pady=(0, 5))

        self.key_label = tk.Label(self.root, text="Key:", **label_style)
        self.key_label.pack(pady=(5, 2))
        key_frame = tk.Frame(self.root, bg='black')
        key_frame.pack(padx=10, pady=(0, 5))
        self.key_box = tk.Text(key_frame, height=1, width=46, **style)
        self.key_box.pack(side=tk.LEFT, padx=(0, 5))
        self.copy_key_btn = tk.Button(key_frame, text="Copy Key", command=self.copy_key, bg="black", fg="lime", font=("Courier", 9), relief=tk.GROOVE)
        self.copy_key_btn.pack(side=tk.LEFT)

        self.action_btn = tk.Button(self.root, text="Encrypt", command=self.perform_action, bg="lime", fg="black", font=('Courier', 11, 'bold'), width=18)
        self.action_btn.pack(pady=(10, 5))

        self.output_label = tk.Label(self.root, text="Encrypted Text:", **label_style)
        self.output_label.pack(pady=(5, 2))
        self.output_box = tk.Text(self.root, height=3, width=58, **style)
        self.output_box.pack(padx=10, pady=(0, 5))
        self.copy_output_btn = tk.Button(self.root, text="Copy Output", command=self.copy_output, bg="black", fg="lime", font=("Courier", 9), relief=tk.GROOVE)
        self.copy_output_btn.pack(pady=(5, 10))


    def update_mode(self):
        mode = self.mode.get()
        self.input_box.delete("1.0", tk.END)
        self.key_box.config(state='normal')
        self.key_box.delete("1.0", tk.END)
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.copy_key_btn.config(text="Copy Key")
        self.copy_output_btn.config(text="Copy Output")

        if mode == "Encrypt":
            self.action_btn.config(text="Encrypt")
            self.output_label.config(text="Encrypted Text:")
            self.copy_key_btn.config(state="normal")
        else:
            self.action_btn.config(text="Decrypt")
            self.output_label.config(text="Decrypted Text:")
            self.copy_key_btn.config(state="disabled")


    def perform_action(self):
        text = self.input_box.get("1.0", tk.END).strip()
        key = self.key_box.get("1.0", tk.END).strip()

        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.key_box.config(state='normal')
        self.key_box.delete("1.0", tk.END)
        self.copy_key_btn.config(text="Copy Key")
        self.copy_output_btn.config(text="Copy Output")

        if self.mode.get() == "Encrypt":
            if not text:
                messagebox.showerror("Missing Input", "Please enter text to encrypt.")
                return
            
            encrypted, generated_key = encrypt(text, key if key else None)

            if encrypted is None:
                messagebox.showerror("Error", "Invalid key format.")
                return

            self.output_box.insert(tk.END, encrypted)
            self.key_box.insert(tk.END, generated_key)
            self.key_box.config(state='disabled')

        else:
            if not text or not key:
                messagebox.showerror("Missing Info", "Please enter both encrypted text and key.")
                return
            
            decrypted = decrypt(text, key)
            
            if decrypted is None:
                messagebox.showerror("Error", "Invalid key format.")
            else:
                self.output_box.insert(tk.END, decrypted)

        self.output_box.config(state='disabled')


    def copy_output(self):
        self.output_box.config(state='normal')
        text = self.output_box.get("1.0", tk.END).strip()
        self.output_box.config(state='disabled')
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.copy_output_btn.config(text="Copied!")
            self.root.after(1500, lambda: self.copy_output_btn.config(text="Copy Output"))


    def copy_key(self):
        self.key_box.config(state='normal')
        key = self.key_box.get("1.0", tk.END).strip()
        self.key_box.config(state='disabled')
        if key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            self.copy_key_btn.config(text="Copied!")
            self.root.after(1500, lambda: self.copy_key_btn.config(text="Copy Key"))



# --- Launch ---
root = tk.Tk()
app = CipherApp(root)
root.mainloop()
