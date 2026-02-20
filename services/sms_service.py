"""
SMS Reminder Service - ماژول یادآوری پیامکی (ماژولار، قابل خاموش/روشن).
When SMS_ENABLED=false or no API key, all methods no-op.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional

from app.config import settings
from app.database.local_db import local_db
from app.database.models import Appointment

logger = logging.getLogger(__name__)


class SMSService:
    """Sends appointment reminders via SMS. Disabled when settings.sms_enabled is False."""

    def __init__(self):
        self.enabled = getattr(settings, "sms_enabled", False) and bool(
            getattr(settings, "sms_api_key", "")
        )
        self.provider = getattr(settings, "sms_provider", "kavenegar")

    def is_enabled(self) -> bool:
        return self.enabled

    def send_sms(self, mobile: str, message: str) -> bool:
        """Send a single SMS. Returns False if disabled or on error."""
        if not self.enabled:
            return False
        if not mobile or not message:
            return False
        try:
            return self._do_send(mobile, message)
        except Exception as e:
            logger.warning("SMS send failed: %s", e)
            return False

    def _do_send(self, mobile: str, message: str) -> bool:
        """Actual send implementation. Override or implement per provider (e.g. Kavenegar)."""
        # Kavenegar-style: HTTP GET/POST to API. Keep minimal for MVP.
        if self.provider == "kavenegar" and settings.sms_api_key:
            try:
                import httpx
                resp = httpx.get(
                    "https://api.kavenegar.com/v1/%s/sms/send.json" % settings.sms_api_key,
                    params={"receptor": mobile, "message": message},
                    timeout=10,
                )
                return resp.status_code == 200
            except Exception as e:
                logger.warning("Kavenegar send error: %s", e)
                return False
        return False

    def get_appointments_for_reminder(
        self, clinic_id: str, target_date: date, hours_ahead: int = 24
    ) -> List[Appointment]:
        """Appointments that should receive a reminder (scheduled, not yet reminded)."""
        with local_db.get_session() as session:
            start = datetime.combine(target_date, datetime.min.time())
            end = start + timedelta(hours=hours_ahead)
            appointments = (
                session.query(Appointment)
                .filter(
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                    Appointment.status == "scheduled",
                    Appointment.appointment_date >= start,
                    Appointment.appointment_date <= end,
                    Appointment.reminder_sent == False,  # noqa: E712
                )
                .all()
            )
            return list(appointments)

    def send_reminders_for_tomorrow(self, clinic_id: str) -> int:
        """Send reminders for tomorrow's appointments. Returns count sent."""
        if not self.enabled:
            return 0
        tomorrow = date.today() + timedelta(days=1)
        with local_db.get_session() as session:
            start = datetime.combine(tomorrow, datetime.min.time())
            end = start + timedelta(hours=24)
            from sqlalchemy.orm import joinedload

            appointments = (
                session.query(Appointment)
                .options(joinedload(Appointment.patient))
                .filter(
                    Appointment.clinic_id == clinic_id,
                    Appointment.deleted_at.is_(None),
                    Appointment.status == "scheduled",
                    Appointment.appointment_date >= start,
                    Appointment.appointment_date <= end,
                    Appointment.reminder_sent == False,  # noqa: E712
                )
                .all()
            )
            sent = 0
            for apt in appointments:
                mobile = apt.patient.mobile if apt.patient else None
                if not mobile:
                    continue
                text = "یادآور نوبت: فردا %s در مطب. در صورت عدم امکان حضور لطفاً تماس بگیرید." % (
                    apt.appointment_date.strftime("%H:%M"),
                )
                if self.send_sms(mobile, text):
                    sent += 1
                    apt.reminder_sent = True
                    apt.reminder_sent_at = datetime.utcnow()
                    apt.sync_status = "pending"
            return sent


sms_service = SMSService()
