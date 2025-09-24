# Manual Attendance System (Lite)

## NOTE: First delete the '.db' file in the main directory to create a new admin account and be able to use the app

A simple **manual attendance check-in system** built with **HTML + JavaScript**.  
Users can enter their **Name** and **Student ID**, **Class** and then check in, and the system logs their attendance with a timestamp.  
Attendance logs can be **exported to CSV or PDF** for easy reporting.

---

## ✨ Features

- ✅ Manual check-in with Name + Student ID + Class
- ✅ Stores logs in memory (browser)  
- ✅ Export logs to **CSV** (Excel compatible)  
- ✅ Export logs to **PDF** (formatted report)  
- ✅ Lightweight — runs in any browser, no backend required  

---

## 📂 Project Structure

- manual-attendance-system/
  - templates/
    - index.html          # Main HTML file
    - attendance.html     # Attendance log display
    - settings.html       # Settings page
    - login.html          # Admin login page
    -register.html       # Admin registration page
  - uploads/              # Directory for uploaded files (if any)
  - app.py                # Main Flask application
  - requirements.txt      # Python dependencies
  - README.md             # Project documentation

## 🚀 How to Use

1. Clone or download this repository:

   ```bash
   git clone https://github.com/Ak23bh/vision-based-attendance-system.git
   cd vision-based-attendance-system/manual-attendance-system
   ```

2. Run the app.py in your terminal with "python app.py".

3. Enter your **Name** and **Student ID**, then click **Check In**.
4. If you're an admin and have an account, click the Admin login button(If you created an account) to view and export attendance logs. You can also create an account by clicking the create account button.
5. Use the **Export to CSV** or **Export to PDF** buttons to download the

## Technologies Used

- Frontend: HTML, CSS, JavaScript
- Libraries: jsPDF (for PDF export), FileSaver.js (for CSV export)
- No backend required (runs entirely in the browser)
- Optional: Flask (if you want to run a local server)
- Optional: SQLite (if you want to store logs persistently)

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/licenses/MIT) file for details.
