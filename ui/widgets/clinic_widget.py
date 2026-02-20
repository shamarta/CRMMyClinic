"""ویجت مدیریت مطب - نمایش و ویرایش اطلاعات مطب."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Qt

from app.database.local_db import local_db
from app.services.clinic_service import ClinicService
from app.config import settings


class ClinicWidget(QWidget):
    def __init__(self, clinic_id: str, main_window=None):
        super().__init__()
        self.clinic_id = clinic_id
        self.main_window = main_window
        self.init_ui()
        self.load_clinic()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.group = QGroupBox("اطلاعات مطب")
        form = QFormLayout()
        self.group.setLayout(form)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام مطب")
        form.addRow("نام مطب:", self.name_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("آدرس")
        form.addRow("آدرس:", self.address_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("تلفن")
        form.addRow("تلفن:", self.phone_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ایمیل")
        form.addRow("ایمیل:", self.email_input)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("شماره پروانه")
        form.addRow("شماره پروانه:", self.license_input)

        layout.addWidget(self.group)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("ذخیره تغییرات")
        save_btn.clicked.connect(self.save_clinic)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # وضعیت ماژول‌ها
        mod_group = QGroupBox("وضعیت ماژول‌ها")
        mod_layout = QVBoxLayout()
        self.mode_label = QLabel()
        self.sms_label = QLabel()
        mod_layout.addWidget(self.mode_label)
        mod_layout.addWidget(self.sms_label)
        mod_group.setLayout(mod_layout)
        layout.addWidget(mod_group)
        layout.addStretch()

    def load_clinic(self):
        with local_db.get_session() as session:
            clinic = ClinicService(session).get_clinic(self.clinic_id)
            if clinic:
                self.name_input.setText(clinic.name or "")
                self.address_input.setText(clinic.address or "")
                self.phone_input.setText(clinic.phone or "")
                self.email_input.setText(clinic.email or "")
                self.license_input.setText(clinic.license_number or "")
        self.mode_label.setText("حالت برنامه: %s" % settings.app_mode)
        from app.services.sms_service import sms_service
        self.sms_label.setText(
            "یادآوری پیامکی: %s" % ("فعال" if sms_service.is_enabled() else "غیرفعال")
        )

    def save_clinic(self):
        try:
            with local_db.get_session() as session:
                ClinicService(session).update_clinic(
                    self.clinic_id,
                    name=self.name_input.text().strip(),
                    address=self.address_input.text().strip(),
                    phone=self.phone_input.text().strip(),
                    email=self.email_input.text().strip(),
                    license_number=self.license_input.text().strip(),
                )
            QMessageBox.information(self, "موفقیت", "اطلاعات مطب ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", "خطا در ذخیره:\n%s" % str(e))
