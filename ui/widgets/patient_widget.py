from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMessageBox,
    QHeaderView,
)
from PySide6.QtCore import Qt

from app.database.local_db import local_db
from app.services.patient_service import PatientService


class PatientWidget(QWidget):
    def __init__(self, clinic_id: str = None):
        super().__init__()
        self.clinic_id = clinic_id
        self.init_ui()
        self.load_patients()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجوی بیمار (نام، کد ملی، تلفن)")
        self.search_input.textChanged.connect(self.search_patients)
        toolbar.addWidget(self.search_input)

        add_button = QPushButton("افزودن بیمار جدید")
        add_button.clicked.connect(self.add_patient)
        toolbar.addWidget(add_button)

        refresh_button = QPushButton("بروزرسانی")
        refresh_button.clicked.connect(self.load_patients)
        toolbar.addWidget(refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["کد ملی", "نام", "نام خانوادگی", "تلفن", "موبایل", "ویرایش", "حذف"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def load_patients(self):
        with local_db.get_session() as session:
            service = PatientService(session)
            patients = service.get_patients(self.clinic_id)

            self.table.setRowCount(len(patients))
            for row, patient in enumerate(patients):
                self.table.setItem(row, 0, QTableWidgetItem(patient.national_id))
                self.table.setItem(row, 1, QTableWidgetItem(patient.first_name))
                self.table.setItem(row, 2, QTableWidgetItem(patient.last_name))
                self.table.setItem(row, 3, QTableWidgetItem(patient.phone or ""))
                self.table.setItem(row, 4, QTableWidgetItem(patient.mobile or ""))

                edit_btn = QPushButton("ویرایش")
                edit_btn.clicked.connect(
                    lambda checked, p=patient: self.edit_patient(p)
                )
                self.table.setCellWidget(row, 5, edit_btn)

                delete_btn = QPushButton("حذف")
                delete_btn.clicked.connect(
                    lambda checked, p=patient: self.delete_patient(p)
                )
                self.table.setCellWidget(row, 6, delete_btn)

    def search_patients(self, query: str):
        if not query:
            self.load_patients()
            return

        with local_db.get_session() as session:
            service = PatientService(session)
            patients = service.search_patients(self.clinic_id, query)

            self.table.setRowCount(len(patients))
            for row, patient in enumerate(patients):
                self.table.setItem(row, 0, QTableWidgetItem(patient.national_id))
                self.table.setItem(row, 1, QTableWidgetItem(patient.first_name))
                self.table.setItem(row, 2, QTableWidgetItem(patient.last_name))
                self.table.setItem(row, 3, QTableWidgetItem(patient.phone or ""))
                self.table.setItem(row, 4, QTableWidgetItem(patient.mobile or ""))

                edit_btn = QPushButton("ویرایش")
                edit_btn.clicked.connect(
                    lambda checked, p=patient: self.edit_patient(p)
                )
                self.table.setCellWidget(row, 5, edit_btn)

                delete_btn = QPushButton("حذف")
                delete_btn.clicked.connect(
                    lambda checked, p=patient: self.delete_patient(p)
                )
                self.table.setCellWidget(row, 6, delete_btn)

    def add_patient(self):
        dialog = PatientDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with local_db.get_session() as session:
                    service = PatientService(session)
                    service.create_patient(self.clinic_id, **data)
                self.load_patients()
                QMessageBox.information(self, "موفقیت", "بیمار با موفقیت اضافه شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن بیمار:\n{str(e)}")

    def edit_patient(self, patient):
        dialog = PatientDialog(self, patient)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with local_db.get_session() as session:
                    service = PatientService(session)
                    service.update_patient(patient.id, **data)
                self.load_patients()
                QMessageBox.information(self, "موفقیت", "بیمار با موفقیت ویرایش شد")
            except Exception as e:
                QMessageBox.critical(
                    self, "خطا", f"خطا در ویرایش بیمار:\n{str(e)}"
                )

    def delete_patient(self, patient):
        reply = QMessageBox.question(
            self,
            "تایید حذف",
            f"آیا از حذف {patient.first_name} {patient.last_name} اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                with local_db.get_session() as session:
                    service = PatientService(session)
                    service.delete_patient(patient.id)
                self.load_patients()
                QMessageBox.information(self, "موفقیت", "بیمار با موفقیت حذف شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف بیمار:\n{str(e)}")


class PatientDialog(QDialog):
    def __init__(self, parent=None, patient=None):
        super().__init__(parent)
        self.patient = patient
        self.setWindowTitle("افزودن بیمار" if not patient else "ویرایش بیمار")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        self.national_id_input = QLineEdit()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.mobile_input = QLineEdit()

        if self.patient:
            self.national_id_input.setText(self.patient.national_id)
            self.first_name_input.setText(self.patient.first_name)
            self.last_name_input.setText(self.patient.last_name)
            self.phone_input.setText(self.patient.phone or "")
            self.mobile_input.setText(self.patient.mobile or "")

        layout.addRow("کد ملی:", self.national_id_input)
        layout.addRow("نام:", self.first_name_input)
        layout.addRow("نام خانوادگی:", self.last_name_input)
        layout.addRow("تلفن:", self.phone_input)
        layout.addRow("موبایل:", self.mobile_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "national_id": self.national_id_input.text(),
            "first_name": self.first_name_input.text(),
            "last_name": self.last_name_input.text(),
            "phone": self.phone_input.text(),
            "mobile": self.mobile_input.text(),
        }
