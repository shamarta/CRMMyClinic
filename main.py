import sys
import logging
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.config import settings
from app.database.local_db import local_db
from app.services.clinic_service import ClinicService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("clinic_crm.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Running in {settings.app_mode} mode")

    # Ensure default clinic exists (Local-first: data in SQLite first)
    with local_db.get_session() as session:
        clinic = ClinicService(session).ensure_default_clinic()
        clinic_id = clinic.id
    logger.info("Using clinic_id: %s", clinic_id)

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    app.setApplicationVersion(settings.app_version)

    window = MainWindow(clinic_id=clinic_id)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
