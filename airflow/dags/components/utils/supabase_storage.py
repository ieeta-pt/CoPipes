import os
import json
import joblib
import tempfile
import logging
from typing import Any, Dict, Optional
from supabase import create_client, Client
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class SupabaseStorage:
    """
    Utility class for storing and retrieving files from Supabase Storage
    """
    
    def __init__(self):
        # Get Supabase credentials from environment variables
        self.supabase_url = os.getenv('SUPABASE_PUBLIC_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role for admin access
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.bucket_name = 'ml-pipeline-storage'
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create the storage bucket if it doesn't exist"""
        try:
            # Try to get bucket info
            self.client.storage.get_bucket(self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")
        except Exception:
            # Create bucket if it doesn't exist
            try:
                self.client.storage.create_bucket(self.bucket_name, options={"public": False})
                logger.info(f"Created new bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"Could not create bucket (might already exist): {e}")
    
    def save_joblib(self, obj: Any, path: str) -> str:
        """
        Save a joblib-serializable object to Supabase Storage
        
        Args:
            obj: Object to save (model, preprocessor, etc.)
            path: Storage path (e.g., 'models/my_model.joblib')
        
        Returns:
            str: Storage path of the saved file
        """
        try:
            # Serialize object to bytes
            with tempfile.NamedTemporaryFile() as tmp_file:
                joblib.dump(obj, tmp_file.name)
                
                # Read the file content
                with open(tmp_file.name, 'rb') as f:
                    file_content = f.read()
            
            # Check if file exists and use update instead of upload
            if self.file_exists(path):
                logger.info(f"File exists, updating: {path}")
                response = self.client.storage.from_(self.bucket_name).update(
                    path=path,
                    file=file_content,
                    file_options={"content-type": "application/octet-stream"}
                )
            else:
                # Upload new file
                response = self.client.storage.from_(self.bucket_name).upload(
                    path=path,
                    file=file_content,
                    file_options={"content-type": "application/octet-stream"}
                )
            
            logger.info(f"Saved joblib object to Supabase Storage: {path}")
            return path
            
        except Exception as e:
            logger.error(f"Failed to save joblib object to Supabase Storage: {e}")
            raise
    
    def load_joblib(self, path: str) -> Any:
        """
        Load a joblib object from Supabase Storage
        
        Args:
            path: Storage path of the file
        
        Returns:
            Deserialized object
        """
        try:
            # Download file from Supabase Storage
            response = self.client.storage.from_(self.bucket_name).download(path)
            
            # Create temporary file and load object
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(response)
                tmp_file.flush()
                obj = joblib.load(tmp_file.name)
            
            logger.info(f"Loaded joblib object from Supabase Storage: {path}")
            return obj
            
        except Exception as e:
            logger.error(f"Failed to load joblib object from Supabase Storage: {e}")
            raise
    
    def save_json(self, data: Dict, path: str) -> str:
        """
        Save JSON data to Supabase Storage
        
        Args:
            data: Dictionary to save as JSON
            path: Storage path (e.g., 'metadata/model_info.json')
        
        Returns:
            str: Storage path of the saved file
        """
        try:
            json_content = json.dumps(data, indent=2, default=str).encode('utf-8')
            
            # Check if file exists and use update instead of upload
            if self.file_exists(path):
                logger.info(f"File exists, updating: {path}")
                response = self.client.storage.from_(self.bucket_name).update(
                    path=path,
                    file=json_content,
                    file_options={"content-type": "application/json"}
                )
            else:
                response = self.client.storage.from_(self.bucket_name).upload(
                    path=path,
                    file=json_content,
                    file_options={"content-type": "application/json"}
                )
            
            logger.info(f"Saved JSON to Supabase Storage: {path}")
            return path
            
        except Exception as e:
            logger.error(f"Failed to save JSON to Supabase Storage: {e}")
            raise
    
    def load_json(self, path: str) -> Dict:
        """
        Load JSON data from Supabase Storage
        
        Args:
            path: Storage path of the file
        
        Returns:
            Dictionary loaded from JSON
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(path)
            data = json.loads(response.decode('utf-8'))
            
            logger.info(f"Loaded JSON from Supabase Storage: {path}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load JSON from Supabase Storage: {e}")
            raise
    
    def save_text(self, content: str, path: str) -> str:
        """
        Save text content to Supabase Storage
        
        Args:
            content: Text content to save
            path: Storage path (e.g., 'reports/analysis.txt')
        
        Returns:
            str: Storage path of the saved file
        """
        try:
            content_bytes = content.encode('utf-8')
            
            # Check if file exists and use update instead of upload
            if self.file_exists(path):
                logger.info(f"File exists, updating: {path}")
                response = self.client.storage.from_(self.bucket_name).update(
                    path=path,
                    file=content_bytes,
                    file_options={"content-type": "text/plain"}
                )
            else:
                response = self.client.storage.from_(self.bucket_name).upload(
                    path=path,
                    file=content_bytes,
                    file_options={"content-type": "text/plain"}
                )
            
            logger.info(f"Saved text to Supabase Storage: {path}")
            return path
            
        except Exception as e:
            logger.error(f"Failed to save text to Supabase Storage: {e}")
            raise
    
    def load_text(self, path: str) -> str:
        """
        Load text content from Supabase Storage
        
        Args:
            path: Storage path of the file
        
        Returns:
            Text content
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(path)
            content = response.decode('utf-8')
            
            logger.info(f"Loaded text from Supabase Storage: {path}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to load text from Supabase Storage: {e}")
            raise
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in Supabase Storage
        
        Args:
            path: Storage path to check
        
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            # Try to get file info
            files = self.client.storage.from_(self.bucket_name).list(path=os.path.dirname(path))
            filename = os.path.basename(path)
            
            for file_info in files:
                if file_info['name'] == filename:
                    return True
            return False
            
        except Exception:
            return False
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file from Supabase Storage
        
        Args:
            path: Storage path of the file to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.client.storage.from_(self.bucket_name).remove([path])
            logger.info(f"Deleted file from Supabase Storage: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file from Supabase Storage: {e}")
            return False
    
    def list_files(self, path: str = "") -> list:
        """
        List files in a Supabase Storage directory
        
        Args:
            path: Directory path (empty string for root)
        
        Returns:
            List of file information dictionaries
        """
        try:
            files = self.client.storage.from_(self.bucket_name).list(path=path)
            logger.info(f"Listed {len(files)} files in Supabase Storage: {path}")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files in Supabase Storage: {e}")
            return []
    
    def get_public_url(self, path: str) -> Optional[str]:
        """
        Get a public URL for a file (if bucket is public)
        
        Args:
            path: Storage path of the file
        
        Returns:
            Public URL if available, None otherwise
        """
        try:
            response = self.client.storage.from_(self.bucket_name).get_public_url(path)
            return response
            
        except Exception as e:
            logger.error(f"Failed to get public URL: {e}")
            return None
    
    def create_signed_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Create a signed URL for temporary access to a file
        
        Args:
            path: Storage path of the file
            expires_in: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Signed URL if successful, None otherwise
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

    def download_from_bucket(self, path: str, bucket_name: str) -> bytes:
        """Download raw file bytes from a specified Supabase Storage bucket."""
        try:
            response = self.client.storage.from_(bucket_name).download(path)
            logger.info(f"Downloaded file from bucket '{bucket_name}': {path}")
            return response
        except Exception as e:
            logger.error(f"Failed to download from bucket '{bucket_name}', path '{path}': {e}")
            raise

# Global instance
storage = SupabaseStorage()