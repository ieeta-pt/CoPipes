import os
import logging

logger = logging.getLogger(__name__)

LOCAL_DIRS = ["/opt/airflow/data/", "/shared_data/"]
DOWNLOAD_CACHE_DIR = "/tmp/copipes_downloads"
SUPABASE_BUCKET = "user-uploads"


def resolve_input_file(filename: str, user_id: str = None) -> str:
    """
    Resolve an input file path by checking local directories first,
    then downloading from Supabase Storage if a user_id is provided.

    Args:
        filename: The filename (or relative path) to resolve.
        user_id: Optional Supabase user ID for cloud storage lookup.

    Returns:
        Absolute path to the resolved file on local filesystem.

    Raises:
        FileNotFoundError: If the file cannot be found in any location.
    """
    searched = []

    # 1. Check legacy local paths
    for local_dir in LOCAL_DIRS:
        candidate = os.path.join(local_dir, filename)
        if os.path.isfile(candidate):
            logger.info(f"Resolved '{filename}' from local path: {candidate}")
            return candidate
        searched.append(candidate)

    # 2. Try downloading from Supabase Storage
    if user_id:
        storage_path = f"uploads/{user_id}/{filename}"
        local_dest = os.path.join(DOWNLOAD_CACHE_DIR, user_id, filename)
        searched.append(f"supabase://{SUPABASE_BUCKET}/{storage_path}")

        try:
            from components.utils.supabase_storage import storage

            data = storage.download_from_bucket(storage_path, SUPABASE_BUCKET)
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)
            with open(local_dest, "wb") as f:
                f.write(data)
            logger.info(f"Downloaded '{filename}' from Supabase to {local_dest}")
            return local_dest
        except Exception as e:
            logger.warning(f"Supabase download failed for '{storage_path}': {e}")

    raise FileNotFoundError(
        f"Could not resolve file '{filename}'. Searched: {searched}"
    )
