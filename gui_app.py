import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from crypto_utils import decrypt_data, encrypt_data, generate_key
from vault_storage import load_vault_data, save_vault_data, vault_exists


class PasswordVaultApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Password Vault - by Adam Maatouk")
        self.root.geometry("500x540")
        self.root.resizable(False, False)

        # Helper to locate assets whether running as a script or inside PyInstaller .exe
        if getattr(sys, "frozen", False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_dir, "vault_logo.ico")

        # Set custom window icon if present
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.key = None
        self.vault_data = None

        if not vault_exists():
            self.show_setup_screen()
        else:
            self.show_login_screen()

    def clear_screen(self):
        """Helper to clear window widgets when switching views."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_footer(self):
        """Adds branding credit at the bottom of screens."""
        lbl_credit = tk.Label(
            self.root,
            text="Designed & Developed by Adam Maatouk",
            font=("Helvetica", 8, "italic"),
            fg="gray",
        )
        lbl_credit.pack(side="bottom", pady=5)

    # --- SCREEN 1: Setup Master Password (First Time) ---
    def show_setup_screen(self):
        self.clear_screen()

        title = tk.Label(
            self.root, text="Create Master Password", font=("Helvetica", 14, "bold")
        )
        title.pack(pady=20)

        lbl1 = tk.Label(self.root, text="Master Password:")
        lbl1.pack()
        self.txt_pass1 = tk.Entry(self.root, show="*", width=30)
        self.txt_pass1.pack(pady=5)

        lbl2 = tk.Label(self.root, text="Confirm Master Password:")
        lbl2.pack()
        self.txt_pass2 = tk.Entry(self.root, show="*", width=30)
        self.txt_pass2.pack(pady=5)

        btn_create = tk.Button(
            self.root,
            text="Create Vault",
            command=self.handle_setup,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 10, "bold"),
        )
        btn_create.pack(pady=20)

        self.add_footer()

    def handle_setup(self):
        p1 = self.txt_pass1.get().strip()
        p2 = self.txt_pass2.get().strip()

        if not p1 or p1 != p2:
            messagebox.showerror("Error", "Passwords do not match or are empty!")
            return

        self.key, salt = generate_key(p1)
        self.vault_data = {"salt": salt.hex(), "passwords": {}}
        save_vault_data(self.vault_data)

        messagebox.showinfo("Success", "Vault initialized successfully!")
        self.show_dashboard_screen()

    # --- SCREEN 2: Login / Unlock Vault ---
    def show_login_screen(self):
        self.clear_screen()

        title = tk.Label(
            self.root, text="Unlock Password Vault", font=("Helvetica", 14, "bold")
        )
        title.pack(pady=20)

        lbl = tk.Label(self.root, text="Enter Master Password:")
        lbl.pack()

        self.txt_login_pass = tk.Entry(self.root, show="*", width=30)
        self.txt_login_pass.pack(pady=10)

        btn_login = tk.Button(
            self.root,
            text="Unlock Vault",
            command=self.handle_login,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10, "bold"),
        )
        btn_login.pack(pady=10)

        # Forgot Master Password option
        btn_reset = tk.Button(
            self.root,
            text="Forgot Master Password? (Reset Vault)",
            command=self.handle_reset_vault,
            fg="red",
            bd=0,
        )
        btn_reset.pack(pady=15)

        self.add_footer()

    def handle_login(self):
        entered_pass = self.txt_login_pass.get().strip()
        if not entered_pass:
            messagebox.showerror("Error", "Please enter your Master Password.")
            return

        data = load_vault_data()
        salt = bytes.fromhex(data["salt"])
        derived_key, _ = generate_key(entered_pass, salt=salt)

        # Verify key if passwords exist
        if data["passwords"]:
            first_enc = next(iter(data["passwords"].values()))
            try:
                decrypt_data(first_enc.encode("utf-8"), derived_key)
            except Exception:
                messagebox.showerror("Access Denied", "Incorrect Master Password!")
                return

        self.key = derived_key
        self.vault_data = data
        self.show_dashboard_screen()

    def handle_reset_vault(self):
        confirm = messagebox.askyesno(
            "Reset Vault Warning",
            "Because of AES-256 encryption, your data cannot be recovered without"
            " the Master Password.\n\nResetting will DELETE 'vault.json' and all"
            " stored passwords permanently.\n\nDo you want to reset?",
        )
        if confirm:
            if os.path.exists("vault.json"):
                os.remove("vault.json")
            messagebox.showinfo(
                "Vault Reset", "Vault deleted. Let's set up a new master password."
            )
            self.show_setup_screen()

    # --- SCREEN 3: Vault Dashboard ---
    def show_dashboard_screen(self):
        self.clear_screen()

        # Top Form to Add Entry
        frame_add = ttk.LabelFrame(
            self.root, text="Add New Password", padding=10
        )
        frame_add.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_add, text="Service Name:").grid(row=0, column=0, sticky="w")
        self.ent_service = tk.Entry(frame_add, width=22)
        self.ent_service.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Password:").grid(row=1, column=0, sticky="w")
        self.ent_password = tk.Entry(frame_add, width=22, show="*")
        self.ent_password.grid(row=1, column=1, padx=5, pady=5)

        btn_save = tk.Button(
            frame_add,
            text="Save Entry",
            command=self.handle_save,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 9, "bold"),
        )
        btn_save.grid(row=2, column=1, sticky="e", pady=5)

        # Saved Items List Frame
        frame_list = ttk.LabelFrame(
            self.root, text="Saved Accounts", padding=10
        )
        frame_list.pack(fill="both", expand=True, padx=15, pady=5)

        # Scrollable Listbox
        self.lst_services = tk.Listbox(
            frame_list, height=8, font=("Helvetica", 10)
        )
        self.lst_services.pack(fill="both", expand=True, side="left", padx=(0, 10))

        # Action Buttons Frame (Right side)
        frame_actions = tk.Frame(frame_list)
        frame_actions.pack(side="right", fill="y")

        btn_retrieve = tk.Button(
            frame_actions,
            text="Get Password",
            command=self.handle_retrieve,
            bg="#2196F3",
            fg="white",
            width=12,
        )
        btn_retrieve.pack(pady=4)

        btn_edit = tk.Button(
            frame_actions,
            text="Edit Entry",
            command=self.handle_edit,
            bg="#FF9800",
            fg="white",
            width=12,
        )
        btn_edit.pack(pady=4)

        btn_delete = tk.Button(
            frame_actions,
            text="Delete Entry",
            command=self.handle_delete,
            bg="#F44336",
            fg="white",
            width=12,
        )
        btn_delete.pack(pady=4)

        self.refresh_service_list()
        self.add_footer()

    def refresh_service_list(self):
        self.lst_services.delete(0, tk.END)
        for service in self.vault_data["passwords"].keys():
            self.lst_services.insert(tk.END, service)

    def handle_save(self):
        service = self.ent_service.get().strip().lower()
        password = self.ent_password.get().strip()

        if not service or not password:
            messagebox.showwarning(
                "Input Warning", "Service name and password are required."
            )
            return

        encrypted = encrypt_data(password, self.key).decode("utf-8")
        self.vault_data["passwords"][service] = encrypted
        save_vault_data(self.vault_data)

        messagebox.showinfo("Saved", f"Password for '{service}' saved successfully!")
        self.ent_service.delete(0, tk.END)
        self.ent_password.delete(0, tk.END)
        self.refresh_service_list()

    def handle_retrieve(self):
        selected = self.lst_services.curselection()
        if not selected:
            messagebox.showwarning(
                "Selection Warning", "Please select a service from the list."
            )
            return

        service = self.lst_services.get(selected[0])
        encrypted = self.vault_data["passwords"][service]

        try:
            decrypted = decrypt_data(encrypted.encode("utf-8"), self.key)
            messagebox.showinfo(
                "Decrypted Password", f"Service: {service}\nPassword: {decrypted}"
            )
        except Exception:
            messagebox.showerror("Error", "Failed to decrypt password.")

    def handle_edit(self):
        selected = self.lst_services.curselection()
        if not selected:
            messagebox.showwarning(
                "Selection Warning", "Please select a service to edit."
            )
            return

        service = self.lst_services.get(selected[0])

        new_password = simpledialog.askstring(
            "Edit Password",
            f"Enter new password for '{service}':",
            show="*",
            parent=self.root,
        )

        if new_password:
            encrypted = encrypt_data(new_password, self.key).decode("utf-8")
            self.vault_data["passwords"][service] = encrypted
            save_vault_data(self.vault_data)
            messagebox.showinfo("Updated", f"Password for '{service}' updated!")

    def handle_delete(self):
        selected = self.lst_services.curselection()
        if not selected:
            messagebox.showwarning(
                "Selection Warning", "Please select a service to delete."
            )
            return

        service = self.lst_services.get(selected[0])

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the entry for '{service}'?",
        )
        if confirm:
            del self.vault_data["passwords"][service]
            save_vault_data(self.vault_data)
            self.refresh_service_list()
            messagebox.showinfo("Deleted", f"Entry for '{service}' deleted.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordVaultApp(root)
    root.mainloop()