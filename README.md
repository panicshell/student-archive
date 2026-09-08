# Archive des Étudiants (Student Archive Manager)

A desktop application for managing student dropout/interruption records, built with **PySide6** and **SQLite**. The interface is fully in Arabic with right-to-left (RTL) layout support.

## Features

- **Add, edit, and delete** student records (name, Massar ID, school year, interruption date, and reason)
- **Live search** across name, last name, Massar number, or school year
- **PDF export** of the full records table, with proper Arabic text shaping and RTL rendering
- **Duplicate protection** — prevents adding a student with an already-registered Massar ID
- **Auto-generated local database** — the SQLite database is created automatically on first run, no manual setup needed

## Built With

- [PySide6](https://doc.qt.io/qtforpython/) — GUI framework (Qt for Python)
- [SQLite3](https://docs.python.org/3/library/sqlite3.html) — local data storage
- [ReportLab](https://www.reportlab.com/) — PDF generation
- [arabic-reshaper](https://github.com/mpcabd/python-arabic-reshaper) & [python-bidi](https://github.com/MeirKriheli/python-bidi) — Arabic text shaping and bidirectional rendering

## Getting Started

### Prerequisites

- Python 3.9+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/panicshell/student-archive.git
   cd student-archive
   ```

2. Install the required packages:
   ```bash
   pip install PySide6 reportlab arabic-reshaper python-bidi
   ```

3. Run the app:
   ```bash
   python archive.py
   ```

The database (`students.db`) will be created automatically in the same folder on first launch.

## Notes

- The `Amiri-Regular.ttf` font is required for correct Arabic rendering in exported PDFs and must stay in the project folder.
- The app window icon (`icon.ico`) is also expected in the project folder.

## Author

**Mehdi Zerhouni**
DUT in Web & Multimedia Development (DWM) — EST Meknès

## License

No license — all rights reserved.
