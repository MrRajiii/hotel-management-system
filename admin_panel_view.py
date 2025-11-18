# admin_panel_view.py

import customtkinter
from db_manager import DBManager, Guest, Room
from tkinter import messagebox
from datetime import datetime, date


class AdminPanelView(customtkinter.CTkFrame):
    def __init__(self, master, db_manager, app_controller):
        super().__init__(master)
        self.db_manager = db_manager
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self, text="Hotel Administration Panel", font=customtkinter.CTkFont(
            size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        self.tab_view.add("Guest Management")
        self.tab_view.add("Room Management")
        self.tab_view.add("Housekeeping")
        self.tab_view.add("Reservations")
        self.tab_view.add("Reporting")

        self.tab_view.tab("Guest Management").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Guest Management").grid_rowconfigure(1, weight=1)

        self.tab_view.tab("Room Management").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Room Management").grid_rowconfigure(1, weight=1)

        self.tab_view.tab("Housekeeping").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Housekeeping").grid_rowconfigure(1, weight=1)

        self.tab_view.tab("Reservations").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Reservations").grid_rowconfigure(1, weight=1)

        self.tab_view.tab("Reporting").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Reporting").grid_rowconfigure(1, weight=1)

        self._setup_guest_management_tab()
        self._setup_room_management_tab()
        self._setup_housekeeping_tab()
        self._setup_reservation_tab()
        self._setup_reporting_tab()

    # --- Guest Management Tab Methods ---

    def _setup_guest_management_tab(self):
        search_frame = customtkinter.CTkFrame(
            self.tab_view.tab("Guest Management"))
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(search_frame, text="Search Guest:").grid(
            row=0, column=0, padx=10, pady=10)
        self.guest_search_entry = customtkinter.CTkEntry(
            search_frame, placeholder_text="Name, Email, or Phone")
        self.guest_search_entry.grid(
            row=0, column=1, padx=10, pady=10, sticky="ew")
        customtkinter.CTkButton(search_frame, text="Search", command=self.search_guests).grid(
            row=0, column=2, padx=10, pady=10)

        self.guest_results_frame = customtkinter.CTkScrollableFrame(
            self.tab_view.tab("Guest Management"), label_text="Search Results")
        self.guest_results_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.guest_results_frame.grid_columnconfigure(0, weight=1)

        self.search_guests()

    def search_guests(self):
        query = self.guest_search_entry.get()
        results = self.db_manager.search_guests(query)

        for widget in self.guest_results_frame.winfo_children():
            widget.destroy()

        if not results:
            customtkinter.CTkLabel(
                self.guest_results_frame, text=f"No guests found matching '{query}'. Showing all guests if query is empty.").pack(pady=20)
            return

        headers = ["ID", "Name", "Email", "Phone", "Blacklisted", "Action"]
        for col, header in enumerate(headers):
            customtkinter.CTkLabel(self.guest_results_frame, text=header, font=customtkinter.CTkFont(
                weight="bold")).grid(row=0, column=col, padx=10, pady=5)

        for row_idx, guest in enumerate(results, start=1):
            customtkinter.CTkLabel(self.guest_results_frame, text=guest['id']).grid(
                row=row_idx, column=0, padx=10, pady=5)
            customtkinter.CTkLabel(self.guest_results_frame, text=guest['name']).grid(
                row=row_idx, column=1, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.guest_results_frame, text=guest['email']).grid(
                row=row_idx, column=2, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.guest_results_frame, text=guest['phone']).grid(
                row=row_idx, column=3, padx=10, pady=5)

            status_text = "Yes" if guest['blacklisted'] else "No"
            status_color = "red" if guest['blacklisted'] else "green"
            customtkinter.CTkLabel(self.guest_results_frame, text=status_text, text_color=status_color).grid(
                row=row_idx, column=4, padx=10, pady=5)

            customtkinter.CTkButton(self.guest_results_frame, text="Edit", width=60,
                                    command=lambda g_id=guest['id']: self.open_guest_edit_popup(g_id)).grid(row=row_idx, column=5, padx=10, pady=5)

        self.guest_results_frame.grid_columnconfigure(1, weight=3)
        self.guest_results_frame.grid_columnconfigure(2, weight=3)
        self.guest_results_frame.grid_columnconfigure(0, weight=1)

    def open_guest_edit_popup(self, guest_id):
        guest = self.db_manager.get_guest_by_id(guest_id)
        if not guest:
            return

        edit_window = customtkinter.CTkToplevel(self.app_controller)
        edit_window.title(f"Edit Guest: {guest.first_name} {guest.last_name}")
        edit_window.geometry("400x350")

        edit_window.transient(self.app_controller)
        edit_window.grab_set()

        frame = customtkinter.CTkFrame(edit_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        fields = [
            ("First Name", "first_name", guest.first_name),
            ("Last Name", "last_name", guest.last_name),
            ("Email", "contact_email", guest.contact_email),
            ("Phone", "contact_phone", guest.contact_phone),
            ("Address", "address", guest.address),
        ]

        entry_widgets = {}
        for i, (label_text, key, value) in enumerate(fields):
            customtkinter.CTkLabel(
                frame, text=label_text + ":").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = customtkinter.CTkEntry(frame)
            entry.insert(0, value or "")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entry_widgets[key] = entry

        is_blacklisted_var = customtkinter.BooleanVar(
            value=guest.is_blacklisted)
        customtkinter.CTkCheckBox(frame, text="Blacklist Guest", variable=is_blacklisted_var).grid(
            row=len(fields), column=0, columnspan=2, pady=10)

        def save_changes():
            data = {key: entry_widgets[key].get()
                    for key in entry_widgets.keys()}
            data['is_blacklisted'] = is_blacklisted_var.get()

            success, message = self.db_manager.update_guest_profile(
                guest_id, data)

            if success:
                edit_window.destroy()
                self.search_guests()
            else:
                messagebox.showerror("Update Error", message)

        customtkinter.CTkButton(
            edit_window, text="Save Changes", command=save_changes).pack(pady=10)

    # --- Room Management Tab Methods ---

    def _setup_room_management_tab(self):
        room_tab = self.tab_view.tab("Room Management")

        controls_frame = customtkinter.CTkFrame(room_tab)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        customtkinter.CTkLabel(controls_frame, text="Manage Room Details and Rates",
                               font=customtkinter.CTkFont(weight="bold")).pack(padx=10, pady=10, side="left")

        customtkinter.CTkButton(controls_frame, text="Refresh List",
                                command=self.load_room_list).pack(padx=10, pady=10, side="right")

        self.room_list_frame = customtkinter.CTkScrollableFrame(
            room_tab, label_text="Hotel Rooms Inventory")
        self.room_list_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew")
        room_tab.grid_rowconfigure(1, weight=1)

        self.load_room_list()

    def load_room_list(self):
        for widget in self.room_list_frame.winfo_children():
            widget.destroy()

        rooms = self.db_manager.get_all_rooms()

        if not rooms:
            customtkinter.CTkLabel(
                self.room_list_frame, text="No rooms found in the database.").pack(pady=20)
            return

        headers = ["Room #", "Type",
                   "Rate ($)", "Capacity", "Status", "Description", "Action"]
        col_weights = [1, 2, 2, 1, 2, 4, 1]

        for col, header in enumerate(headers):
            customtkinter.CTkLabel(self.room_list_frame, text=header, font=customtkinter.CTkFont(
                weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="w")
            self.room_list_frame.grid_columnconfigure(
                col, weight=col_weights[col])

        for row_idx, room in enumerate(rooms, start=1):
            status_color = {'Available': 'green', 'Occupied': 'red', 'Needs Cleaning': 'orange',
                            'Out of Service': 'gray', 'Booked': 'blue'}.get(room['status'], 'blue')

            customtkinter.CTkLabel(self.room_list_frame, text=room['number']).grid(
                row=row_idx, column=0, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.room_list_frame, text=room['type']).grid(
                row=row_idx, column=1, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.room_list_frame, text=f"{room['price']:.2f}").grid(
                row=row_idx, column=2, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.room_list_frame, text=room['capacity']).grid(
                row=row_idx, column=3, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.room_list_frame, text=room['status'], text_color=status_color).grid(
                row=row_idx, column=4, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.room_list_frame, text=room['description'], wraplength=150).grid(
                row=row_idx, column=5, padx=10, pady=5, sticky="w")

            customtkinter.CTkButton(self.room_list_frame, text="Edit", width=60,
                                    command=lambda r_num=room['number']: self.open_room_edit_popup(r_num)).grid(row=row_idx, column=6, padx=10, pady=5)

    def open_room_edit_popup(self, room_number):
        room_data = self.db_manager.get_room_by_number(room_number)
        if not room_data:
            return

        edit_window = customtkinter.CTkToplevel(self.app_controller)
        edit_window.title(f"Edit Room {room_number}")
        edit_window.geometry("450x450")

        edit_window.transient(self.app_controller)
        edit_window.grab_set()

        frame = customtkinter.CTkFrame(edit_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        customtkinter.CTkLabel(frame, text=f"Room {room_number} - Current Status: {room_data['status']}", font=customtkinter.CTkFont(
            weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Room Type Dropdown
        customtkinter.CTkLabel(frame, text="Type:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w")
        room_types = ['Single', 'Double', 'Suite', 'Deluxe']
        type_var = customtkinter.StringVar(value=room_data['type'])
        type_dropdown = customtkinter.CTkOptionMenu(
            frame, values=room_types, variable=type_var)
        type_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Price Entry
        customtkinter.CTkLabel(
            frame, text="Rate ($/Night):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        price_entry = customtkinter.CTkEntry(frame)
        price_entry.insert(0, f"{room_data['price']:.2f}")
        price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Capacity Entry
        customtkinter.CTkLabel(frame, text="Capacity:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w")
        capacity_entry = customtkinter.CTkEntry(frame)
        capacity_entry.insert(0, str(room_data['capacity']))
        capacity_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Description Textbox
        customtkinter.CTkLabel(frame, text="Description:").grid(
            row=4, column=0, padx=10, pady=5, sticky="w")
        description_entry = customtkinter.CTkTextbox(frame, height=50)
        description_entry.insert("0.0", room_data['description'] or "")
        description_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Status Change Dropdown
        customtkinter.CTkLabel(frame, text="Set Status:").grid(
            row=5, column=0, padx=10, pady=10, sticky="w")
        status_options = ['Available', 'Needs Cleaning',
                          'Out of Service', 'Booked']
        if room_data['status'] == 'Occupied':
            status_dropdown = customtkinter.CTkLabel(
                frame, text="Cannot change status (Occupied)")
        else:
            status_dropdown = customtkinter.CTkOptionMenu(
                frame, values=status_options)
            status_dropdown.set(room_data['status'])

        status_dropdown.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        error_label = customtkinter.CTkLabel(frame, text="", text_color="red")
        error_label.grid(row=7, column=0, columnspan=2, pady=5)

        def save_changes():
            try:
                new_price = float(price_entry.get())
                new_capacity = int(capacity_entry.get())
                if new_price <= 0 or new_capacity <= 0:
                    raise ValueError(
                        "Price and Capacity must be positive numbers.")

                # 1. Update Details
                details_data = {
                    'room_type': type_var.get(),
                    'price_per_night': new_price,
                    'capacity': new_capacity,
                    'description': description_entry.get("1.0", "end-1c")
                }
                success_det, msg_det = self.db_manager.update_room_details(
                    room_number, details_data)

                # 2. Update Status (if not occupied)
                success_stat = True
                if room_data['status'] != 'Occupied':
                    new_status = status_dropdown.get()
                    # Only update if it's actually changed
                    if new_status != room_data['status']:
                        self.db_manager.update_room_status(
                            room_number, new_status)
                        success_stat = True

                if success_det or success_stat:
                    edit_window.destroy()
                    self.load_room_list()
                    self.app_controller.show_room_status_view()
                else:
                    error_label.configure(text=msg_det)

            except ValueError as e:
                error_label.configure(text=f"Input Error: {e}")
            except Exception as e:
                error_label.configure(text=f"Error: {e}")

        customtkinter.CTkButton(
            edit_window, text="Save Changes", command=save_changes).pack(pady=10)

    # --- Housekeeping Tab Methods ---

    def _setup_housekeeping_tab(self):
        hk_tab = self.tab_view.tab("Housekeeping")

        controls_frame = customtkinter.CTkFrame(hk_tab)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        customtkinter.CTkLabel(controls_frame, text="Rooms Needing Cleaning", font=customtkinter.CTkFont(
            weight="bold")).pack(padx=10, pady=10, side="left")

        customtkinter.CTkButton(controls_frame, text="Refresh List",
                                command=self.load_housekeeping_list).pack(padx=10, pady=10, side="right")

        self.hk_list_frame = customtkinter.CTkScrollableFrame(
            hk_tab, label_text="Cleaning Queue")
        self.hk_list_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew")
        hk_tab.grid_rowconfigure(1, weight=1)

        self.load_housekeeping_list()

    def load_housekeeping_list(self):
        for widget in self.hk_list_frame.winfo_children():
            widget.destroy()

        rooms = self.db_manager.get_rooms_needing_cleaning()

        if not rooms:
            customtkinter.CTkLabel(
                self.hk_list_frame, text="🎉 All rooms are clean!").pack(pady=20)
            return

        headers = ["Room #", "Type", "Price", "Description", "Action"]
        col_weights = [1, 2, 2, 4, 2]

        for col, header in enumerate(headers):
            customtkinter.CTkLabel(self.hk_list_frame, text=header, font=customtkinter.CTkFont(
                weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="w")
            self.hk_list_frame.grid_columnconfigure(
                col, weight=col_weights[col])

        for row_idx, room in enumerate(rooms, start=1):
            customtkinter.CTkLabel(self.hk_list_frame, text=room['number']).grid(
                row=row_idx, column=0, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.hk_list_frame, text=room['type']).grid(
                row=row_idx, column=1, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.hk_list_frame, text=f"${room['price']:.2f}").grid(
                row=row_idx, column=2, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.hk_list_frame, text=room['description'], wraplength=150).grid(
                row=row_idx, column=3, padx=10, pady=5, sticky="w")

            customtkinter.CTkButton(self.hk_list_frame, text="Mark Clean", fg_color="green", hover_color="#006400",
                                    command=lambda r_num=room['number']: self.mark_room_clean(r_num)).grid(row=row_idx, column=4, padx=10, pady=5)

    def mark_room_clean(self, room_number):
        success = self.db_manager.update_room_status(room_number, 'Available')

        if success:
            messagebox.showinfo(
                "Housekeeping", f"Room {room_number} marked as Available.")
            self.load_housekeeping_list()
            self.app_controller.show_room_status_view()
        else:
            messagebox.showerror("Housekeeping Error",
                                 f"Failed to update room {room_number} status.")

    # --- Reservation History Tab Methods ---

    def _setup_reservation_tab(self):
        res_tab = self.tab_view.tab("Reservations")

        controls_frame = customtkinter.CTkFrame(res_tab)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.columnconfigure((1, 3, 5), weight=1)

        # Row 0: Search and Filter
        customtkinter.CTkLabel(controls_frame, text="Search:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        self.res_search_entry = customtkinter.CTkEntry(
            controls_frame, placeholder_text="Guest Name or Room #")
        self.res_search_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")

        customtkinter.CTkLabel(controls_frame, text="Status:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w")
        self.res_status_var = customtkinter.StringVar(value="All")
        status_options = ['All', 'Paid', 'Unpaid']
        status_dropdown = customtkinter.CTkOptionMenu(
            controls_frame, values=status_options, variable=self.res_status_var)
        status_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        customtkinter.CTkButton(controls_frame, text="Search History", command=self.load_reservation_history).grid(
            row=0, column=5, padx=5, pady=5, sticky="e")

        # Row 1: Date Range
        customtkinter.CTkLabel(controls_frame, text="Start Date (YYYY-MM-DD):").grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.res_start_date_entry = customtkinter.CTkEntry(
            controls_frame, placeholder_text=f"e.g., {date.today().year}-01-01")
        self.res_start_date_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")

        customtkinter.CTkLabel(controls_frame, text="End Date (YYYY-MM-DD):").grid(
            row=1, column=2, padx=5, pady=5, sticky="w")
        self.res_end_date_entry = customtkinter.CTkEntry(
            controls_frame, placeholder_text=f"e.g., {date.today().strftime('%Y-%m-%d')}")
        self.res_end_date_entry.grid(
            row=1, column=3, padx=5, pady=5, sticky="ew")

        self.res_list_frame = customtkinter.CTkScrollableFrame(
            res_tab, label_text="Reservation History")
        self.res_list_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.load_reservation_history()

    def load_reservation_history(self):
        for widget in self.res_list_frame.winfo_children():
            widget.destroy()

        search_query = self.res_search_entry.get()
        status_filter = self.res_status_var.get()

        start_date_str = self.res_start_date_entry.get()
        end_date_str = self.res_end_date_entry.get()

        # Convert date strings to date objects
        try:
            start_date = datetime.strptime(
                start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(
                end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            customtkinter.CTkLabel(
                self.res_list_frame, text="Error: Invalid date format. Use YYYY-MM-DD.", text_color="red").pack(pady=20)
            return

        success, results = self.db_manager.get_reservation_history(
            search_query=search_query,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date
        )

        if not success:
            customtkinter.CTkLabel(
                self.res_list_frame, text=results, text_color="red").pack(pady=20)
            return

        if not results:
            customtkinter.CTkLabel(
                self.res_list_frame, text="No matching reservations found.").pack(pady=20)
            return

        headers = ["ID", "Room #", "Guest Name",
                   "Check-in", "Check-out", "Bill Total", "Status"]
        col_weights = [1, 1, 3, 2, 2, 2, 1]

        for col, header in enumerate(headers):
            customtkinter.CTkLabel(self.res_list_frame, text=header, font=customtkinter.CTkFont(
                weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="w")
            self.res_list_frame.grid_columnconfigure(
                col, weight=col_weights[col])

        for row_idx, res in enumerate(results, start=1):
            status_text = "Paid" if res['is_paid'] else "UNPAID"
            status_color = "green" if res['is_paid'] else "red"

            customtkinter.CTkLabel(self.res_list_frame, text=res['booking_id']).grid(
                row=row_idx, column=0, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.res_list_frame, text=res['room_number']).grid(
                row=row_idx, column=1, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.res_list_frame, text=res['guest_name']).grid(
                row=row_idx, column=2, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.res_list_frame, text=res['check_in']).grid(
                row=row_idx, column=3, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.res_list_frame, text=res['check_out']).grid(
                row=row_idx, column=4, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.res_list_frame, text=f"${res['bill']:.2f}", font=customtkinter.CTkFont(
                weight="bold")).grid(row=row_idx, column=5, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(self.res_list_frame, text=status_text, text_color=status_color).grid(
                row=row_idx, column=6, padx=10, pady=5, sticky="w")

    # --- Reporting Tab Methods ---

    def _setup_reporting_tab(self):
        report_tab = self.tab_view.tab("Reporting")

        controls_frame = customtkinter.CTkFrame(report_tab)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.columnconfigure((1, 3), weight=1)

        # Date Range Selection
        customtkinter.CTkLabel(controls_frame, text="Start Date (YYYY-MM-DD):").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        self.report_start_date_entry = customtkinter.CTkEntry(
            controls_frame, placeholder_text=f"{date.today().year}-01-01")
        self.report_start_date_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")

        customtkinter.CTkLabel(controls_frame, text="End Date (YYYY-MM-DD):").grid(
            row=0, column=2, padx=5, pady=5, sticky="w")
        self.report_end_date_entry = customtkinter.CTkEntry(
            controls_frame, placeholder_text=f"{date.today().strftime('%Y-%m-%d')}")
        self.report_end_date_entry.grid(
            row=0, column=3, padx=5, pady=5, sticky="ew")

        customtkinter.CTkButton(controls_frame, text="Generate Report",
                                command=self.generate_revenue_report).grid(row=0, column=4, padx=5, pady=5)

        self.report_display_frame = customtkinter.CTkFrame(
            report_tab, fg_color="transparent")
        self.report_display_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.report_display_frame.columnconfigure((0, 1), weight=1)

        # Initial call to populate with default dates (or show error)
        self.generate_revenue_report(initial_load=True)

    def generate_revenue_report(self, initial_load=False):
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()

        start_date_str = self.report_start_date_entry.get()
        end_date_str = self.report_end_date_entry.get()

        # Use default dates for initial load if entries are empty
        if initial_load and not start_date_str and not end_date_str:
            start_date_str = f"{date.today().year}-01-01"
            end_date_str = date.today().strftime('%Y-%m-%d')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            customtkinter.CTkLabel(
                self.report_display_frame, text="Error: Please enter dates in YYYY-MM-DD format.", text_color="red").pack(pady=20)
            return

        success, results = self.db_manager.get_revenue_report(
            start_date, end_date)

        if not success:
            customtkinter.CTkLabel(
                self.report_display_frame, text=f"Report Generation Error: {results}", text_color="red").pack(pady=20)
            return

        # --- Display KPIs ---

        customtkinter.CTkLabel(self.report_display_frame,
                               text=f"Revenue Report: {results['start_date']} to {results['end_date']} ({results['period_days']} days)",
                               font=customtkinter.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # KPI Cards (2 columns)
        kpi_data = [
            ("💰 Total Revenue",
             f"${results['total_revenue']:.2f}", 1, 0, "green"),
            ("📈 Occupancy Rate",
             f"{results['occupancy_rate']:.2f}%", 1, 1, "blue"),
            ("💵 Average Daily Rate (ADR)",
             f"${results['adr']:.2f}", 2, 0, "orange"),
            ("📊 RevPAR", f"${results['revpar']:.2f}", 2, 1, "purple"),
        ]

        for title, value, row, col, color in kpi_data:
            card = customtkinter.CTkFrame(
                self.report_display_frame, fg_color="gray20", width=250)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.columnconfigure(0, weight=1)

            customtkinter.CTkLabel(card, text=title, font=customtkinter.CTkFont(
                weight="bold")).pack(pady=(10, 5))
            customtkinter.CTkLabel(card, text=value, font=customtkinter.CTkFont(
                size=24, weight="bold"), text_color=color).pack(pady=(5, 10))

        # Detailed Metrics (Below KPIs)
        customtkinter.CTkLabel(self.report_display_frame,
                               text="Detailed Metrics",
                               font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=3, column=0, columnspan=2, pady=(30, 10), sticky="w")

        detail_frame = customtkinter.CTkFrame(
            self.report_display_frame, fg_color="transparent")
        detail_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        detail_frame.columnconfigure((0, 2), weight=1)

        details = [
            ("Total Room Nights Available:", f"{results['available_nights']}"),
            ("Total Room Nights Occupied:", f"{results['occupied_nights']}"),
            ("Total Rooms in Hotel:", f"{results['total_rooms']}"),
        ]

        for i, (label, value) in enumerate(details):
            customtkinter.CTkLabel(detail_frame, text=label).grid(
                row=i, column=0, padx=10, pady=2, sticky="w")
            customtkinter.CTkLabel(detail_frame, text=value, font=customtkinter.CTkFont(
                weight="bold")).grid(row=i, column=1, padx=10, pady=2, sticky="e")
