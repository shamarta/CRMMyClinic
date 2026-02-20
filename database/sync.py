import asyncio
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.config import settings
from .models import Clinic, Patient, Appointment, SyncLog, Base
from .local_db import local_db
from .remote_db import remote_db

logger = logging.getLogger(__name__)


class SyncEngine:
    def __init__(self):
        self.sync_enabled = settings.app_mode in ["online", "hybrid"]
        self.sync_interval = settings.sync_interval_minutes * 60
        self.running = False

    def _get_entity_mapping(self) -> Dict[str, Any]:
        return {
            "clinics": Clinic,
            "patients": Patient,
            "appointments": Appointment,
        }

    def _model_to_dict(self, obj: Base) -> Dict[str, Any]:
        data = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if value is None:
                data[column.name] = None
            elif isinstance(value, datetime):
                data[column.name] = value.isoformat()
            elif isinstance(value, date):
                data[column.name] = value.isoformat()
            elif isinstance(value, Decimal):
                data[column.name] = float(value)
            else:
                data[column.name] = value
        return data

    async def sync_to_remote(self, session: Session) -> bool:
        if not remote_db.is_available():
            logger.warning("Remote database not available for sync")
            return False

        entity_mapping = self._get_entity_mapping()
        success = True

        for table_name, model_class in entity_mapping.items():
            try:
                pending_entities = (
                    session.query(model_class)
                    .filter(
                        model_class.deleted_at.is_(None),
                        or_(
                            model_class.sync_status == "pending",
                            model_class.last_synced_at.is_(None),
                            model_class.last_synced_at < model_class.updated_at,
                        ),
                    )
                    .all()
                )

                for entity in pending_entities:
                    data = self._model_to_dict(entity)

                    sync_success = await remote_db.sync_entity(
                        table_name, entity.id, data
                    )

                    if sync_success:
                        entity.sync_status = "synced"
                        entity.last_synced_at = datetime.utcnow()

                        sync_log = SyncLog(
                            entity_type=table_name,
                            entity_id=entity.id,
                            operation="upload",
                            sync_direction="local_to_remote",
                            status="success",
                        )
                        session.add(sync_log)
                    else:
                        entity.sync_status = "failed"
                        sync_log = SyncLog(
                            entity_type=table_name,
                            entity_id=entity.id,
                            operation="upload",
                            sync_direction="local_to_remote",
                            status="failed",
                            error_message="Failed to sync to remote",
                        )
                        session.add(sync_log)
                        success = False

                session.commit()
                logger.info(f"Synced {len(pending_entities)} {table_name} to remote")

            except Exception as e:
                logger.error(f"Error syncing {table_name} to remote: {e}")
                session.rollback()
                success = False

        return success

    async def sync_from_remote(self, session: Session) -> bool:
        if not remote_db.is_available():
            logger.warning("Remote database not available for sync")
            return False

        entity_mapping = self._get_entity_mapping()
        success = True

        for table_name, model_class in entity_mapping.items():
            try:
                last_sync = (
                    session.query(model_class.last_synced_at)
                    .order_by(model_class.last_synced_at.desc())
                    .first()
                )

                last_sync_time = (
                    last_sync[0].isoformat() if last_sync and last_sync[0] else None
                )

                remote_updates = await remote_db.fetch_updates(
                    table_name, last_sync_time
                )

                for remote_data in remote_updates:
                    entity_id = remote_data.get("id")
                    existing = session.query(model_class).filter_by(id=entity_id).first()

                    if existing:
                        for key, value in remote_data.items():
                            if hasattr(existing, key) and key not in ["id"]:
                                setattr(existing, key, value)
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        new_entity = model_class(**remote_data)
                        new_entity.last_synced_at = datetime.utcnow()
                        session.add(new_entity)

                    sync_log = SyncLog(
                        entity_type=table_name,
                        entity_id=entity_id,
                        operation="download",
                        sync_direction="remote_to_local",
                        status="success",
                    )
                    session.add(sync_log)

                session.commit()
                logger.info(
                    f"Synced {len(remote_updates)} {table_name} from remote"
                )

            except Exception as e:
                logger.error(f"Error syncing {table_name} from remote: {e}")
                session.rollback()
                success = False

        return success

    async def perform_sync(self) -> Dict[str, bool]:
        if not self.sync_enabled:
            logger.info("Sync is disabled in current app mode")
            return {"to_remote": False, "from_remote": False}

        logger.info("Starting synchronization...")

        with local_db.get_session() as session:
            to_remote = await self.sync_to_remote(session)
            from_remote = await self.sync_from_remote(session)

        logger.info(
            f"Sync completed. To remote: {to_remote}, From remote: {from_remote}"
        )

        return {"to_remote": to_remote, "from_remote": from_remote}

    async def start_auto_sync(self):
        if not settings.auto_sync_enabled or not self.sync_enabled:
            logger.info("Auto-sync is disabled")
            return

        self.running = True
        logger.info(f"Auto-sync started with interval: {self.sync_interval}s")

        while self.running:
            try:
                await self.perform_sync()
            except Exception as e:
                logger.error(f"Error in auto-sync: {e}")

            await asyncio.sleep(self.sync_interval)

    def stop_auto_sync(self):
        self.running = False
        logger.info("Auto-sync stopped")


sync_engine = SyncEngine()
