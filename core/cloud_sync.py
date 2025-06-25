"""
Cloud Synchronization Module for Atlas

This module handles cloud storage integration for data backup, real-time synchronization
across devices, and ensures data security during transmission and storage.
"""

import os
import logging
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime

import boto3
import requests
from botocore.exceptions import ClientError

from core.logging import get_logger
from core.config import load_config

from security.security_utils import encrypt_data, decrypt_data

# Set up logging
logger = get_logger("CloudSync")

class CloudSyncManager:
    """Manages cloud synchronization for Atlas application data."""
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "dev"):
        """
        Initialize the Cloud Sync Manager with configuration.
        
        Args:
            config_path (str, optional): Path to configuration file
            environment (str): Deployment environment (dev, staging, prod)
        """
        self.config = load_config(config_path, environment=environment)
        self.cloud_config = self.config.get("cloud_sync", {})
        self.enabled = self.cloud_config.get("enabled", False)
        
        if not self.enabled:
            logger.warning("Cloud synchronization is disabled in configuration")
            return
        
        self.provider = self.cloud_config.get("provider", "aws")
        self.bucket_name = self.cloud_config.get("bucket_name")
        self.region = self.cloud_config.get("region", "us-east-1")
        self.sync_interval = self.cloud_config.get("sync_interval", 300)  # seconds
        self.local_data_path = self.cloud_config.get("local_data_path", "data")
        self.cloud_data_path = self.cloud_config.get("cloud_data_path", "atlas-data")
        self.encryption_key = self.cloud_config.get("encryption_key")
        
        if not all([self.bucket_name, self.encryption_key]):
            logger.error("Missing required cloud sync configuration")
            self.enabled = False
            return
        
        # Initialize AWS S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            logger.info("CloudSync initialized with provider: %s", self.provider)
        except Exception as e:
            logger.error("Failed to initialize cloud sync: %s", str(e))
            self.enabled = False
        
        # Synchronization thread
        self.sync_thread = None
        self.stop_event = threading.Event()
    
    def start_sync(self) -> None:
        """Start the background synchronization thread."""
        if not self.enabled:
            logger.warning("Cannot start sync: Cloud synchronization is disabled")
            return
        
        self.stop_event.clear()
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("Cloud synchronization started")
    
    def stop_sync(self) -> None:
        """Stop the background synchronization thread."""
        if not self.enabled or not self.sync_thread:
            return
        
        self.stop_event.set()
        if self.sync_thread:
            self.sync_thread.join(timeout=2.0)
        logger.info("Cloud synchronization stopped")
    
    def _sync_loop(self) -> None:
        """Main synchronization loop running in background thread."""
        while not self.stop_event.is_set():
            try:
                self.perform_sync()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error("Error in sync loop: %s", str(e))
                time.sleep(60)  # Wait briefly before retrying on error
    
    def perform_sync(self) -> bool:
        """
        Perform a full synchronization cycle - upload local changes and download remote changes.
        
        Returns:
            bool: True if sync successful, False otherwise
        """
        if not self.enabled:
            return False
        
        logger.info("Starting cloud synchronization cycle")
        try:
            # Upload local changes to cloud
            if not self._upload_local_changes():
                logger.warning("Failed to upload local changes")
            
            # Download remote changes
            if not self._download_remote_changes():
                logger.warning("Failed to download remote changes")
            
            logger.info("Cloud synchronization cycle completed")
            return True
        except Exception as e:
            logger.error("Synchronization cycle failed: %s", str(e))
            return False
    
    def _upload_local_changes(self) -> bool:
        """
        Upload local data files to cloud storage if they have been modified.
        
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            for root, _, files in os.walk(self.local_data_path):
                for filename in files:
                    local_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(local_path, self.local_data_path)
                    cloud_key = f"{self.cloud_data_path}/{relative_path}"
                    
                    # Check if local file is newer than cloud version
                    local_mtime = os.path.getmtime(local_path)
                    cloud_mtime = self._get_cloud_file_mtime(cloud_key)
                    
                    if cloud_mtime is None or local_mtime > cloud_mtime:
                        logger.info("Uploading updated file: %s", relative_path)
                        
                        # Read and encrypt the file content
                        with open(local_path, 'rb') as f:
                            data = f.read()
                        encrypted_data = encrypt_data(data, self.encryption_key)
                        
                        # Upload encrypted data
                        self.s3_client.put_object(
                            Bucket=self.bucket_name,
                            Key=cloud_key,
                            Body=encrypted_data,
                            Metadata={
                                'mtime': str(local_mtime),
                                'encrypted': 'true'
                            }
                        )
            return True
        except Exception as e:
            logger.error("Failed to upload local changes: %s", str(e))
            return False
    
    def _download_remote_changes(self) -> bool:
        """
        Download files from cloud storage that are newer than local versions.
        
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.cloud_data_path
            )
            
            for obj in response.get('Contents', []):
                cloud_key = obj['Key']
                relative_path = os.path.relpath(cloud_key, self.cloud_data_path)
                local_path = os.path.join(self.local_data_path, relative_path)
                
                cloud_mtime_str = obj.get('Metadata', {}).get('mtime', '0')
                try:
                    cloud_mtime = float(cloud_mtime_str)
                except ValueError:
                    cloud_mtime = 0
                
                # Check if cloud file is newer than local version
                local_mtime = os.path.getmtime(local_path) if os.path.exists(local_path) else 0
                
                if cloud_mtime > local_mtime:
                    logger.info("Downloading updated file: %s", relative_path)
                    
                    # Ensure local directory exists
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    
                    # Download and decrypt the file content
                    encrypted_data = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=cloud_key
                    )['Body'].read()
                    
                    decrypted_data = decrypt_data(encrypted_data, self.encryption_key)
                    
                    # Write decrypted data to local file
                    with open(local_path, 'wb') as f:
                        f.write(decrypted_data)
                    
                    # Update local file modification time to match cloud
                    os.utime(local_path, (os.path.getatime(local_path), cloud_mtime))
            return True
        except Exception as e:
            logger.error("Failed to download remote changes: %s", str(e))
            return False
    
    def _get_cloud_file_mtime(self, cloud_key: str) -> Optional[float]:
        """
        Get the modification time of a file in cloud storage.
        
        Args:
            cloud_key (str): Key of the file in cloud storage
        
        Returns:
            float, optional: Modification time as float timestamp, or None if file doesn't exist
        """
        try:
            head = self.s3_client.head_object(Bucket=self.bucket_name, Key=cloud_key)
            mtime_str = head.get('Metadata', {}).get('mtime', '0')
            return float(mtime_str) if mtime_str else None
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise
