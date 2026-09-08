from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
import sys, sqlite3, random, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime


def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "students.db")

db = sqlite3.connect(get_db_path())
cursor = db.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    massar TEXT UNIQUE,
    school_year TEXT,
    interruption_date TEXT,
    reason TEXT
)
""")
db.commit()

app = QApplication(sys.argv)
app.setLayoutDirection(Qt.RightToLeft)
app.setWindowIcon(QIcon("icon.ico"))

window = QMainWindow()
window.setGeometry(100, 100, 800, 500)
window.setWindowTitle("تدبير أرشيف المؤسسة")

def makeLine():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setStyleSheet("""
        background-color: gray;
        height: 3px;
    """)
    return line

def makeLabel(labelName, family, size, weight):
    label = QLabel(labelName)
    font = QFont(family, size, weight)
    label.setFont(font)
    return label

def makeTextField(placeHolder):
    textField = QLineEdit()
    textField.setPlaceholderText(placeHolder)
    textField.setMaximumWidth(250)
    textField.setStyleSheet("""
    font-size: 20px;
    font-family: Arial;
    """)
    return textField


central = QWidget()
window.setCentralWidget(central)

#LAYOUT PRINCIPAL
mainLayout = QVBoxLayout()

#PREMIER LAYOUT
layout1 = QVBoxLayout()

title = QLabel("تدبير أرشيف المؤسسة")
title.setStyleSheet("""
    font-size: 40px;
    font-family: Arial;
    font-weight: bold;    
""")
title.setAlignment(Qt.AlignHCenter)
layout1.addWidget(title)

#2nd Layout
layout2 = QHBoxLayout()

searchArabic = QLabel("بحث :")
searchArabic.setStyleSheet("""
    font-size: 25px;
    font-family: Arial;
    font-weight: bold;
""")

searchCombo = QComboBox()
searchCombo.addItem("الإسم")
searchCombo.addItem("النسب")
searchCombo.addItem("رقم مسار")
searchCombo.addItem("السنة الدراسية")


searchCombo.setMaximumWidth(200)
searchCombo.setStyleSheet("""
    font-size: 16px;
""")

searchInput = QLineEdit()
searchInput.setPlaceholderText("اكتب هنا...")
searchInput.setMaximumWidth(200)
searchInput.setStyleSheet("""
    font-size: 16px;
    font-family: Arial;
""")

searchButton = QPushButton("بحث")
searchButton.setMinimumWidth(150)
searchButton.setStyleSheet("""
    font-size: 20px;
    background-color: #007acc;
    border: 2px solid #005f99;
    border-radius: 15px;
""")
layout2.addWidget(searchArabic)
layout2.addWidget(searchCombo)
layout2.addWidget(searchInput)
layout2.addWidget(searchButton)
layout2.setSpacing(20)
layout2.addStretch()

#3RD LAYOUT
layout3 = QGridLayout()

layout3.addWidget(makeLabel("الإسم", "Arial", 17, QFont.Bold), 0, 0, alignment=Qt.AlignHCenter)
layout3.addWidget(makeLabel("النسب", "Arial", 17, QFont.Bold), 0, 1, alignment=Qt.AlignHCenter)
layout3.addWidget(makeLabel("رقم مسار", "Arial", 17, QFont.Bold), 0, 2, alignment=Qt.AlignHCenter)
layout3.addWidget(makeLabel("السنة الدراسية", "Arial", 17, QFont.Bold), 0, 3, alignment=Qt.AlignHCenter)
layout3.addWidget(makeLabel("تاريخ الإنقطاع", "Arial", 17, QFont.Bold), 0, 4, alignment=Qt.AlignHCenter)
layout3.addWidget(makeLabel("سبب الإنقطاع", "Arial", 17, QFont.Bold), 0, 5, alignment=Qt.AlignHCenter)

firstNameInput = makeTextField("")
lastNameInput = makeTextField("")
massarNumInput = makeTextField("")
schoolYearInput = makeTextField("")
interruptionDateInput = makeTextField("")
layout3.addWidget(firstNameInput, 1, 0, alignment=Qt.AlignHCenter)
layout3.addWidget(lastNameInput, 1, 1, alignment=Qt.AlignHCenter)
layout3.addWidget(massarNumInput, 1, 2, alignment=Qt.AlignHCenter)
layout3.addWidget(schoolYearInput, 1, 3, alignment=Qt.AlignHCenter)
layout3.addWidget(interruptionDateInput, 1, 4, alignment=Qt.AlignHCenter)
reasonCombo = QComboBox()
reasonCombo.addItems(["لم يلتحق", "انقطاع", "فصل", "انتقل و لم يطلب ملفه"])
reasonCombo.setStyleSheet("""
    font-size: 16px;
