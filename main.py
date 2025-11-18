# main.py

import customtkinter
from db_manager import DBManager, Room
from room_view import RoomStatusView
from admin_panel_view import AdminPanelView


class HotelManagerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Hotel Management System (HMS)")
        customtkinter.set_appearance_mode("System")

        # --- WINDOW FIX & CENTERING ---

        self.window_width = 1000
        self.window_height = 700

        # Set the initial size
        self.geometry(f"{self.window_width}x{self.window_height}")

        # Prevent the user from resizing the window
        self.resizable(False, False)

        # Center the window on the screen
        self.set_center_geometry()

        # If the window can still be moved, you can use this more drastic solution:
        # self.overrideredirect(True) # WARNING: Removes the title bar and requires a custom exit button!

        # --- END WINDOW FIX ---

        self.db_manager = DBManager()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_navigation_frame()
        self._setup_content_frame()

        self.show_room_status_view()

    def set_center_geometry(self):
        """Calculates the center position and applies the geometry."""

        # Forces the window manager to calculate dimensions immediately
        self.update_idletasks()

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position to center the window
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)

        # Set the final geometry (width x height + x_offset + y_offset)
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def _setup_navigation_frame(self):
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.dash_button = customtkinter.CTkButton(
            self.navigation_frame, text="Dashboard", command=self.show_room_status_view)
        self.dash_button.grid(row=1, column=0, padx=20, pady=10)

        self.admin_button = customtkinter.CTkButton(
            self.navigation_frame, text="Admin Panel", command=self.show_admin_panel_view)
        self.admin_button.grid(row=2, column=0, padx=20, pady=10)

    def _setup_content_frame(self):
        self.content_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def show_room_status_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.room_view = RoomStatusView(
            self.content_frame, self.db_manager, self)
        self.room_view.grid(row=0, column=0, sticky="nsew")

    def show_admin_panel_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.admin_view = AdminPanelView(
            self.content_frame, self.db_manager, self)
        self.admin_view.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":

    db = DBManager()

    # Check and populate initial data
    if not db.session.query(Room).count():
        db.session.add_all([
            Room(room_number=101, room_type='Single', description='Basic room with 1 double bed',
                 capacity=2, price_per_night=100.0, status='Available'),
            Room(room_number=102, room_type='Double', description='Standard room with 2 double beds',
                 capacity=4, price_per_night=150.0, status='Available'),
            Room(room_number=201, room_type='Suite', description='Luxury suite with separate living area',
                 capacity=3, price_per_night=250.0, status='Available'),
            Room(room_number=202, room_type='Double', description='Standard room with 2 double beds',
                 capacity=4, price_per_night=150.0, status='Available'),
            Room(room_number=301, room_type='Single', description='Basic room with 1 double bed',
                 capacity=2, price_per_night=100.0, status='Available'),
        ])
        db.session.commit()
    db.session.close()

    app = HotelManagerApp()
    app.mainloop()
