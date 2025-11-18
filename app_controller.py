# app_controller.py

import customtkinter
from db_manager import DBManager
from room_status_view import RoomStatusView
from admin_panel_view import AdminPanelView
from login_view import LoginView  # NEW IMPORT
from tkinter import messagebox  # NEW IMPORT


class AppController(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.db_manager = DBManager()

        # --- Authentication State ---
        self.is_logged_in = False
        self.current_user = None
        self.user_role = None
        # --- END NEW ---

        self.title("Hotel Management System")
        self.geometry("1000x700")
        customtkinter.set_appearance_mode("Dark")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- View initialization ---
        self.login_view = LoginView(
            master=self, app_controller=self, db_manager=self.db_manager)
        self.room_status_view = RoomStatusView(
            master=self, db_manager=self.db_manager, app_controller=self)
        self.admin_panel_view = AdminPanelView(
            master=self, db_manager=self.db_manager, app_controller=self)

        # Start with the Login View
        self.show_login_view()

    # --- State Management Methods ---

    def set_logged_in_user(self, username, role):
        self.is_logged_in = True
        self.current_user = username
        self.user_role = role
        self.title(f"HMS - Logged in as: {username} ({role})")

    def logout_user(self):
        self.is_logged_in = False
        self.current_user = None
        self.user_role = None
        self.title("Hotel Management System")
        self.show_login_view()

    # --- View Switching Methods ---

    def show_view(self, view_instance):
        """Helper to hide all views and show the target view."""
        for view in [self.login_view, self.room_status_view, self.admin_panel_view]:
            view.grid_forget()

        view_instance.grid(row=0, column=0, sticky="nsew")

    def show_login_view(self):
        self.show_view(self.login_view)

    def show_room_status_view(self):
        if self.is_logged_in:
            # Note: RoomStatusView needs a logout button added to its UI!
            self.room_status_view.update_status_list()
            self.show_view(self.room_status_view)
        else:
            self.show_login_view()

    def show_admin_panel(self):
        # Only allow access if the user is logged in AND is an Admin
        if self.is_logged_in and self.user_role == 'Admin':
            self.admin_panel_view.load_room_list()
            self.show_view(self.admin_panel_view)
        elif self.is_logged_in:
            messagebox.showwarning(
                "Access Denied", "You do not have administrative privileges.")
            # If they aren't admin, send them back to the main room status screen
            self.show_room_status_view()
        else:
            self.show_login_view()


if __name__ == "__main__":
    # This is the application entry point
    app = AppController()
    app.mainloop()
