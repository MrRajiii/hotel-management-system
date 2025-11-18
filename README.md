# 🏨 Hotel Management System (HMS)

## Project Overview

The Hotel Management System (HMS) is a desktop application built using Python and `customtkinter` (for a modern GUI) combined with SQLAlchemy for robust database management. It provides essential tools for hotel staff and administrators, covering guest check-in/out, room status tracking, inventory management, billing, reservation history, and key financial reporting (ADR, Occupancy, RevPAR).

## ✨ Features

The system is organized into the following key modules accessible via the Administration Panel:

### 🏠 Front Desk Operations (Main View)
* **Real-time Room Status:** See the current status of every room (Available, Occupied, Booked, Needs Cleaning).
* **Check-in/Booking:** Process new reservations, create new guest profiles, and instantly update room status.
* **Check-out & Billing:** Finalize guest stays, calculate the total bill (room charges + extra charges), mark the bill as paid, and set the room status to 'Needs Cleaning'.
* **Add Extra Charges:** Easily add incidentals (e.g., dining, laundry) to an active reservation.

### ⚙️ Administration Panel (Admin View)

1.  **Guest Management**
    * Search and filter guests by name, email, or phone.
    * Edit guest contact information and address.
    * Manage guest blacklist status.
2.  **Room Management**
    * View and edit room details, including type, price per night, and capacity.
    * Set rooms to 'Out of Service' for maintenance (excluding currently 'Occupied' rooms).
3.  **Housekeeping**
    * View a dedicated queue of all rooms currently marked as 'Needs Cleaning'.
    * One-click function to change room status from 'Needs Cleaning' back to 'Available'.
4.  **Reservations (History)**
    * View a filterable log of all past and future reservations.
    * Filter by **Guest Name**, **Room Number**, **Status** (Paid/Unpaid), and a **Date Range**.
5.  **Reporting (Revenue Analysis)**
    * Generate a Key Performance Indicator (KPI) report for a specific date range.
    * Calculates essential metrics:
        * **Total Revenue**
        * **Occupancy Rate (%)**
        * **Average Daily Rate (ADR)**
        * **Revenue Per Available Room (RevPAR)**

## 💻 Tech Stack

* **GUI:** `customtkinter` (Python Library)
* **Core Logic:** Python 3.x
* **Database:** `SQLite` (File-based storage)
* **ORM:** `SQLAlchemy` (Object-Relational Mapper)
* **Version Control:** Git

## 🛠️ Installation and Setup

### Prerequisites

* Python 3.8+ installed on your machine.
* A stable internet connection for installing dependencies.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/hotel-management-system.git](https://github.com/YourUsername/hotel-management-system.git)
    cd hotel-management-system
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate the environment:
    # On Windows: venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install customtkinter sqlalchemy
    ```

4.  **Run the application:**
    * *Note: Ensure you have a core application file (e.g., `main.py` or `app.py`) to launch the `AppController`.* Assuming your main file is `main.py`:
    ```bash
    python main.py
    ```
    The database file (`hotel_management.db`) will be automatically created upon the first run of the `DBManager`.

## 📂 File Structure (Implied)

* `main.py` (App startup, initializes DBManager and AppController)
* `db_manager.py` (Database model definitions and interaction logic)
* `app_controller.py` (Handles view switching and shared methods)
* `room_status_view.py` (The main front desk view)
* `admin_panel_view.py` (The administrative view with all tabs)
* `.gitignore`
* `README.md` (This file)

## 🤝 Contribution

Feel free to open issues or submit pull requests for bug fixes, new features, or improvements. Please use the standard Git workflow: create a feature branch, commit logically, and open a PR against `main`.

---
*Created by MrRajiii*