""")
layout3.addWidget(reasonCombo, 1, 5, alignment=Qt.AlignHCenter)

addStudent = QPushButton("إضافة")
addStudent.setMinimumHeight(40)
addStudent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
addStudent.setStyleSheet("""
    font-size: 20px;
    background-color: #28a745;
    border: 2px solid #1e7e34;
    border-radius: 15px;
""")
layout3.addWidget(addStudent, 2, 2, 1, 2)

#THE TABLE
studentsTable = QTableWidget()
studentsTable.setColumnCount(6)
studentsTable.setHorizontalHeaderLabels([
    "الإسم",
    "النسب",
    "رقم مسار",
    "السنة الدراسية",
    "تاريخ الإنقطاع",
    "سبب الإنقطاع"
])
studentsTable.setStyleSheet("""
    font-family: Arial;
    font-size: 18px;
    font-weight: bold;
""")
studentsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
studentsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
studentsTable.setSelectionMode(QAbstractItemView.SingleSelection)
studentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
studentsTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

#Buttons Layout
buttonsLayout = QHBoxLayout()

deleteStudent = QPushButton("حذف")
deleteStudent.setMinimumHeight(40)
deleteStudent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
deleteStudent.setStyleSheet("""
    font-size: 20px;
    background-color: #d41111;
    border: 2px solid #a00b0b;
    border-radius: 15px;
""")


editStudent = QPushButton("تعديل")
editStudent.setMinimumHeight(40)
editStudent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
editStudent.setStyleSheet("""
    font-size: 20px;
    background-color: #ffc107;
    border: 2px solid #e0a800;
    border-radius: 15px;
""")

pdfButton = QPushButton("تصدير PDF")
pdfButton.setMinimumHeight(40)
pdfButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
pdfButton.setStyleSheet("""
    font-size: 20px;
    background-color: #007acc;
    border: 2px solid #005f99;
    border-radius: 15px;
""")

buttonsLayout.addWidget(editStudent)
buttonsLayout.addWidget(deleteStudent)
buttonsLayout.addWidget(pdfButton)
buttonsLayout.setSpacing(20)

mainLayout.addLayout(layout1)
mainLayout.addWidget(makeLine())
mainLayout.addLayout(layout2)
mainLayout.addWidget(makeLine())
mainLayout.addLayout(layout3)
mainLayout.addWidget(makeLine())
mainLayout.addWidget(studentsTable, stretch=1)
mainLayout.addLayout(buttonsLayout)
mainLayout.addStretch()
mainLayout.setSpacing(20)
central.setLayout(mainLayout)

#FUNCTIONS CONNECTED TO BUTTONS

def add_Student():
    fst = firstNameInput.text().strip()
    scnd = lastNameInput.text().strip()
    third = massarNumInput.text().strip()
    fourth = schoolYearInput.text().strip()
    fifth = interruptionDateInput.text().strip()
    sixth = reasonCombo.currentText()

    incorrectMessage = QMessageBox()
    incorrectMessage.setWindowTitle("خطأ")
    incorrectMessage.setText("يرجى ملء جميع الحقول")
    incorrectMessage.setStyleSheet("""
        QLabel {
            font-size: 18px;
            font-family: Arial;
        }
        QPushButton {
            font-size: 16px;
            font-family: Arial;                     
        }
    """)

    if not fst or not scnd or not third or not fourth or not fifth:
        incorrectMessage.exec()
        return
    
    try:
        cursor.execute("""
            INSERT INTO students 
            (first_name, last_name, massar, school_year, interruption_date, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fst, scnd, third, fourth, fifth, sixth))

        db.commit()
        load_from_db()

        firstNameInput.clear()
        lastNameInput.clear()
        massarNumInput.clear()
        schoolYearInput.clear()
        interruptionDateInput.clear()

    except sqlite3.IntegrityError:
        QMessageBox.warning(window, "خطأ", "رقم مسار موجود بالفعل")

