# login_view.py

import customtkinter
from tkinter import messagebox
from db_manager import DBManager


class LoginView(customtkinter.CTkFrame):
    def __init__(self, master, app_controller, db_manager):
        super().__init__(master)
        self.app_controller = app_controller
        self.db_manager = db_manager

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(row=0, column=0, padx=20, pady=20)

        # --- UI Elements ---

        customtkinter.CTkLabel(self.frame, text="Hotel Management Login", font=customtkinter.CTkFont(
            size=20, weight="bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Username
        customtkinter.CTkLabel(self.frame, text="Username:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = customtkinter.CTkEntry(self.frame, width=200)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Password
        customtkinter.CTkLabel(self.frame, text="Password:").grid(
            row=2, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = customtkinter.CTkEntry(
            self.frame, width=200, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        # Enable Enter key press
        self.password_entry.bind("<Return>", lambda event: self.login_event())

        # Login Button
        self.login_button = customtkinter.CTkButton(
            self.frame, text="Login", command=self.login_event)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=20)

        # --- Check for Initial User Setup ---
        self._check_initial_setup()

    def _check_initial_setup(self):
        # Check if any users exist in the database
        users_count = self.db_manager.session.query(
            self.db_manager.User).count()
        if users_count == 0:
            messagebox.showinfo(
                "First Run Setup", "No users found. Creating a default 'admin' user now.")

            # Set a default user
            success, msg = self.db_manager.add_initial_user(
                "admin", "adminpass123", "Admin")
            if success:
                messagebox.showinfo(
                    "Setup Complete", f"Default admin user created. Please log in with:\nUsername: admin\nPassword: adminpass123")
            else:
                messagebox.showerror(
                    "Setup Error", "Failed to create initial admin user.")

    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        authenticated, role = self.db_manager.check_credentials(
            username, password)

        if authenticated:
            messagebox.showinfo("Success", f"Welcome, {username}!")
            # Store login state in the controller
            self.app_controller.set_logged_in_user(username, role)
            self.app_controller.show_room_status_view()
        else:
            messagebox.showerror(
                "Login Failed", "Invalid username or password.")
            self.password_entry.delete(0, 'end')
