from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTabWidget,
    QStatusBar,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont
import asyncio

from app.database.local_db import local_db
from app.database.sync import sync_engine
from app.config import settings
from .widgets.patient_widget import PatientWidget
from .widgets.appointment_widget import AppointmentWidget
from .widgets.report_widget import ReportWidget
from .widgets.clinic_widget import ClinicWidget


class SyncRunner(QThread):
    """Runs sync in a background thread to avoid blocking UI and event-loop issues."""
    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(sync_engine.perform_sync())
            loop.close()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, clinic_id: str):
        super().__init__()
        self.clinic_id = clinic_id
        self._sync_runner = None
        self.init_ui()
        self.setup_sync()

    def init_ui(self):
        self.setWindowTitle(f"{settings.app_name} - نسخه {settings.app_version}")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        header = self.create_header()
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.patient_widget = PatientWidget(self.clinic_id)
        self.appointment_widget = AppointmentWidget(self.clinic_id)
        self.report_widget = ReportWidget(self.clinic_id)
        self.clinic_widget = ClinicWidget(self.clinic_id, self)

        self.tabs.addTab(self.patient_widget, "بیماران")
        self.tabs.addTab(self.appointment_widget, "نوبت‌دهی")
        self.tabs.addTab(self.report_widget, "گزارشات")
        self.tabs.addTab(self.clinic_widget, "مطب")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("آماده")

    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout()
        header.setLayout(layout)

        title = QLabel("سیستم مدیریت مطب")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        self.sync_button = QPushButton("همگام‌سازی")
        self.sync_button.clicked.connect(self.manual_sync)
        layout.addWidget(self.sync_button)

        mode_label = QLabel(f"حالت: {settings.app_mode}")
        layout.addWidget(mode_label)

        return header

    def setup_sync(self):
        if settings.auto_sync_enabled and settings.app_mode in ["online", "hybrid"]:
            self.sync_timer = QTimer()
            self.sync_timer.timeout.connect(self.auto_sync)
            self.sync_timer.start(settings.sync_interval_minutes * 60 * 1000)

    def manual_sync(self):
        if self._sync_runner and self._sync_runner.isRunning():
            return
        self.update_status("در حال همگام‌سازی...")
        self.sync_button.setEnabled(False)
        self._sync_runner = SyncRunner()
        self._sync_runner.finished.connect(self._on_sync_finished)
        self._sync_runner.error.connect(self._on_sync_error)
        self._sync_runner.start()

    def _on_sync_finished(self, result: dict):
        self.sync_button.setEnabled(True)
        if result.get("to_remote") or result.get("from_remote"):
            self.update_status("همگام‌سازی با موفقیت انجام شد")
            QMessageBox.information(
                self, "موفقیت", "داده‌ها با موفقیت همگام‌سازی شدند"
            )
        else:
            self.update_status("همگام‌سازی امکان‌پذیر نیست")
            QMessageBox.warning(
                self,
                "هشدار",
                "امکان همگام‌سازی وجود ندارد. لطفاً اتصال اینترنت را بررسی کنید.",
            )

    def _on_sync_error(self, message: str):
        self.sync_button.setEnabled(True)
        self.update_status(f"خطا در همگام‌سازی: {message}")
        QMessageBox.critical(self, "خطا", f"خطا در همگام‌سازی:\n{message}")

    def auto_sync(self):
        if settings.app_mode not in ["online", "hybrid"]:
            return
        if self._sync_runner and self._sync_runner.isRunning():
            return
        self._sync_runner = SyncRunner()
        self._sync_runner.finished.connect(
            lambda r: self.update_status("همگام‌سازی خودکار انجام شد")
        )
        self._sync_runner.error.connect(
            lambda m: self.update_status(f"خطا در همگام‌سازی خودکار: {m}")
        )
        self._sync_runner.start()

    def update_status(self, message: str):
        self.status_bar.showMessage(message)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "خروج",
            "آیا از خروج اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            local_db.close()
            event.accept()
        else:
            event.ignore()