addStudent.clicked.connect(add_Student)

def delete_Student():
    row = studentsTable.currentRow()

    incorrectMessage = QMessageBox()
    incorrectMessage.setWindowTitle("خطأ")
    incorrectMessage.setText("يرجى اختيار سطر للحذف")
    incorrectMessage.setStyleSheet("""
        QLabel {
            font-size: 18px;
            font-family: Arial;
        }
        QPushButton {
            font-size: 16px;
            font-family: Arial;                     
        }
    """)

    if row == -1:
        incorrectMessage.exec()
        return
    
    reply = QMessageBox.question(
    window,
    "تأكيد الحذف",
    "هل أنت متأكد أنك تريد حذف هذا السطر؟",
    QMessageBox.Yes | QMessageBox.No
    )

    if reply == QMessageBox.No:
        return
    
    massar = studentsTable.item(row, 2).text()

    cursor.execute("DELETE FROM students WHERE massar = ?", (massar,))
    db.commit()
    load_from_db()

deleteStudent.clicked.connect(delete_Student)


isEditing = False

def edit_Student():
    
    global isEditing

    row = studentsTable.currentRow()

    incorrectMessage = QMessageBox()
    incorrectMessage.setWindowTitle("خطأ")
    incorrectMessage.setText("يرجى اختيار سطر للتعديل")
    incorrectMessage.setStyleSheet("""
        QLabel {
            font-size: 18px;
            font-family: Arial;
        }
        QPushButton {
            font-size: 16px;
            font-family: Arial;                     
        }
    """)

    incorrectMessage2 = QMessageBox()
    incorrectMessage2.setWindowTitle("خطأ")
    incorrectMessage2.setText("يرجى ملء جميع الحقول")
    incorrectMessage2.setStyleSheet("""
        QLabel {
            font-size: 18px;
            font-family: Arial;
        }
        QPushButton {
            font-size: 16px;
            font-family: Arial;                     
        }
    """)

    if row == -1:
        incorrectMessage.exec()
        return


    if not isEditing:

        firstNameInput.setText(studentsTable.item(row, 0).text())
        lastNameInput.setText(studentsTable.item(row, 1).text())
        massarNumInput.setText(studentsTable.item(row, 2).text())
        schoolYearInput.setText(studentsTable.item(row, 3).text())
        interruptionDateInput.setText(studentsTable.item(row, 4).text())
        reasonCombo.setCurrentText(studentsTable.item(row, 5).text())

        isEditing = True

        addStudent.setEnabled(False)
        editStudent.setText("تحديث")

        return

    # UPDATE STUDENT
    fst = firstNameInput.text().strip()
    scnd = lastNameInput.text().strip()
    third = massarNumInput.text().strip()
    fourth = schoolYearInput.text().strip()
    fifth = interruptionDateInput.text().strip()
    sixth = reasonCombo.currentText()

    if not fst or not scnd or not third or not fourth or not fifth:
        incorrectMessage2.exec()
        return

    old_massar = studentsTable.item(row, 2).text()

    cursor.execute("""
        UPDATE students
        SET first_name = ?, 
            last_name = ?, 
            massar = ?, 
            school_year = ?, 
            interruption_date = ?, 
            reason = ?
        WHERE massar = ?
    """, (fst, scnd, third, fourth, fifth, sixth, old_massar))

    db.commit()
    load_from_db()

    firstNameInput.clear()
    lastNameInput.clear()
    massarNumInput.clear()
    schoolYearInput.clear()
    interruptionDateInput.clear()

    studentsTable.clearSelection()

    isEditing = False

    addStudent.setEnabled(True)
    editStudent.setText("تعديل")

editStudent.clicked.connect(edit_Student)

