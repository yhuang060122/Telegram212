from app.infrastructure.supabase import SupabaseClient


class Storage:
    """Application storage provider."""

    def __init__(self):
        self.client = SupabaseClient()