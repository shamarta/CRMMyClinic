from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import date

from app.database.local_db import local_db
from app.services.report_service import ReportService


class ReportWidget(QWidget):
    def __init__(self, clinic_id: str = None):
        super().__init__()
        self.clinic_id = clinic_id
        self.init_ui()
        self.load_reports()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)

        toolbar.addWidget(QLabel("نوع گزارش:"))

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["امروز", "ماه جاری", "آمار کلی"])
        self.report_type_combo.currentTextChanged.connect(self.load_reports)
        toolbar.addWidget(self.report_type_combo)

        toolbar.addStretch()

        refresh_button = QPushButton("بروزرسانی")
        refresh_button.clicked.connect(self.load_reports)
        toolbar.addWidget(refresh_button)

        self.stats_group = QGroupBox("آمار کلی")
        stats_layout = QVBoxLayout()
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)

        self.stats_label = QLabel()
        stats_font = QFont()
        stats_font.setPointSize(12)
        self.stats_label.setFont(stats_font)
        stats_layout.addWidget(self.stats_label)

        self.details_table = QTableWidget()
        layout.addWidget(self.details_table)

    def load_reports(self):
        report_type = self.report_type_combo.currentText()

        with local_db.get_session() as session:
            service = ReportService(session)

            if report_type == "امروز":
                self.load_daily_report(service)
            elif report_type == "ماه جاری":
                self.load_monthly_report(service)
            else:
                self.load_overall_stats(service)

    def load_daily_report(self, service: ReportService):
        today = date.today()
        report = service.get_daily_revenue(self.clinic_id, today)

        stats_text = f"""
        <b>گزارش روزانه - {report['date']}</b><br>
        مجموع نوبت‌ها: {report['total_appointments']}<br>
        تکمیل شده: {report['completed_appointments']}<br>
        لغو شده: {report['cancelled_appointments']}<br>
        <br>
        <b>درآمد کل: {report['total_revenue']:,} تومان</b><br>
        پرداخت شده: {report['total_paid']:,} تومان<br>
        باقیمانده: {report['total_pending']:,} تومان
        """
        self.stats_label.setText(stats_text)

        self.details_table.setVisible(False)

    def load_monthly_report(self, service: ReportService):
        today = date.today()
        report = service.get_monthly_revenue(
            self.clinic_id, today.year, today.month
        )

        stats_text = f"""
        <b>گزارش ماهانه - {report['year']}/{report['month']}</b><br>
        مجموع نوبت‌ها: {report['total_appointments']}<br>
        <br>
        <b>درآمد کل: {report['total_revenue']:,} تومان</b><br>
        پرداخت شده: {report['total_paid']:,} تومان<br>
        باقیمانده: {report['total_pending']:,} تومان
        """
        self.stats_label.setText(stats_text)

        daily_breakdown = report.get("daily_breakdown", {})
        self.details_table.setVisible(True)
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(
            ["تاریخ", "تعداد نوبت", "درآمد", "پرداخت شده"]
        )
        self.details_table.setRowCount(len(daily_breakdown))

        for row, (day, data) in enumerate(daily_breakdown.items()):
            self.details_table.setItem(row, 0, QTableWidgetItem(day))
            self.details_table.setItem(
                row, 1, QTableWidgetItem(str(data["appointments"]))
            )
            self.details_table.setItem(
                row, 2, QTableWidgetItem(f"{data['revenue']:,}")
            )
            self.details_table.setItem(
                row, 3, QTableWidgetItem(f"{data['paid']:,}")
            )

        self.details_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

    def load_overall_stats(self, service: ReportService):
        stats = service.get_clinic_stats(self.clinic_id)

        stats_text = f"""
        <b>آمار کلی مطب</b><br>
        <br>
        تعداد کل بیماران: {stats['total_patients']}<br>
        تعداد کل نوبت‌ها: {stats['total_appointments']}<br>
        نوبت‌های امروز: {stats['today_appointments']}<br>
        نوبت‌های هفته آینده: {stats['upcoming_appointments']}
        """
        self.stats_label.setText(stats_text)

        self.details_table.setVisible(False)
