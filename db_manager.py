# db_manager.py

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import date, datetime
from sqlalchemy import func, or_
import hashlib  # NEW IMPORT


Base = declarative_base()


# --- NEW: User Model ---
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Store hashed password
    # Admin, Clerk, Housekeeping (for future use)
    role = Column(String, default='Clerk')


class Room(Base):
    __tablename__ = 'rooms'
    room_number = Column(Integer, primary_key=True)
    room_type = Column(String)
    description = Column(String)
    capacity = Column(Integer)
    price_per_night = Column(Float)
    status = Column(String, default='Available')

    reservations = relationship("Reservation", back_populates="room")
    charges = relationship("Charge", back_populates="room")


class Guest(Base):
    __tablename__ = 'guests'
    guest_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_email = Column(String, unique=True)
    contact_phone = Column(String)
    address = Column(String)
    is_blacklisted = Column(Boolean, default=False)

    reservations = relationship("Reservation", back_populates="guest")


class Reservation(Base):
    __tablename__ = 'reservations'
    booking_id = Column(Integer, primary_key=True)
    room_number_fk = Column(Integer, ForeignKey('rooms.room_number'))
    guest_id_fk = Column(Integer, ForeignKey('guests.guest_id'))
    check_in_date = Column(Date, default=date.today())
    check_out_date = Column(Date)
    total_bill = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)

    charges = relationship("Charge", back_populates="reservation")

    room = relationship("Room", back_populates="reservations")
    guest = relationship("Guest", back_populates="reservations")


class Charge(Base):
    __tablename__ = 'charges'
    charge_id = Column(Integer, primary_key=True)
    reservation_id_fk = Column(Integer, ForeignKey('reservations.booking_id'))
    room_number_fk = Column(Integer, ForeignKey('rooms.room_number'))
    description = Column(String)
    amount = Column(Float)
    charge_date = Column(Date, default=date.today())

    reservation = relationship("Reservation", back_populates="charges")
    room = relationship("Room", back_populates="charges")


