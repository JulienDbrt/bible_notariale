from minio import Minio
from minio.error import S3Error
import os
from typing import Optional, Any
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class MinioService:
    def __init__(self) -> None:
        self.client: Optional[Minio] = None
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "training-docs")
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
        self.secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
    async def initialize(self) -> None:
        """Initialize Minio client and create bucket if it doesn't exist"""
        try:
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # Create bucket if it doesn't exist
            if self.client and not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket {self.bucket_name} already exists")
                
        except Exception as e:
            logger.error(f"Failed to initialize Minio client: {e}")
            raise e
    
    async def upload_file(self, file_content: bytes, filename: str, file_id: str) -> str:
        """Upload file to Minio and return the object path"""
        if not self.client:
            await self.initialize()
            
        try:
            # Create a unique object name
            file_extension = os.path.splitext(filename)[1]
            object_name = f"{file_id}{file_extension}"
            
            # Upload file
            from io import BytesIO
            file_stream = BytesIO(file_content)
            
            if self.client:
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    data=file_stream,
                    length=len(file_content),
                    content_type=self._get_content_type(file_extension)
                )
            
            # Return the full path
            minio_path = f"s3://{self.bucket_name}/{object_name}"
            logger.info(f"File uploaded successfully to: {minio_path}")
            return minio_path
            
        except S3Error as e:
            logger.error(f"Minio S3 error: {e}")
            raise Exception(f"Failed to upload file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise Exception(f"Failed to upload file: {e}")
    
    async def download_file(self, object_name: str) -> bytes:
        """Download file from Minio"""
        if not self.client:
            await self.initialize()
            
        try:
            # Extract object name from full path if needed
            if object_name.startswith("s3://"):
                object_name = object_name.split("/")[-1]
                
            if self.client:
                response = self.client.get_object(self.bucket_name, object_name)
                data: bytes = response.read()
                response.close()
                response.release_conn()
                return data
            return b""
            
        except S3Error as e:
            logger.error(f"Minio S3 error downloading file: {e}")
            raise Exception(f"Failed to download file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {e}")
            raise Exception(f"Failed to download file: {e}")
    
    async def delete_file(self, object_name: str) -> bool:
        """Delete file from Minio"""
        if not self.client:
            await self.initialize()
            
        try:
            # Extract object name from full path if needed
            if object_name.startswith("s3://"):
                object_name = object_name.split("/")[-1]
                
            if self.client:
                self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"File deleted successfully: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Minio S3 error deleting file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {e}")
            return False
    
    def list_files(self) -> Any:
        """List all files in the MinIO bucket"""
        if not self.client:
            # Need to initialize synchronously for this method
            import asyncio
            asyncio.create_task(self.initialize())
            
        try:
            if self.client:
                objects = self.client.list_objects(self.bucket_name, recursive=True)
            else:
                objects = []
            return list(objects)
        except S3Error as e:
            logger.error(f"Minio S3 error listing files: {e}")
            raise Exception(f"Failed to list files: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            raise Exception(f"Failed to list files: {e}")
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')

# Global Minio service instance
minio_service = None

def get_minio_service() -> MinioService:
    """Dependency function for FastAPI"""
    global minio_service
    if minio_service is None:
        minio_service = MinioService()
    return minio_service