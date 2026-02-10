import os
import logging
from typing import Optional
from supabase import Client
from services.supabase_client import supabase_admin

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """
    Storage service for uploading and managing user files in Supabase Storage.
    Used by the FastAPI backend for file upload operations.
    """

    def __init__(self):
        self.client: Client = supabase_admin
        self.bucket_name = 'user-uploads'
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create the storage bucket if it doesn't exist (private bucket)."""
        try:
            self.client.storage.get_bucket(self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")
        except Exception:
            try:
                self.client.storage.create_bucket(self.bucket_name, options={"public": False})
                logger.info(f"Created new bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"Could not create bucket (might already exist): {e}")

    def upload_file(self, content: bytes, path: str, content_type: str) -> str:
        """
        Upload file to Supabase Storage.

        Args:
            content: File content as bytes
            path: Storage path (e.g., 'uploads/user-id/filename.csv')
            content_type: MIME type of the file

        Returns:
            str: The storage path of the uploaded file
        """
        try:
            if self.file_exists(path):
                logger.info(f"File exists, updating: {path}")
                self.client.storage.from_(self.bucket_name).update(
                    path=path,
                    file=content,
                    file_options={"content-type": content_type}
                )
            else:
                self.client.storage.from_(self.bucket_name).upload(
                    path=path,
                    file=content,
                    file_options={"content-type": content_type}
                )

            logger.info(f"Uploaded file to Supabase Storage: {path}")
            return path

        except Exception as e:
            logger.error(f"Failed to upload file to Supabase Storage: {e}")
            raise

    def download_file(self, path: str) -> bytes:
        """
        Download file from Supabase Storage.

        Args:
            path: Storage path of the file

        Returns:
            bytes: File content
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(path)
            logger.info(f"Downloaded file from Supabase Storage: {path}")
            return response

        except Exception as e:
            logger.error(f"Failed to download file from Supabase Storage: {e}")
            raise

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in Supabase Storage.

        Args:
            path: Storage path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            dir_path = os.path.dirname(path)
            filename = os.path.basename(path)
            files = self.client.storage.from_(self.bucket_name).list(path=dir_path)

            for file_info in files:
                if file_info['name'] == filename:
                    return True
            return False

        except Exception:
            return False

    def delete_file(self, path: str) -> bool:
        """
        Delete a file from Supabase Storage.

        Args:
            path: Storage path of the file to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.storage.from_(self.bucket_name).remove([path])
            logger.info(f"Deleted file from Supabase Storage: {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file from Supabase Storage: {e}")
            return False

    def create_signed_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Create a signed URL for temporary access to a file.

        Args:
            path: Storage path of the file
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Signed URL if successful, None otherwise
        """
        try:
            response = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=path,
                expires_in=expires_in
            )
            return response['signedURL']

        except Exception as e:
            logger.error(f"Failed to create signed URL: {e}")
            return None


# Global instance
storage_service = SupabaseStorageService()
