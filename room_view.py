# room_view.py

import customtkinter
from db_manager import DBManager, Charge, Reservation, Guest
from tkcalendar import Calendar
from tkinter import Frame, Toplevel
from datetime import date, datetime
from tkinter import messagebox


class RoomStatusView(customtkinter.CTkFrame):
    def __init__(self, master, db_manager, app_controller):
        super().__init__(master)
        self.db_manager = db_manager
        self.app_controller = app_controller
        self.detail_window = None
        # Store a reference to the entry widget that needs the calendar date
        self.date_entry_target = None

        self.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self, text="Room Status Dashboard", font=customtkinter.CTkFont(
            size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.room_grid_frame = customtkinter.CTkScrollableFrame(
            self, label_text="Hotel Rooms")
        self.room_grid_frame.grid(
            row=1, column=0, padx=20, pady=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        self.load_room_cards()

    def load_room_cards(self):
        for widget in self.room_grid_frame.winfo_children():
            widget.destroy()

        rooms = self.db_manager.get_room_status()
        cols = 4

        STATUS_COLORS = {
            'Available': 'green',
            'Occupied': 'red',
            'Needs Cleaning': 'orange',
            'Out of Service': 'gray',
            'Booked': 'blue'
        }

        for i, room in enumerate(rooms):
            row = i // cols
            col = i % cols

            room_card = customtkinter.CTkButton(
                self.room_grid_frame,
                text=f"Room {room['number']}\n({room['type']})\nStatus: {room['status']}",
                fg_color=STATUS_COLORS.get(room['status'], 'blue'),
                command=lambda r_num=room['number']: self.open_room_detail(
                    r_num)
            )
            room_card.grid(row=row, column=col, padx=10,
                           pady=10, sticky="nsew")

        for c in range(cols):
            self.room_grid_frame.grid_columnconfigure(c, weight=1)

    def open_room_detail(self, room_number):
        room_data = self.db_manager.get_room_by_number(room_number)

        if self.detail_window is not None:
            self.detail_window.destroy()

        self.detail_window = customtkinter.CTkToplevel(self.app_controller)
        self.detail_window.title(f"Room {room_number} - {room_data['status']}")
        self.detail_window.geometry("500x600")

        self.detail_window.grid_columnconfigure(0, weight=1)

        # --- MODAL BEHAVIOR IMPLEMENTATION ---
        self.detail_window.transient(self.app_controller)
        self.detail_window.grab_set()
        # -------------------------------------

        customtkinter.CTkLabel(self.detail_window,
                               text=f"Management: Room {room_number} ({room_data['type']})",
                               font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)

        if room_data['status'] == 'Available' or room_data['status'] == 'Booked':
            self._show_check_in_form(room_number, room_data['price'])
        elif room_data['status'] == 'Occupied':
            self._show_check_out_details(room_number, room_data)
        else:
            self._show_maintenance_options(room_number)

    # --- Helper Windows (Calendar/Charge) ---

    def _open_calendar_popup(self, target_entry, date_type_title):
        """Opens a Toplevel window with the tkcalendar widget."""
        self.date_entry_target = target_entry

        cal_window = customtkinter.CTkToplevel(self.app_controller)
        cal_window.title(f"Select {date_type_title} Date")
        cal_window.geometry("300x300")

        # --- MODAL BEHAVIOR IMPLEMENTATION ---
        cal_window.transient(self.app_controller)
        cal_window.grab_set()
        # -------------------------------------

        tk_frame = Frame(cal_window)
        tk_frame.pack(expand=True, fill='both')

        # Restrict calendar mindate
        min_date_val = None
        # We generally only want check-out to be today or later
        if date_type_title == "Check-out":
            min_date_val = date.today()
        # Allow check-in to be in the future (for booking) but not in the past.
        if date_type_title == "Check-in":
            min_date_val = date.today()

        self.cal = Calendar(tk_frame, selectmode='day',
                            date_pattern='yyyy-mm-dd', mindate=min_date_val)
        self.cal.pack(pady=10, padx=10, expand=True, fill='both')

        customtkinter.CTkButton(cal_window, text="Confirm Date",
                                command=lambda: self._set_selected_date(cal_window)).pack(pady=10)

    def _set_selected_date(self, cal_window):
        """Retrieves the selected date and updates the stored entry field."""
        if self.date_entry_target:
            selected_date_str = self.cal.get_date()
            self.date_entry_target.delete(0, 'end')
            self.date_entry_target.insert(0, selected_date_str)
        cal_window.destroy()

    def _open_charge_popup(self, room_number, reservation_id):
        """Opens a Toplevel window to add an extra charge."""

        charge_window = customtkinter.CTkToplevel(self.app_controller)
        charge_window.title(f"Add Charge to Room {room_number}")
        charge_window.geometry("350x250")

        # --- MODAL BEHAVIOR IMPLEMENTATION ---
        charge_window.transient(self.app_controller)
        charge_window.grab_set()
        # -------------------------------------

        charge_window.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(charge_window, text="Add Extra Charge", font=customtkinter.CTkFont(
            weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        customtkinter.CTkLabel(charge_window, text="Description:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w")
        entry_desc = customtkinter.CTkEntry(
            charge_window, placeholder_text="Minibar, Laundry, etc.")
        entry_desc.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(charge_window, text="Amount ($):").grid(
            row=2, column=0, padx=10, pady=5, sticky="w")
        entry_amount = customtkinter.CTkEntry(charge_window)
        entry_amount.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        charge_error_label = customtkinter.CTkLabel(charge_window, text="")
        charge_error_label.grid(row=4, column=0, columnspan=2, pady=5)

        def submit_charge():
            try:
                amount = float(entry_amount.get())
                if amount <= 0:
                    raise ValueError("Amount must be positive.")

                desc = entry_desc.get()
                if not desc:
                    raise ValueError("Description is required.")

                success, message = self.db_manager.add_extra_charge(
                    room_number, reservation_id, desc, amount)

                if success:
                    charge_window.destroy()
                    self.open_room_detail(room_number)
                else:
                    charge_error_label.configure(
                        text=f"DB Error: {message}", text_color="red")
            except ValueError as e:
                charge_error_label.configure(
                    text=f"Input Error: {e}", text_color="red")

        customtkinter.CTkButton(charge_window, text="Submit Charge",
                                command=submit_charge).grid(row=3, column=0, columnspan=2, pady=20)

    # --- View Dispatches ---

    def _show_maintenance_options(self, room_number):
        frame = customtkinter.CTkFrame(self.detail_window)
        frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        customtkinter.CTkLabel(frame, text="Room requires attention.",
                               font=customtkinter.CTkFont(weight="bold")).pack(pady=10)

        customtkinter.CTkButton(frame, text="Mark as Available",
                                command=lambda: self.handle_status_change(room_number, 'Available', self.detail_window)).pack(pady=5, padx=20)

        customtkinter.CTkButton(frame, text="Mark as Out of Service",
                                command=lambda: self.handle_status_change(room_number, 'Out of Service', self.detail_window)).pack(pady=5, padx=20)

    def _show_check_in_form(self, room_number, price):
        form_frame = customtkinter.CTkFrame(self.detail_window)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Row 0: Guest Name
        customtkinter.CTkLabel(form_frame, text="Guest Name:").grid(
            row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_first = customtkinter.CTkEntry(
            form_frame, placeholder_text="First Name")
        self.entry_first.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.entry_last = customtkinter.CTkEntry(
            form_frame, placeholder_text="Last Name")
        self.entry_last.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Row 1: Email
        customtkinter.CTkLabel(form_frame, text="Email:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_email = customtkinter.CTkEntry(form_frame)
        self.entry_email.grid(row=1, column=1, columnspan=2,
                              padx=10, pady=5, sticky="ew")

        # Row 2: Phone
        customtkinter.CTkLabel(form_frame, text="Phone:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_phone = customtkinter.CTkEntry(form_frame)
        self.entry_phone.grid(row=2, column=1, columnspan=2,
                              padx=10, pady=5, sticky="ew")

        # Row 3: Address
        customtkinter.CTkLabel(form_frame, text="Address:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_address = customtkinter.CTkEntry(
            form_frame, placeholder_text="Guest Address")
        self.entry_address.grid(
            row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        # Row 4: Check-in Date
        customtkinter.CTkLabel(
            form_frame, text="Check-in Date:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.entry_checkin_display = customtkinter.CTkEntry(
            form_frame, placeholder_text="YYYY-MM-DD (Today)")
        self.entry_checkin_display.grid(
            row=4, column=1, padx=5, pady=5, sticky="ew")
        self.entry_checkin_display.insert(0, date.today().strftime('%Y-%m-%d'))

        customtkinter.CTkButton(form_frame, text="Select",
                                command=lambda: self._open_calendar_popup(self.entry_checkin_display, "Check-in")).grid(row=4, column=2, padx=10, pady=5, sticky="w")

        # Row 5: Check-out Date
        customtkinter.CTkLabel(
            form_frame, text="Check-out Date:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.entry_checkout_display = customtkinter.CTkEntry(
            form_frame, placeholder_text="YYYY-MM-DD")
        self.entry_checkout_display.grid(
            row=5, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(form_frame, text="Select",
                                command=lambda: self._open_calendar_popup(self.entry_checkout_display, "Check-out")).grid(row=5, column=2, padx=10, pady=5, sticky="w")

        # Row 6: Price confirmation
        customtkinter.CTkLabel(form_frame, text=f"Price: ${price:.2f} / Night", font=customtkinter.CTkFont(
            weight="bold")).grid(row=6, column=0, columnspan=3, pady=10)

        # Row 7: Submit Button
        customtkinter.CTkButton(form_frame, text="SUBMIT BOOKING",
                                command=lambda: self.handle_check_in(room_number, price)).grid(row=7, column=0, columnspan=3, pady=20)

        self.error_label = customtkinter.CTkLabel(form_frame, text="")
        self.error_label.grid(row=8, column=0, columnspan=3)

    def _show_check_out_details(self, room_number, room_data):
        res = room_data['reservation']
        guest = room_data['guest']
        price_per_night = room_data['price']

        charges = self.db_manager.session.query(Charge).filter_by(
            reservation_id_fk=res.booking_id).all()

        days_stayed = (date.today() - res.check_in_date).days + 1
        room_charge = days_stayed * price_per_night
        extra_charges_total = sum(c.amount for c in charges)
        estimated_total = room_charge + extra_charges_total

        main_frame = customtkinter.CTkFrame(self.detail_window)
        main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # 1. Guest & Stay Summary
        customtkinter.CTkLabel(main_frame, text="Guest & Stay Summary", font=customtkinter.CTkFont(
            size=16, weight="bold")).pack(pady=(10, 5))
        customtkinter.CTkLabel(
            main_frame, text=f"Guest: {guest.first_name} {guest.last_name} ({guest.contact_phone})").pack(anchor="w", padx=20)
        customtkinter.CTkLabel(main_frame, text=f"Stay: {res.check_in_date} to {res.check_out_date} ({days_stayed} nights)").pack(
            anchor="w", padx=20, pady=(0, 10))

        # 2. Charges Section
        charge_frame = customtkinter.CTkScrollableFrame(
            main_frame, label_text="Charges Log")
        charge_frame.pack(fill="x", padx=10, pady=5, ipady=5)

        customtkinter.CTkLabel(charge_frame, text="Description", font=customtkinter.CTkFont(
            weight="bold")).grid(row=0, column=0, padx=10)
        customtkinter.CTkLabel(charge_frame, text="Amount", font=customtkinter.CTkFont(
            weight="bold")).grid(row=0, column=1, padx=10)

        customtkinter.CTkLabel(charge_frame, text="Room Rate").grid(
            row=1, column=0, padx=10, sticky="w")
        customtkinter.CTkLabel(charge_frame, text=f"${room_charge:.2f}").grid(
            row=1, column=1, padx=10, sticky="e")

        row_idx = 2
        for charge in charges:
            customtkinter.CTkLabel(charge_frame, text=charge.description).grid(
                row=row_idx, column=0, padx=10, sticky="w")
            customtkinter.CTkLabel(charge_frame, text=f"${charge.amount:.2f}").grid(
                row=row_idx, column=1, padx=10, sticky="e")
            row_idx += 1

        charge_frame.grid_columnconfigure(0, weight=1)

        # 3. Add Charge Button
        customtkinter.CTkButton(main_frame, text="Add Extra Charge (+)",
                                command=lambda: self._open_charge_popup(room_number, res.booking_id)).pack(pady=10)

        # 4. Final Billing
        customtkinter.CTkLabel(main_frame, text=f"TOTAL ESTIMATED BILL: ${estimated_total:.2f}", font=customtkinter.CTkFont(
            size=18, weight="bold"), text_color="green").pack(pady=(15, 10))

        customtkinter.CTkButton(main_frame, text="PROCESS CHECK-OUT & PAY", fg_color="red", hover_color="#800000",
                                command=lambda: self.handle_check_out(room_number, res.booking_id, price_per_night)).pack(pady=10, padx=20)

        self.checkout_error_label = customtkinter.CTkLabel(main_frame, text="")
        self.checkout_error_label.pack()

    # --- Controller Logic ---

    def handle_check_in(self, room_number, price):
        guest_data = {
            'first_name': self.entry_first.get(),
            'last_name': self.entry_last.get(),
            'email': self.entry_email.get(),
            'phone': self.entry_phone.get(),
            'address': self.entry_address.get()
        }

        reservation_data = {
            'room_number': room_number,
            'check_in_date_str': self.entry_checkin_display.get(),
            'checkout_date_str': self.entry_checkout_display.get(),
            'price': price
        }

        success, message = self.db_manager.check_in_guest(
            guest_data, reservation_data)

        if success:
            self.detail_window.destroy()
            self.load_room_cards()
        else:
            self.error_label.configure(text=f"Error: {message}")

    def handle_check_out(self, room_number, booking_id, price_per_night):
        success, message = self.db_manager.check_out_guest(
            room_number, booking_id, price_per_night)

        if success:
            self.detail_window.destroy()
            self.load_room_cards()
            messagebox.showinfo("Check-Out Success", message)
        else:
            self.checkout_error_label.configure(
                text=f"Error: {message}", text_color="red")

    def handle_status_change(self, room_number, new_status, window_to_close):
        success = self.db_manager.update_room_status(room_number, new_status)
        if success:
            window_to_close.destroy()
            self.load_room_cards()
            # Important: Refresh the main dashboard via the controller
            self.app_controller.show_room_status_view()
