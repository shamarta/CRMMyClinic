from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QCalendarWidget,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMessageBox,
    QComboBox,
    QDateTimeEdit,
    QHeaderView,
    QLabel,
)
from PySide6.QtCore import Qt, QDate, QDateTime
from datetime import datetime, date

from app.database.local_db import local_db
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService


class AppointmentWidget(QWidget):
    def __init__(self, clinic_id: str = None):
        super().__init__()
        self.clinic_id = clinic_id
        self.selected_date = date.today()
        self.init_ui()
        self.load_appointments()

    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        left_panel = QVBoxLayout()
        layout.addLayout(left_panel, 1)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.date_selected)
        left_panel.addWidget(self.calendar)

        stats_label = QLabel("آمار روز:")
        left_panel.addWidget(stats_label)

        self.stats_text = QLabel()
        left_panel.addWidget(self.stats_text)

        right_panel = QVBoxLayout()
        layout.addLayout(right_panel, 2)

        toolbar = QHBoxLayout()
        right_panel.addLayout(toolbar)

        self.date_label = QLabel(f"نوبت‌های تاریخ: {self.selected_date}")
        toolbar.addWidget(self.date_label)

        toolbar.addStretch()

        add_button = QPushButton("نوبت جدید")
        add_button.clicked.connect(self.add_appointment)
        toolbar.addWidget(add_button)

        refresh_button = QPushButton("بروزرسانی")
        refresh_button.clicked.connect(self.load_appointments)
        toolbar.addWidget(refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ساعت", "بیمار", "وضعیت", "هزینه", "مشاهده", "تکمیل", "لغو"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_panel.addWidget(self.table)

    def date_selected(self, qdate: QDate):
        self.selected_date = qdate.toPython()
        self.date_label.setText(f"نوبت‌های تاریخ: {self.selected_date}")
        self.load_appointments()

    def load_appointments(self):
        with local_db.get_session() as session:
            service = AppointmentService(session)
            appointments = service.get_appointments_by_date(
                self.clinic_id, self.selected_date
            )

            self.table.setRowCount(len(appointments))
            for row, apt in enumerate(appointments):
                time_str = apt.appointment_date.strftime("%H:%M")
                patient_name = (
                    f"{apt.patient.first_name} {apt.patient.last_name}"
                    if apt.patient
                    else "نامشخص"
                )

                self.table.setItem(row, 0, QTableWidgetItem(time_str))
                self.table.setItem(row, 1, QTableWidgetItem(patient_name))
                self.table.setItem(row, 2, QTableWidgetItem(apt.status))
                self.table.setItem(
                    row, 3, QTableWidgetItem(str(apt.visit_fee or 0))
                )

                view_btn = QPushButton("مشاهده")
                view_btn.clicked.connect(lambda checked, a=apt: self.view_appointment(a))
                self.table.setCellWidget(row, 4, view_btn)

                complete_btn = QPushButton("تکمیل")
                complete_btn.clicked.connect(
                    lambda checked, a=apt: self.complete_appointment(a)
                )
                self.table.setCellWidget(row, 5, complete_btn)

                cancel_btn = QPushButton("لغو")
                cancel_btn.clicked.connect(
                    lambda checked, a=apt: self.cancel_appointment(a)
                )
                self.table.setCellWidget(row, 6, cancel_btn)

            total = len(appointments)
            completed = len([a for a in appointments if a.status == "completed"])
            cancelled = len([a for a in appointments if a.status == "cancelled"])

            self.stats_text.setText(
                f"مجموع: {total}\nتکمیل شده: {completed}\nلغو شده: {cancelled}"
            )

    def add_appointment(self):
        dialog = AppointmentDialog(self, self.clinic_id, self.selected_date)
        if dialog.exec():
            self.load_appointments()

    def view_appointment(self, appointment):
        QMessageBox.information(
            self,
            "جزئیات نوبت",
            f"بیمار: {appointment.patient.first_name} {appointment.patient.last_name}\n"
            f"تاریخ: {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"وضعیت: {appointment.status}\n"
            f"هزینه: {appointment.visit_fee or 0}\n"
            f"یادداشت: {appointment.notes or '-'}",
        )

    def complete_appointment(self, appointment):
        reply = QMessageBox.question(
            self, "تایید", "آیا از تکمیل این نوبت اطمینان دارید؟"
        )
        if reply == QMessageBox.Yes:
            with local_db.get_session() as session:
                service = AppointmentService(session)
                service.complete_appointment(appointment.id)
            self.load_appointments()

    def cancel_appointment(self, appointment):
        reply = QMessageBox.question(
            self, "تایید", "آیا از لغو این نوبت اطمینان دارید؟"
        )
        if reply == QMessageBox.Yes:
            with local_db.get_session() as session:
                service = AppointmentService(session)
                service.cancel_appointment(appointment.id)
            self.load_appointments()


class AppointmentDialog(QDialog):
    def __init__(self, parent=None, clinic_id=None, selected_date=None):
        super().__init__(parent)
        self.clinic_id = clinic_id
        self.selected_date = selected_date or date.today()
        self.setWindowTitle("نوبت جدید")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        self.patient_combo = QComboBox()
        self.load_patients()
        layout.addRow("بیمار:", self.patient_combo)

        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(
            QDateTime(
                QDate(
                    self.selected_date.year,
                    self.selected_date.month,
                    self.selected_date.day,
                ),
                self.datetime_input.time(),
            )
        )
        layout.addRow("تاریخ و ساعت:", self.datetime_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_appointment)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def load_patients(self):
        with local_db.get_session() as session:
            service = PatientService(session)
            patients = service.get_patients(self.clinic_id)

            for patient in patients:
                self.patient_combo.addItem(
                    f"{patient.first_name} {patient.last_name}", patient.id
                )

    def save_appointment(self):
        patient_id = self.patient_combo.currentData()
        appointment_datetime = self.datetime_input.dateTime().toPython()

        try:
            with local_db.get_session() as session:
                service = AppointmentService(session)
                service.create_appointment(
                    self.clinic_id, patient_id, appointment_datetime
                )
            QMessageBox.information(self, "موفقیت", "نوبت با موفقیت ثبت شد")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت نوبت:\n{str(e)}")