class DBManager:
    # Adding User model to the DBManager so we can reference it easily
    User = User

    def __init__(self, db_url='sqlite:///hotel_management.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # --- NEW: User Authentication Methods ---

    def hash_password(self, password):
        """Hashes the password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_initial_user(self, username, password, role='Admin'):
        """Adds a new user, checking for duplicates first."""
        try:
            if self.session.query(User).filter_by(username=username).first():
                return False, "Username already exists."

            hashed_password = self.hash_password(password)
            new_user = User(
                username=username,
                password_hash=hashed_password,
                role=role
            )
            self.session.add(new_user)
            self.session.commit()
            return True, "User created successfully."
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating user: {e}"

    def check_credentials(self, username, password):
        """Authenticates a user by checking the hashed password."""
        user = self.session.query(User).filter_by(username=username).first()

        if user:
            # Hash the input password and compare it to the stored hash
            if user.password_hash == self.hash_password(password):
                return True, user.role

        return False, None

    # --- Room Status & Basic Room Methods --- (All previous methods remain the same)

    def get_room_status(self):
        rooms = self.session.query(Room).all()
        return [{'number': r.room_number, 'type': r.room_type, 'status': r.status} for r in rooms]

    def get_room_by_number(self, room_number):
        room = self.session.query(Room).filter_by(
            room_number=room_number).first()
        if room:
            # Check for active reservations based on today's date
            active_reservation = self.session.query(Reservation).filter(
                Reservation.room_number_fk == room_number,
                Reservation.check_out_date >= date.today(),
                Reservation.check_in_date <= date.today()
            ).first()

            if active_reservation:
                guest = self.session.query(Guest).filter_by(
                    guest_id=active_reservation.guest_id_fk).first()
            else:
                guest = None

            return {
                'number': room.room_number,
                'type': room.room_type,
                'status': room.status,
                'price': room.price_per_night,
                'capacity': room.capacity,
                'description': room.description,
                'reservation': active_reservation,
                'guest': guest
            }
        return None

    def get_all_rooms(self):
        rooms = self.session.query(Room).all()
        return [{
            'number': r.room_number,
            'type': r.room_type,
            'price': r.price_per_night,
            'capacity': r.capacity,
            'description': r.description,
            'status': r.status
        } for r in rooms]

    def update_room_status(self, room_number, new_status):
        room = self.session.query(Room).filter_by(
            room_number=room_number).first()
        if room:
            room.status = new_status
            self.session.commit()
            return True
        return False

    def get_rooms_needing_cleaning(self):
        """Returns a list of rooms currently in 'Needs Cleaning' status."""
        rooms = self.session.query(Room).filter_by(
            status='Needs Cleaning').all()
        return [{
            'number': r.room_number,
            'type': r.room_type,
            'price': r.price_per_night,
            'description': r.description,
            'status': r.status
        } for r in rooms]

    def update_room_details(self, room_number, data):
        try:
            room = self.session.query(Room).filter_by(
                room_number=room_number).first()
            if room:
                if 'room_type' in data:
                    room.room_type = data['room_type']
                if 'price_per_night' in data:
                    room.price_per_night = data['price_per_night']
                if 'capacity' in data:
                    room.capacity = data['capacity']
                if 'description' in data:
                    room.description = data['description']

                self.session.commit()
                return True, f"Room {room_number} details updated."
            return False, "Room not found."
        except Exception as e:
            self.session.rollback()
            return False, f"Database Error: {e}"

    # --- Guest Management Methods ---

    def search_guests(self, query):
        search_term = f"%{query}%"

        guests = self.session.query(Guest).filter(
            or_(
                func.lower(Guest.first_name).like(func.lower(search_term)),
                func.lower(Guest.last_name).like(func.lower(search_term)),
                func.lower(Guest.contact_email).like(func.lower(search_term)),
                Guest.contact_phone.like(search_term)
            )
        ).all()

        results = [{
            'id': g.guest_id,
            'name': f"{g.first_name} {g.last_name}",
            'email': g.contact_email,
            'phone': g.contact_phone,
            'address': g.address,
            'blacklisted': g.is_blacklisted
        } for g in guests]

        return results

    def get_guest_by_id(self, guest_id):
        return self.session.query(Guest).filter_by(guest_id=guest_id).first()

    def update_guest_profile(self, guest_id, data):
        try:
            guest = self.session.query(Guest).filter_by(
                guest_id=guest_id).first()
            if guest:
                for key, value in data.items():
                    if hasattr(guest, key):
                        setattr(guest, key, value)
                self.session.commit()
                return True, "Profile updated."
            return False, "Guest not found."
        except Exception as e:
            self.session.rollback()
            return False, f"Database Error: {e}"

    # --- Transaction & Billing Methods ---

    def check_in_guest(self, guest_data, reservation_data):
        try:
            # Convert date strings to date objects
            check_in_date = datetime.strptime(
                reservation_data['check_in_date_str'], '%Y-%m-%d').date()
            checkout_date = datetime.strptime(
                reservation_data['checkout_date_str'], '%Y-%m-%d').date()

            # Validation
            if check_in_date < date.today():
                return False, "Check-in date cannot be in the past."
            if checkout_date <= check_in_date:
                return False, "Check-out date must be after the check-in date."

            # Find or Create Guest
            guest = self.session.query(Guest).filter_by(
                contact_email=guest_data['email']).first()
            if not guest:
                guest = Guest(
                    first_name=guest_data['first_name'],
                    last_name=guest_data['last_name'],
                    contact_email=guest_data['email'],
                    contact_phone=guest_data['phone'],
                    address=guest_data['address']
                )
                self.session.add(guest)
                self.session.flush()

            # Create Reservation
            res = Reservation(
                room_number_fk=reservation_data['room_number'],
                guest_id_fk=guest.guest_id,
                check_in_date=check_in_date,
                check_out_date=checkout_date,
                total_bill=0.0
            )
            self.session.add(res)

            # Update Room Status only if check-in is today
            if check_in_date == date.today():
                self.update_room_status(
                    reservation_data['room_number'], 'Occupied')
            else:
                self.update_room_status(
                    reservation_data['room_number'], 'Booked')

            self.session.commit()
            return True, "Check-in/Booking successful."

        except ValueError:
            self.session.rollback()
            return False, "Invalid date format. Use YYYY-MM-DD."
        except Exception as e:
            self.session.rollback()
            return False, f"Database Error: {e}"

    def check_out_guest(self, room_number, reservation_id, price_per_night):
        try:
            res = self.session.query(Reservation).filter_by(
                booking_id=reservation_id).first()
            if not res:
                return False, "Reservation not found."

            # Calculate days stayed based on check-in date vs today
            days_stayed = (date.today() - res.check_in_date).days + 1
            room_charge = days_stayed * price_per_night

            extra_charges = self.session.query(func.sum(Charge.amount)).filter_by(
                reservation_id_fk=reservation_id).scalar()
            extra_charges = extra_charges if extra_charges is not None else 0.0

            total_bill = room_charge + extra_charges

            res.total_bill = total_bill
            res.is_paid = True

            self.update_room_status(room_number, 'Needs Cleaning')

            self.session.commit()
            return True, f"Check-out successful. Final Bill: ${total_bill:.2f} ({days_stayed} nights + ${extra_charges:.2f} extras)"

        except Exception as e:
            self.session.rollback()
            return False, f"Check-out Error: {e}"

    def add_extra_charge(self, room_number, reservation_id, description, amount):
        try:
            charge = Charge(
                reservation_id_fk=reservation_id,
                room_number_fk=room_number,
                description=description,
                amount=amount,
                charge_date=date.today()
            )
            self.session.add(charge)
            self.session.commit()
            return True, "Charge added successfully."
        except Exception as e:
            self.session.rollback()
            return False, f"Error adding charge: {e}"

    # --- Reservation History & Reporting Methods ---

    def get_reservation_history(self, search_query="", status_filter="All", start_date=None, end_date=None):
        """
        Retrieves detailed reservation history based on various filters.
        """
        try:
            query = self.session.query(
                Reservation.booking_id,
                Reservation.check_in_date,
                Reservation.check_out_date,
                Reservation.total_bill,
                Reservation.is_paid,
                Guest.first_name,
                Guest.last_name,
                Room.room_number,
                Room.price_per_night,
                Room.room_type
            ).join(Guest).join(Room)

            # 1. Status Filter
            if status_filter == 'Paid':
                query = query.filter(Reservation.is_paid == True)
            elif status_filter == 'Unpaid':
                query = query.filter(Reservation.is_paid == False)

            # 2. Search Query (Guest Name or Room Number)
            if search_query:
                search_term = f"%{search_query}%"
                query = query.filter(or_(
                    func.lower(Guest.first_name).like(func.lower(search_term)),
                    func.lower(Guest.last_name).like(func.lower(search_term)),
                    Room.room_number.like(search_term)
                ))

            # 3. Date Range Filter
            if start_date:
                query = query.filter(Reservation.check_out_date >= start_date)
            if end_date:
                query = query.filter(Reservation.check_in_date <= end_date)

            # Order by check-in date (newest first)
            query = query.order_by(Reservation.check_in_date.desc())

            results = []
            for (booking_id, ci_date, co_date, total_bill, is_paid, f_name, l_name, r_num, price, r_type) in query.all():
                results.append({
                    'booking_id': booking_id,
                    'room_number': r_num,
                    'room_type': r_type,
                    'guest_name': f"{f_name} {l_name}",
                    'check_in': ci_date.strftime('%Y-%m-%d'),
                    'check_out': co_date.strftime('%Y-%m-%d'),
                    'bill': total_bill,
                    'is_paid': is_paid
                })

            return True, results

        except Exception as e:
            return False, f"Database query failed: {e}"

    def get_revenue_report(self, start_date, end_date):
        """
        Calculates key revenue and occupancy metrics for a given date range.
        """
        try:
            # Calculate total days in the period
            delta = (end_date - start_date).days + 1
            if delta <= 0:
                return False, "End date must be after or equal to the start date."

            # 1. Total Revenue (Sum of total_bill for paid reservations within the period)
            total_revenue_query = self.session.query(
                func.sum(Reservation.total_bill)
            ).filter(
                Reservation.is_paid == True,
                Reservation.check_in_date <= end_date,
                Reservation.check_out_date >= start_date
            ).scalar()

            total_revenue = total_revenue_query if total_revenue_query is not None else 0.0

            # 2. Total Available Room Nights
            total_rooms = self.session.query(
                func.count(Room.room_number)).scalar()
            total_available_nights = total_rooms * delta

            # 3. Total Occupied Room Nights (Calculating Actual Stay within the reporting period)
            occupied_nights = 0

            # Get all relevant reservations (those overlapping the date range)
            reservations = self.session.query(Reservation).filter(
                Reservation.check_in_date <= end_date,
                Reservation.check_out_date >= start_date
            ).all()

            for res in reservations:
                stay_start = max(res.check_in_date, start_date)
                stay_end = min(res.check_out_date, end_date)

                nights = (stay_end - stay_start).days

                if nights > 0:
                    occupied_nights += nights

            # 4. Calculate KPIs
            occupancy_rate = (occupied_nights / total_available_nights) * \
                100 if total_available_nights > 0 else 0.0

            # Average Daily Rate (ADR)
            adr = total_revenue / occupied_nights if occupied_nights > 0 else 0.0

            # Revenue Per Available Room (RevPAR)
            revpar = total_revenue / total_available_nights if total_available_nights > 0 else 0.0

            return True, {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'period_days': delta,
                'total_rooms': total_rooms,
                'total_revenue': total_revenue,
                'occupied_nights': occupied_nights,
                'available_nights': total_available_nights,
                'occupancy_rate': occupancy_rate,
                'adr': adr,
                'revpar': revpar
            }

        except Exception as e:
            return False, f"Reporting error: {e}"
