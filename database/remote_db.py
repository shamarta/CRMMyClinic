from typing import Optional, Dict, List, Any
import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


class RemoteDatabase:
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize()

    def _initialize(self):
        if not settings.supabase_url or not settings.supabase_anon_key:
            logger.warning("Supabase credentials not configured. Remote sync disabled.")
            return

        try:
            self.client = create_client(
                settings.supabase_url, settings.supabase_anon_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")

    def is_available(self) -> bool:
        return self.client is not None

    async def sync_entity(
        self, table: str, entity_id: str, data: Dict[str, Any]
    ) -> bool:
        if not self.is_available():
            return False

        try:
            response = (
                self.client.table(table).upsert(data, on_conflict="id").execute()
            )
            return True
        except Exception as e:
            logger.error(f"Failed to sync entity to Supabase: {e}")
            return False

    async def fetch_updates(
        self, table: str, last_sync: str = None
    ) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []

        try:
            query = self.client.table(table).select("*")
            if last_sync:
                query = query.gt("updated_at", last_sync)

            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch updates from Supabase: {e}")
            return []

    async def delete_entity(self, table: str, entity_id: str) -> bool:
        if not self.is_available():
            return False

        try:
            self.client.table(table).update({"deleted_at": "now()"}).eq(
                "id", entity_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete entity in Supabase: {e}")
            return False


remote_db = RemoteDatabase()
