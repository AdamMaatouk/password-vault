import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import crypto_utils
import vault_storage
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#0B0F17"          
PANEL_BG = "#131B2E"          
BORDER_COLOR = "#1E293B"      
PRIMARY_BLUE = "#3B82F6"      
PRIMARY_HOVER = "#2563EB"     
TEXT_MUTED = "#64748B"        
DANGER_RED = "#EF4444"        
DANGER_BG = "#2C151B"         

# ----------------------------------------------------------------------
# ADD / EDIT MODAL
# ----------------------------------------------------------------------
class AddPasswordModal(ctk.CTkToplevel):
    def __init__(self, parent, save_callback, edit_data=None):
        super().__init__(parent)
        self.save_callback = save_callback
        self.edit_data = edit_data
        
        title_text = "Edit Credential" if edit_data else "Add New Credential"
        self.title(title_text)
        self.geometry("400x540")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(
            self, text=title_text, font=("Segoe UI", 18, "bold"), text_color="white"
        ).pack(pady=(20, 15))

        fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=25)

        ctk.CTkLabel(fields_frame, text="SERVICE NAME", font=("Segoe UI", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.service_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. Google, GitHub", fg_color=PANEL_BG, border_color=BORDER_COLOR, height=40)
        self.service_entry.pack(fill="x", pady=(2, 12))

        ctk.CTkLabel(fields_frame, text="USERNAME / EMAIL", font=("Segoe UI", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.user_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. alex@example.com", fg_color=PANEL_BG, border_color=BORDER_COLOR, height=40)
        self.user_entry.pack(fill="x", pady=(2, 12))

        ctk.CTkLabel(fields_frame, text="PASSWORD", font=("Segoe UI", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        
        # --- PASSWORD ENTRY WITH EMBEDDED VIEW BUTTON ---
        self.pwd_entry = ctk.CTkEntry(fields_frame, placeholder_text="Enter password", show="•", fg_color=PANEL_BG, border_color=BORDER_COLOR, height=40)
        self.pwd_entry.pack(fill="x", pady=(2, 12))

        def toggle_password_visibility():
            if self.pwd_entry.cget("show") == "•":
                self.pwd_entry.configure(show="")
                toggle_btn.configure(text_color=PRIMARY_BLUE)
            else:
                self.pwd_entry.configure(show="•")
                toggle_btn.configure(text_color=TEXT_MUTED)

        toggle_btn = ctk.CTkButton(
            self.pwd_entry,
            text="👁",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=PANEL_BG,
            text_color=TEXT_MUTED,
            font=("Segoe UI", 12),
            command=toggle_password_visibility
        )
        toggle_btn.place(relx=0.98, rely=0.5, anchor="e")
        # ------------------------------------------------

        ctk.CTkLabel(fields_frame, text="CATEGORY", font=("Segoe UI", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.category_opt = ctk.CTkOptionMenu(
            fields_frame, 
            values=["Work", "Social", "Finance", "Shopping", "Entertainment"],
            fg_color=PANEL_BG, 
            button_color=BORDER_COLOR,
            dropdown_fg_color=PANEL_BG,
            height=38
        )
        self.category_opt.pack(fill="x", pady=(2, 20))

        if edit_data:
            self.service_entry.insert(0, edit_data.get("service", ""))
            self.service_entry.configure(state="disabled")  # Primary key fix
            self.user_entry.insert(0, edit_data.get("username", ""))
            self.pwd_entry.insert(0, edit_data.get("password", ""))
            self.category_opt.set(edit_data.get("category", "Work"))

        ctk.CTkButton(
            self, 
            text="Save Changes" if edit_data else "Save Credential", 
            font=("Segoe UI", 13, "bold"),
            fg_color=PRIMARY_BLUE, 
            hover_color=PRIMARY_HOVER,
            height=42,
            corner_radius=8,
            command=self.save_credential
        ).pack(fill="x", padx=25, pady=(0, 20))
        self.pwd_entry.bind("<Return>", lambda event: self.save_credential())

    def save_credential(self):
        service = self.service_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pwd_entry.get().strip()
        category = self.category_opt.get()

        if not service or not password:
            messagebox.showwarning("Missing Fields", "Please enter at least a service name and password.")
            return

        self.save_callback(service, username, password, category)
        self.destroy()


# ----------------------------------------------------------------------
# DETAIL VIEW MODAL
# ----------------------------------------------------------------------
class PasswordDetailModal(ctk.CTkToplevel):
    def __init__(self, parent, service, username, plain_password, meta, on_edit, on_delete):
        super().__init__(parent)
        self.title(f"{service} - PassVault")
        self.geometry("520x620")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, False)
        self.grab_set()

        self.parent = parent
        self.service = service
        self.username = username
        self.plain_password = plain_password
        self.meta = meta
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.pwd_visible = False

        # Navigation Header
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkButton(
            nav_frame, text="←", font=("Segoe UI", 16, "bold"), width=30, height=30,
            fg_color="transparent", hover_color=PANEL_BG, text_color="white",
            command=self.destroy
        ).pack(side="left")

        ctk.CTkLabel(nav_frame, text=service, font=("Segoe UI", 16, "bold"), text_color="white").pack(side="left", padx=10)

        # Title Card Section
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(5, 15))

        initial = service[0].upper() if service else "P"
        avatar = ctk.CTkLabel(
            title_frame, text=initial, font=("Segoe UI", 18, "bold"),
            fg_color="#1E293B", text_color=PRIMARY_BLUE,
            width=48, height=48, corner_radius=12
        )
        avatar.pack(side="left", padx=(0, 15))

        header_info = ctk.CTkFrame(title_frame, fg_color="transparent")
        header_info.pack(side="left")

        ctk.CTkLabel(header_info, text=service, font=("Segoe UI", 18, "bold"), text_color="white").pack(anchor="w")
        domain_sub = f"{service.lower().replace(' ', '')}.com"
        ctk.CTkLabel(header_info, text=domain_sub, font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(anchor="w")

        # Username / Email Card
        u_card = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10)
        u_card.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(u_card, text="USERNAME / EMAIL", font=("Segoe UI", 9, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=15, pady=(10, 0))
        u_inner = ctk.CTkFrame(u_card, fg_color="transparent")
        u_inner.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(u_inner, text=username, font=("Segoe UI", 13), text_color="white").pack(side="left")
        ctk.CTkButton(
            u_inner, text="📋 Copy", font=("Segoe UI", 11), width=65, height=28,
            fg_color="#1E293B", hover_color=PRIMARY_HOVER, text_color="white",
            command=lambda: self.copy_to_clipboard(username, "Username")
        ).pack(side="right")

        # Password Card
        p_card = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10)
        p_card.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(p_card, text="PASSWORD", font=("Segoe UI", 9, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=15, pady=(10, 0))
        p_inner = ctk.CTkFrame(p_card, fg_color="transparent")
        p_inner.pack(fill="x", padx=15, pady=(0, 10))

        self.pwd_display_lbl = ctk.CTkLabel(p_inner, text="•" * len(plain_password), font=("Segoe UI", 13), text_color="white")
        self.pwd_display_lbl.pack(side="left")

        p_btn_frame = ctk.CTkFrame(p_inner, fg_color="transparent")
        p_btn_frame.pack(side="right")

        self.eye_btn = ctk.CTkButton(
            p_btn_frame, text="👁", font=("Segoe UI", 13), width=32, height=28,
            fg_color="transparent", hover_color="#1E293B", text_color=TEXT_MUTED,
            command=self.toggle_password_visibility
        )
        self.eye_btn.pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            p_btn_frame, text="📋 Copy", font=("Segoe UI", 11), width=65, height=28,
            fg_color="#1E293B", hover_color=PRIMARY_HOVER, text_color="white",
            command=lambda: self.copy_to_clipboard(plain_password, "Password")
        ).pack(side="left")

        # Auto-hide Notice
        notice_frame = ctk.CTkFrame(self, fg_color="#122019", corner_radius=8)
        notice_frame.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(
            notice_frame, text="🟢 Password will auto-hide when you leave this screen.",
            font=("Segoe UI", 11), text_color="#10B981"
        ).pack(anchor="w", padx=12, pady=8)

        # Dates Display Card
        dates_card = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10)
        dates_card.pack(fill="x", padx=20, pady=6)

        created_str = meta.get("created_at", "Feb 3, 2025")
        modified_str = meta.get("updated_at", "Aug 15, 2026")

        d_row1 = ctk.CTkFrame(dates_card, fg_color="transparent")
        d_row1.pack(fill="x", padx=15, pady=(10, 4))
        ctk.CTkLabel(d_row1, text="Added", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(d_row1, text=created_str, font=("Segoe UI", 12), text_color="white").pack(side="right")

        d_row2 = ctk.CTkFrame(dates_card, fg_color="transparent")
        d_row2.pack(fill="x", padx=15, pady=(4, 10))
        ctk.CTkLabel(d_row2, text="Modified", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(d_row2, text=modified_str, font=("Segoe UI", 12), text_color="white").pack(side="right")

        # Action Buttons
        ctk.CTkButton(
            self, text="✏️  Edit Entry", font=("Segoe UI", 13, "bold"),
            fg_color=PANEL_BG, hover_color="#1E293B", text_color=PRIMARY_BLUE,
            height=40, corner_radius=10, command=self.handle_edit
        ).pack(fill="x", padx=20, pady=(12, 6))

        ctk.CTkButton(
            self, text="🗑️  Delete Entry", font=("Segoe UI", 13, "bold"),
            fg_color=DANGER_BG, hover_color="#3E1A20", text_color=DANGER_RED,
            height=40, corner_radius=10, command=self.handle_delete
        ).pack(fill="x", padx=20, pady=(0, 15))

    def toggle_password_visibility(self):
        self.pwd_visible = not self.pwd_visible
        if self.pwd_visible:
            self.pwd_display_lbl.configure(text=self.plain_password)
        else:
            self.pwd_display_lbl.configure(text="•" * len(self.plain_password))

    def copy_to_clipboard(self, value, item_name):
        self.clipboard_clear()
        self.clipboard_append(value)
        messagebox.showinfo("Copied", f"{item_name} copied to clipboard!")

    def handle_edit(self):
        self.destroy()
        self.on_edit(self.service, self.username, self.plain_password, self.meta.get("category", "Work"))

    def handle_delete(self):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{self.service}'?"):
            self.destroy()
            self.on_delete(self.service)


# ----------------------------------------------------------------------
# MAIN APPLICATION
# ----------------------------------------------------------------------
class ModernPassVault(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PassVault")
        self.geometry("980x650")
        self.configure(fg_color=BG_COLOR)
        self.iconbitmap(resource_path("app_logo.ico"))

        self.key = None
        self.vault_data = None
        self.current_category = "All"

        # Check setup status on launch (Removed duplicate call below)
        if vault_storage.vault_exists():
            self.show_login_screen()
        else:
            self.show_setup_screen()

    def clear_screen(self):
        """Wipes all packed frames to prevent UI stacking."""
        for widget in self.winfo_children():
            widget.destroy()

    # ----------------------------------------------------------------------
    # SETUP & LOGIN VIEWS
    # ----------------------------------------------------------------------
    def show_setup_screen(self):
        self.clear_screen()
        self.setup_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.setup_frame.pack(expand=True)

        setup_badge = ctk.CTkFrame(
            self.setup_frame, 
            fg_color=PRIMARY_BLUE, 
            corner_radius=16, 
            width=72, 
            height=72
        )
        setup_badge.pack(anchor="center", pady=(0, 15))
        setup_badge.pack_propagate(False)

        ctk.CTkLabel(
            setup_badge, 
            text="🔒", 
            font=("Segoe UI", 32), 
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.setup_frame, text="Welcome to PassVault", font=("Segoe UI", 26, "bold"), text_color="white").pack(pady=(0, 2))
        ctk.CTkLabel(self.setup_frame, text="Create a master password to protect your vault.", font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=(0, 25))

        input_container = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        input_container.pack(fill="x", pady=5)

        # --- CREATE MASTER PASSWORD ---
        ctk.CTkLabel(input_container, text="CREATE MASTER PASSWORD", font=("Segoe UI", 11, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 5))

        pwd_box1 = ctk.CTkFrame(input_container, fg_color=PANEL_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=8, width=320, height=45)
        pwd_box1.pack(fill="x", pady=(0, 15))
        pwd_box1.pack_propagate(False)

        self.new_pwd_entry = ctk.CTkEntry(
            pwd_box1, 
            placeholder_text="🔑  New master password", 
            show="•",
            fg_color="transparent", 
            border_width=0, 
            text_color="white"
        )
        self.new_pwd_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.eye_btn1 = ctk.CTkButton(
            pwd_box1, 
            text="👁", 
            width=35, 
            fg_color="transparent",
            hover_color=PANEL_BG, 
            text_color=TEXT_MUTED,
            font=("Segoe UI", 14),
            command=lambda: self.toggle_password_visibility(self.new_pwd_entry, self.eye_btn1)
        )
        self.eye_btn1.pack(side="right", padx=(0, 5))

        # --- CONFIRM MASTER PASSWORD ---
        ctk.CTkLabel(input_container, text="CONFIRM MASTER PASSWORD", font=("Segoe UI", 11, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 5))

        pwd_box2 = ctk.CTkFrame(input_container, fg_color=PANEL_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=8, width=320, height=45)
        pwd_box2.pack(fill="x", pady=(0, 20))
        pwd_box2.pack_propagate(False)

        self.confirm_pwd_entry = ctk.CTkEntry(
            pwd_box2, 
            placeholder_text="🔑  Confirm master password", 
            show="•",
            fg_color="transparent", 
            border_width=0, 
            text_color="white"
        )
        self.confirm_pwd_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.confirm_pwd_entry.bind("<Return>", lambda e: self.create_vault())

        self.eye_btn2 = ctk.CTkButton(
            pwd_box2, 
            text="👁", 
            width=35, 
            fg_color="transparent",
            hover_color=PANEL_BG, 
            text_color=TEXT_MUTED,
            font=("Segoe UI", 14),
            command=lambda: self.toggle_password_visibility(self.confirm_pwd_entry, self.eye_btn2)
        )
        self.eye_btn2.pack(side="right", padx=(0, 5))

        ctk.CTkButton(
            self.setup_frame, text="✨ Create Vault", font=("Segoe UI", 14, "bold"),
            width=320, height=45, fg_color=PRIMARY_BLUE, hover_color=PRIMARY_HOVER,
            corner_radius=8, command=self.create_vault
        ).pack(pady=(0, 20))

        ctk.CTkLabel(self.setup_frame, text="⚠️ Warning: If you lose this password, your vault cannot be recovered.", font=("Segoe UI", 11), text_color=TEXT_MUTED).pack()

    def load_vault_entries(self):
        # 1. Clear existing card widgets
        for widget in self.card_container.winfo_children():
            widget.destroy()

        search_query = self.search_entry.get().lower().strip() if hasattr(self, "search_entry") else ""
        passwords = self.vault_data.get("passwords", {})
        metadata = self.vault_data.get("metadata", {})

        active_cat = getattr(self, "selected_category", "All").strip()

        for service, encrypted_pass in passwords.items():
            # Get metadata dictionary for the service
            entry_meta = metadata.get(service, {})
            if not isinstance(entry_meta, dict):
                entry_meta = {}

            username = entry_meta.get("username", "")
            
            # Extract category & favorite strictly from entry_meta
            item_category = str(entry_meta.get("category", "")).strip()
            is_favorite = bool(entry_meta.get("favorite", False))

            # --- CATEGORY MATCHING ---
            if active_cat == "Favorites":
                # Show ANY item where favorite is True, regardless of its category
                matches_cat = is_favorite
            elif active_cat == "All":
                # Show ALL items
                matches_cat = True
            else:
                # Show ONLY items matching the active category name exactly (case-insensitive)
                matches_cat = (item_category.lower() == active_cat.lower())

            # --- SEARCH MATCHING ---
            matches_search = (search_query in service.lower()) or (search_query in username.lower())

            # Render card ONLY if both category and search match
            if matches_cat and matches_search:
                self.create_card(service, username, encrypted_pass, entry_meta)

    def create_vault(self):
        pwd = self.new_pwd_entry.get().strip()
        confirm_pwd = self.confirm_pwd_entry.get().strip()

        if not pwd or not confirm_pwd:
            messagebox.showwarning("Missing Input", "Please enter and confirm your master password.")
            return

        if pwd != confirm_pwd:
            messagebox.showerror("Mismatch", "Passwords do not match. Please try again.")
            return

        if len(pwd) < 6:
            messagebox.showwarning("Weak Password", "Master password must be at least 6 characters.")
            return

        try:
            self.key = crypto_utils.generate_key(pwd)
            
            self.vault_data = {
                "auth_check": crypto_utils.encrypt_data("vault_authenticated", self.key),
                "passwords": {},
                "metadata": {}
            }
            
            vault_storage.save_vault_data(self.vault_data)
            self.clear_screen()
            self.show_dashboard()
            messagebox.showinfo("Success", "Master password set! Your vault is ready.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create vault: {str(e)}")

    def show_login_screen(self):
        self.clear_screen()
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.login_frame.pack(expand=True)

        login_badge = ctk.CTkFrame(
            self.login_frame, 
            fg_color=PRIMARY_BLUE, 
            corner_radius=16, 
            width=72, 
            height=72
        )
        login_badge.pack(anchor="center", pady=(0, 15))
        login_badge.pack_propagate(False)

        ctk.CTkLabel(
            login_badge, 
            text="🔒", 
            font=("Segoe UI", 32), 
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="PassVault", font=("Segoe UI", 26, "bold"), text_color="white").pack(pady=(0, 2))
        ctk.CTkLabel(self.login_frame, text="Your passwords. Encrypted locally.", font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=(0, 25))

        input_container = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        input_container.pack(fill="x", pady=5)

        ctk.CTkLabel(input_container, text="MASTER PASSWORD", font=("Segoe UI", 11, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 5))

        # --- Container Box ---
        pwd_box = ctk.CTkFrame(input_container, fg_color=PANEL_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=8, width=320, height=45)
        pwd_box.pack(fill="x", pady=(0, 15))
        pwd_box.pack_propagate(False)

        # --- Entry Field (expands to fill left side) ---
        self.pwd_entry = ctk.CTkEntry(
            pwd_box, 
            placeholder_text="🔒  Enter master password", 
            show="•",
            fg_color="transparent", 
            border_width=0, 
            text_color="white"
        )
        self.pwd_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.pwd_entry.bind("<Return>", lambda e: self.unlock_vault())

        # --- Static Eye Toggle (anchored to far right) ---
        self.login_eye_btn = ctk.CTkButton(
            pwd_box, 
            text="👁", 
            width=35, 
            fg_color="transparent",
            hover_color=PANEL_BG,
            text_color=TEXT_MUTED,
            font=("Segoe UI", 14),
            command=lambda: self.toggle_password_visibility(self.pwd_entry, self.login_eye_btn)
        )
        self.login_eye_btn.pack(side="right", padx=(0, 5))

        ctk.CTkButton(
            self.login_frame, text="🔓 Unlock Vault", font=("Segoe UI", 14, "bold"),
            width=320, height=45, fg_color=PRIMARY_BLUE, hover_color=PRIMARY_HOVER,
            corner_radius=8, command=self.unlock_vault
        ).pack(pady=(0, 20))

        # --- FORGOT PASSWORD BUTTON ---
        forgot_btn = ctk.CTkButton(
            self.login_frame, 
            text="Forgot Master Password?", 
            font=("Segoe UI", 11),
            fg_color="transparent", 
            text_color=TEXT_MUTED,
            hover_color=PANEL_BG,
            height=28,
            command=self.open_forgot_password_modal
        )
        forgot_btn.pack(pady=(8, 0))

        ctk.CTkLabel(self.login_frame, text="🟢 Protected with AES-256 encryption", font=("Segoe UI", 11), text_color="#10B981").pack()

        credit_lbl = ctk.CTkLabel(
            self.login_frame,  # Replace with your actual login frame variable name
            text="PassVault • Adam Maatouk", 
            font=("Segoe UI", 10), 
            text_color=TEXT_MUTED
        )
        credit_lbl.pack(side="bottom", pady=(15, 5))

    def unlock_vault(self):
        master_pwd = self.pwd_entry.get().strip()
        if not master_pwd:
            messagebox.showwarning("Input Required", "Please enter your master password.")
            return

        try:
            derived_key = crypto_utils.generate_key(master_pwd)
            data = vault_storage.load_vault_data()
            
            auth_marker = data.get("auth_check")
            if auth_marker:
                decrypted_check = crypto_utils.decrypt_data(auth_marker, derived_key)
                if decrypted_check != "vault_authenticated":
                    raise ValueError("Invalid Key")

            self.key = derived_key
            self.vault_data = data
            self.clear_screen()
            self.show_dashboard()
        except Exception:
            messagebox.showerror("Access Denied", "Incorrect master password. Please try again.")

    # ----------------------------------------------------------------------
    # DASHBOARD VIEW
    # ----------------------------------------------------------------------
    def show_dashboard(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(self.main_container, fg_color=BG_COLOR, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=(15, 0), pady=15)

        # --- BRAND HEADER ---
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            brand_frame, text="🔒", font=("Segoe UI", 16), 
            fg_color=PRIMARY_BLUE, text_color="white", corner_radius=10, width=38, height=38
        ).pack(side="left", padx=(0, 10))

        brand_text = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text.pack(side="left")
        ctk.CTkLabel(brand_text, text="PassVault", font=("Segoe UI", 16, "bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(brand_text, text="🟢 Secured locally", font=("Segoe UI", 10), text_color="#10B981").pack(anchor="w")

        # --- CATEGORIES SECTION CONTAINER ---
        cat_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        cat_container.pack(fill="both", expand=True)

        ctk.CTkLabel(cat_container, text="CATEGORIES", font=("Segoe UI", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 5))

        self.cat_buttons = {}
        categories = [
            ("All", "💼"), ("Favorites", "⭐"), ("Work", "📁"), 
            ("Social", "👤"), ("Finance", "💳"), ("Shopping", "🛒"), ("Entertainment", "🎬")
        ]

        for cat, icon in categories:
            btn = ctk.CTkButton(
                cat_container, 
                text=f"{icon}  {cat}", 
                font=("Segoe UI", 12),
                anchor="w",
                compound="left",
                fg_color=PANEL_BG if cat == "All" else "transparent",
                text_color="white",
                hover_color=PANEL_BG,
                height=38,
                corner_radius=8,
                command=lambda c=cat: self.select_category(c)
            )
            btn.pack(fill="x", pady=2)
            self.cat_buttons[cat] = btn

        # --- ADD PASSWORD BUTTON ---
        ctk.CTkButton(
            self.sidebar,
            text="+ Add Password",
            font=("Segoe UI", 13, "bold"),
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_HOVER,
            height=42,
            corner_radius=10,
            command=self.open_add_modal
        ).pack(side="bottom", fill="x", pady=(10, 0))
        # --- ABOUT BUTTON (Bottom of Sidebar) ---
        about_btn = ctk.CTkButton(
            self.sidebar, # or cat_container if you want it inside the same wrapper
            text="ℹ️  About PassVault", 
            font=("Segoe UI", 12),
            anchor="w",
            compound="left",
            fg_color="transparent",
            text_color=TEXT_MUTED,
            hover_color=PANEL_BG,
            height=38,
            corner_radius=8,
            command=self.open_about_modal
        )
        about_btn.pack(side="bottom", fill="x", padx=12, pady=(5, 10))

        # --- MAIN CONTENT PANEL ---
        self.content_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_panel.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        search_frame = ctk.CTkFrame(self.content_panel, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))

        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="🔍  Search passwords, apps, or accounts...", 
            fg_color=PANEL_BG, 
            border_color=BORDER_COLOR,
            text_color="white",
            height=42
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_vault_entries())

        self.section_title = ctk.CTkLabel(
            self.content_panel, text="All Passwords", font=("Segoe UI", 15, "bold"), text_color="white"
        )
        self.section_title.pack(anchor="w", pady=(0, 10))

        self.card_container = ctk.CTkScrollableFrame(self.content_panel, fg_color="transparent")
        self.card_container.pack(fill="both", expand=True)
        self.selected_category = "All"
        self.load_vault_entries()

    # ----------------------------------------------------------------------
    # CONTROLLER LOGIC
    # ----------------------------------------------------------------------
    def select_category(self, cat):
        # Save the active category string cleanly
        self.selected_category = str(cat).strip()
        self.section_title.configure(
            text=f"{self.selected_category} Passwords" if self.selected_category != "All" else "All Passwords"
        )

        # Highlight sidebar active tab
        for name, btn in self.cat_buttons.items():
            btn.configure(fg_color=PANEL_BG if name == self.selected_category else "transparent")

        # Re-render cards for the newly selected category
        self.load_vault_entries()

    def get_filtered_passwords(self):
        """Filters passwords by selected category and search query."""
        query = self.search_entry.get().lower().strip() if hasattr(self, "search_entry") else ""
        passwords = self.vault_data.get("passwords", [])
        
        filtered = []
        for item in passwords:
            # Check category filter
            if self.selected_category == "Favorites":
                cat_match = item.get("favorite", False)
            elif self.selected_category == "All":
                cat_match = True
            else:
                cat_match = item.get("category") == self.selected_category

            # Check search query match
            search_match = (
                query in item.get("service", "").lower() or 
                query in item.get("username", "").lower()
            )
            
            if cat_match and search_match:
                filtered.append(item)
                
        return filtered

    def load_vault_entries(self):
        # 1. Clear current card widgets from UI
        for widget in self.card_container.winfo_children():
            widget.destroy()

        search_query = self.search_entry.get().lower().strip() if hasattr(self, "search_entry") else ""
        passwords = self.vault_data.get("passwords", {})
        metadata = self.vault_data.get("metadata", {})

        # Strictly pull from self.selected_category
        active_cat = getattr(self, "selected_category", "All").strip()

        for service, encrypted_pass in passwords.items():
            # Get metadata dictionary corresponding to the exact service key
            entry_meta = metadata.get(service, {})
            username = entry_meta.get("username", "")
            item_category = str(entry_meta.get("category", "")).strip()
            is_favorite = bool(entry_meta.get("favorite", False))

            # --- CATEGORY FILTERING LOGIC ---
            if active_cat == "Favorites":
                matches_cat = is_favorite
            elif active_cat == "All":
                matches_cat = True
            else:
                matches_cat = (item_category.lower() == active_cat.lower())

            # --- SEARCH QUERY LOGIC ---
            matches_search = (search_query in service.lower()) or (search_query in username.lower())

            # Only create card if both category and search match
            if matches_cat and matches_search:
                self.create_card(service, username, encrypted_pass, entry_meta)
    def create_card(self, service, username, encrypted_pass, meta):
        category = meta.get("category", "Work")
        
        card = ctk.CTkFrame(self.card_container, fg_color=PANEL_BG, corner_radius=10, cursor="hand2")
        card.pack(fill="x", pady=6)

        initial = service[0].upper() if service else "P"
        avatar = ctk.CTkLabel(
            card, text=initial, font=("Segoe UI", 16, "bold"),
            fg_color="#1E293B", text_color=PRIMARY_BLUE,
            width=40, height=40, corner_radius=20
        )
        avatar.pack(side="left", padx=15, pady=12)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="y", pady=10)

        lbl_s = ctk.CTkLabel(info_frame, text=service, font=("Segoe UI", 14, "bold"), text_color="white")
        lbl_s.pack(anchor="w")
        lbl_u = ctk.CTkLabel(info_frame, text=username, font=("Segoe UI", 12), text_color=TEXT_MUTED)
        lbl_u.pack(anchor="w")

        tag = ctk.CTkLabel(
            card, text=category, font=("Segoe UI", 10),
            fg_color="#1E293B", text_color=PRIMARY_BLUE,
            corner_radius=6, padx=8, pady=2
        )
        tag.pack(side="left", padx=15)

        # --- COPY BUTTON (Far Right) ---
        copy_btn = ctk.CTkButton(
            card, text="Copy", width=65, height=30,
            fg_color=PRIMARY_BLUE, hover_color=PRIMARY_HOVER,
            command=lambda s=service, ep=encrypted_pass: self.copy_password(s, ep)
        )
        copy_btn.pack(side="right", padx=(5, 15))

        # --- FAVORITE STAR BUTTON (Next to Copy) ---
        is_fav = meta.get("favorite", False)
        star_icon = "★" if is_fav else "☆"
        star_color = "white" if is_fav else TEXT_MUTED

        star_btn = ctk.CTkButton(
            card,
            text=star_icon,
            width=35,
            height=30,
            fg_color="transparent",
            hover_color=PANEL_BG,
            text_color=star_color,
            font=("Segoe UI", 16),
            command=lambda m=meta: self.toggle_favorite(m)
        )
        star_btn.pack(side="right", padx=(0, 2))

        def open_details(event=None):
            try:
                # Pass encrypted_pass string directly (no .encode('utf-8'))
                decrypted = crypto_utils.decrypt_data(encrypted_pass, self.key)
                PasswordDetailModal(
                    self, service, username, decrypted, meta,
                    on_edit=self.open_edit_modal,
                    on_delete=self.delete_credential
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to decrypt password: {str(e)}")

        for widget in [card, avatar, info_frame, lbl_s, lbl_u, tag]:
            widget.bind("<Button-1>", open_details)

    def copy_password(self, service, encrypted_pass):
        try:
            # Pass encrypted_pass string directly (no .encode('utf-8'))
            decrypted = crypto_utils.decrypt_data(encrypted_pass, self.key)
            self.clipboard_clear()
            self.clipboard_append(decrypted)
            messagebox.showinfo("Copied", f"Password for '{service}' copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt password: {str(e)}")

    def open_add_modal(self):
        AddPasswordModal(self, self.add_new_credential)

    def open_edit_modal(self, service, username, password, category):
        edit_data = {
            "service": service,
            "username": username,
            "password": password,
            "category": category
        }
        AddPasswordModal(self, self.add_new_credential, edit_data=edit_data)

    def add_new_credential(self, service, username, password, category):
        try:
            encrypted_str = crypto_utils.encrypt_data(password, self.key)

            if "passwords" not in self.vault_data:
                self.vault_data["passwords"] = {}
            if "metadata" not in self.vault_data:
                self.vault_data["metadata"] = {}

            now_str = datetime.now().strftime("%b %d, %Y")
            existing_created = self.vault_data["metadata"].get(service, {}).get("created_at", now_str)

            self.vault_data["passwords"][service] = encrypted_str
            self.vault_data["metadata"][service] = {
                "username": username,
                "category": category,
                "created_at": existing_created,
                "updated_at": now_str
            }

            vault_storage.save_vault_data(self.vault_data)
            self.load_vault_entries()
            messagebox.showinfo("Saved", f"Successfully saved entry for '{service}'.")
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Could not save password: {str(e)}")

    def delete_credential(self, service):
        if service in self.vault_data.get("passwords", {}):
            del self.vault_data["passwords"][service]
        if service in self.vault_data.get("metadata", {}):
            del self.vault_data["metadata"][service]

        vault_storage.save_vault_data(self.vault_data)
        self.load_vault_entries()
        messagebox.showinfo("Deleted", f"Deleted '{service}' from vault.")

    def toggle_password_visibility(self, entry_widget, button_widget):  
        """Toggles password visibility without changing icon dimensions or layout."""
        if entry_widget.cget("show") == "•":
            entry_widget.configure(show="")
            button_widget.configure(text_color=PRIMARY_BLUE)  # Highlights eye when visible
        else:
            entry_widget.configure(show="•")
            button_widget.configure(text_color=TEXT_MUTED)    # Dimmed eye when hidden

    def toggle_favorite(self, meta):
        """Toggles the favorite key in metadata, saves vault, and re-renders UI."""
        meta["favorite"] = not meta.get("favorite", False)

        # Save to disk
        vault_storage.save_vault_data(self.vault_data)

        # Re-render UI to update view (removes item from view if currently in Favorites tab and unfavorited)
        self.load_vault_entries()

    def open_about_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("About PassVault")
        modal.geometry("440x400")  # Widen modal slightly to prevent text clipping
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        # Main Container Frame
        frame = ctk.CTkFrame(modal, fg_color=BG_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Title & Badge
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 12))

        ctk.CTkLabel(
            header_frame, text="🔒 PassVault", font=("Segoe UI", 20, "bold"), text_color="white"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame, 
            text="Desktop Password Manager • v1.0.1", 
            font=("Segoe UI", 11), 
            text_color=TEXT_MUTED
        ).pack(anchor="w")

        # Developer & Designer Specs Box
        info_box = ctk.CTkFrame(frame, fg_color=PANEL_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        info_box.pack(fill="x", pady=(0, 12), padx=0)

        # --- SIDE-BY-SIDE CREATORS CONTAINER ---
        creators_container = ctk.CTkFrame(info_box, fg_color="transparent")
        creators_container.pack(fill="x", padx=12, pady=(10, 8))

        # Left Side: Developer
        dev_frame = ctk.CTkFrame(creators_container, fg_color="transparent")
        dev_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(dev_frame, text="DEVELOPER", font=("Segoe UI", 9, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(dev_frame, text="Adam Maatouk", font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(2, 0))

        # Vertical Divider Line in the Middle
        divider = ctk.CTkFrame(creators_container, width=1, height=35, fg_color=BORDER_COLOR)
        divider.pack(side="left", fill="y", padx=10)
        divider.pack_propagate(False)

        # Right Side: Designer
        des_frame = ctk.CTkFrame(creators_container, fg_color="transparent")
        des_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(des_frame, text="UX/UI DESIGNER", font=("Segoe UI", 9, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(des_frame, text="Lea Maatouk", font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(2, 0))
        # ---------------------------------------

        # Horizontal separator before security specs
        ctk.CTkFrame(info_box, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=12, pady=4)

        # Core Architecture Details
        arch_frame = ctk.CTkFrame(info_box, fg_color="transparent")
        arch_frame.pack(fill="x", padx=12, pady=(4, 10))

        ctk.CTkLabel(arch_frame, text="SECURITY ARCHITECTURE", font=("Segoe UI", 9, "bold"), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(
            arch_frame, 
            text="• 256-bit AES Encryption with PBKDF2 Key Derivation\n• Zero-Knowledge Local Storage Model\n• Dynamic Category Filtering & Custom UI System", 
            font=("Segoe UI", 11), 
            text_color="#10B981", 
            justify="left"
        ).pack(anchor="w", pady=(2, 0))

        # Project Summary / Description
        desc_lbl = ctk.CTkLabel(
            frame, 
            text="PassVault is a local-first credential management system engineered to securely store, categorize, and protect credentials using industry-standard cryptography.",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
            wraplength=390,
            justify="left"
        )
        desc_lbl.pack(fill="x", pady=(0, 12))

        # Close Button
        ctk.CTkButton(
            frame, 
            text="Close", 
            width=100, 
            height=32,
            fg_color=PRIMARY_BLUE, 
            hover_color=PRIMARY_HOVER, 
            command=modal.destroy
        ).pack(side="bottom")

    def open_forgot_password_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Reset Vault")
        modal.geometry("380x280")
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="⚠️ Reset Vault?", font=("Segoe UI", 16, "bold"), text_color="#EF4444"
        ).pack(pady=(20, 10))

        warning_text = (
            "Because PassVault uses zero-knowledge encryption, "
            "your master password cannot be recovered.\n\n"
            "Proceeding will permanently erase the current "
            "encrypted database so you can set up a new vault."
        )
        ctk.CTkLabel(
            modal, text=warning_text, font=("Segoe UI", 11), text_color=TEXT_MUTED, wraplength=330, justify="left"
        ).pack(padx=20, pady=(0, 20))

        def execute_wipe():
            # 1. Delete your local database file (replace "passvault.db" with your actual file path/name if different)
            import os
            db_file = "vault.json" 
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                except Exception as e:
                    print(f"Error removing database file: {e}")

            # 2. Close the modal and take the user back to the setup screen
            modal.destroy()
            self.show_setup_screen()  # Make sure this points to your function that builds the first-time setup UI

        ctk.CTkButton(
            modal, 
            text="Wipe Data & Reset", 
            fg_color="#EF4444", 
            hover_color="#DC2626",
            height=36,
            command=execute_wipe
        ).pack(fill="x", padx=25, pady=(0, 10))

if __name__ == "__main__":
    app = ModernPassVault()
    app.mainloop()