def search_Student():
    column_map = ["first_name", "last_name", "massar", "school_year"]
    column = column_map[searchCombo.currentIndex()]
    text = searchInput.text().strip()

    if not text:
        load_from_db()
        return

    cursor.execute(f"""
        SELECT first_name, last_name, massar, school_year, interruption_date, reason
        FROM students
        WHERE {column} LIKE ?
    """, (f"%{text}%",))

    studentsTable.setRowCount(0)

    for row_data in cursor.fetchall():
        row = studentsTable.rowCount()
        studentsTable.insertRow(row)

        for col, value in enumerate(row_data):
            studentsTable.setItem(row, col, QTableWidgetItem(str(value)))


searchButton.clicked.connect(search_Student)
searchInput.textChanged.connect(search_Student)
    
def load_from_db():
    studentsTable.setRowCount(0)

    cursor.execute("SELECT first_name, last_name, massar, school_year, interruption_date, reason FROM students")

    for row_data in cursor.fetchall():
        row = studentsTable.rowCount()
        studentsTable.insertRow(row)

        for col, value in enumerate(row_data):
            studentsTable.setItem(row, col, QTableWidgetItem(str(value)))


first_names = ["محمد","أحمد","يوسف","خالد","سعيد","حمزة","ياسين","عمر","أنس","مروان","إلياس","إبراهيم","طه","سفيان","أيوب","يونس","جواد","أمين","بدر"]
last_names = ["العلوي","بنسعيد","الإدريسي","المريني","الفاسي","التازي","الوردي","الصديقي","بوعزة","الشاوي","الكتاني","الحسني","بنجلون","الزياتي","لمغاري","القادري","البقالي","المودن","السالمي","اليوسفي"]
reasons = ["لم يلتحق", "انقطاع", "فصل", "انتقل و لم يطلب ملفه"]

def generate_fake_data(n=1000):
    for i in range(n):
        fst = random.choice(first_names)
        scnd = random.choice(last_names)
        massar = f"M{100000000+i}"

        year = random.randint(2018, 2024)
        school_year = f"{year}/{year+1}"

        day = random.randint(1, 28)
        month = random.randint(1, 12)
        date = f"{day:02d}/{month:02d}/2024"

        reason = random.choice(reasons)

        cursor.execute("""
            INSERT INTO students (first_name, last_name, massar, school_year, interruption_date, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fst, scnd, massar, school_year, date, reason))

    db.commit()

def fix_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(__file__), filename)

def export_pdf():
    from PySide6.QtWidgets import QFileDialog

    # Default file name with timestamp
    default_name = f"students_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    file_name, _ = QFileDialog.getSaveFileName(
        window,
        "اختر مكان حفظ الملف",
        default_name,
        "PDF Files (*.pdf)"
    )

    # If user cancels
    if not file_name:
        return

    # Ensure .pdf extension
    if not file_name.endswith(".pdf"):
        file_name += ".pdf"

    # Load Arabic font
    font_path = get_resource_path('Amiri-Regular.ttf')
    pdfmetrics.registerFont(TTFont('Arabic', font_path))

    doc = SimpleDocTemplate(file_name, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    arabic_style = styles['Heading1']
    arabic_style.fontName = 'Arabic'
    arabic_style.fontSize = 24
    arabic_style.alignment = 1
    arabic_style.spaceAfter = 30

    title = Paragraph(fix_arabic("تقرير أرشيف التلاميذ"), arabic_style)
    elements.append(title)

    data = [[
        fix_arabic("سبب الإنقطاع"),
        fix_arabic("تاريخ الإنقطاع"),
        fix_arabic("السنة الدراسية"),
        fix_arabic("رقم مسار"),
        fix_arabic("النسب"),
        fix_arabic("الإسم"),
    ]]

    # Table rows
    for row in range(studentsTable.rowCount()):
        row_data = []
        for col in range(studentsTable.columnCount()):
            item = studentsTable.item(row, col)
            text = item.text() if item else ""
            row_data.insert(0, fix_arabic(text))  # RTL flip

        data.append(row_data)

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)

    doc.build(elements)

    QMessageBox.information(window, "PDF", f"تم حفظ الملف:\n{file_name}")

pdfButton.clicked.connect(export_pdf)
 


load_from_db()

window.show()
app.exec()