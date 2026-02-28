"""
File Manager for Advanced Scheduler and File Management feature

Handles file uploads, storage, retrieval, and deletion with:
- UUID-based file naming
- Directory structure organization (year/month)
- File type and MIME validation
- Size limit enforcement
- Reference tracking for safe deletion
"""

import uuid
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, BinaryIO
import sqlite3


class FileManager:
    """Manages file uploads, storage, and retrieval"""
    
    UPLOAD_DIR = Path("uploads/files")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    ALLOWED_TYPES = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'zip': 'application/zip'
    }
    
    FORBIDDEN_EXTENSIONS = {'exe', 'bat', 'sh', 'cmd', 'app', 'com', 'scr'}
    
    def __init__(self, db_path: str = "officer_priya.db"):
        """Initialize FileManager with database connection"""
        self.db_path = db_path
        self._ensure_upload_directory()
    
    def _ensure_upload_directory(self):
        """Ensure upload directory exists"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _validate_file_extension(self, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate file extension
        
        Returns:
            (is_valid, extension, error_message)
        """
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if not extension:
            return False, None, "File has no extension"
        
        if extension in self.FORBIDDEN_EXTENSIONS:
            return False, extension, f"File type .{extension} is forbidden for security reasons"
        
        if extension not in self.ALLOWED_TYPES:
            allowed = ', '.join(f'.{ext}' for ext in self.ALLOWED_TYPES.keys())
            return False, extension, f"File type .{extension} is not allowed. Allowed types: {allowed}"
        
        return True, extension, None
    
    def _validate_file_size(self, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate file size
        
        Returns:
            (is_valid, error_message)
        """
        if file_size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            return False, f"File size {actual_mb:.2f}MB exceeds maximum {max_mb:.0f}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    def _validate_mime_type(self, file_path: Path, expected_extension: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate MIME type matches file extension
        
        Returns:
            (is_valid, detected_mime, error_message)
        """
        try:
            # Try to use python-magic if available
            try:
                import magic
                mime = magic.from_file(str(file_path), mime=True)
            except ImportError:
                # Fallback: basic validation based on file signature
                mime = self._detect_mime_basic(file_path)
            
            expected_mime = self.ALLOWED_TYPES.get(expected_extension)
            
            if mime != expected_mime:
                return False, mime, f"File extension .{expected_extension} does not match detected MIME type {mime}"
            
            return True, mime, None
            
        except Exception as e:
            return False, None, f"Failed to validate MIME type: {str(e)}"
    
    def _detect_mime_basic(self, file_path: Path) -> str:
        """
        Basic MIME type detection based on file signatures
        Fallback when python-magic is not available
        """
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        # PDF signature
        if header.startswith(b'%PDF'):
            return 'application/pdf'
        
        # PNG signature
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        
        # JPEG signature
        if header.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        
        # ZIP signature (also used by DOCX)
        if header.startswith(b'PK\x03\x04'):
            # Check if it's a DOCX by looking for specific content
            try:
                import zipfile
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    if 'word/document.xml' in zip_ref.namelist():
                        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            except:
                pass
            return 'application/zip'
        
        # DOC signature
        if header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return 'application/msword'
        
        return 'application/octet-stream'
    
    def _generate_storage_path(self, extension: str) -> Tuple[str, Path]:
        """
        Generate storage path with year/month structure
        
        Returns:
            (file_id, full_path)
        """
        file_id = str(uuid.uuid4())
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        
        # Create directory structure
        dir_path = self.UPLOAD_DIR / year / month
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        filename = f"{file_id}.{extension}"
        full_path = dir_path / filename
        
        # Relative path for database storage
        relative_path = f"{year}/{month}/{filename}"
        
        return file_id, full_path, relative_path
    
    def save_file(self, file_data: BinaryIO, original_filename: str, uploaded_by: Optional[str] = None) -> dict:
        """
        Save uploaded file to storage
        
        Args:
            file_data: File binary data
            original_filename: Original filename from upload
            uploaded_by: Optional user identifier
        
        Returns:
            Dictionary with file metadata
        
        Raises:
            ValueError: If validation fails
            IOError: If file save fails
        """
        # Validate extension
        is_valid, extension, error = self._validate_file_extension(original_filename)
        if not is_valid:
            raise ValueError(error)
        
        # Save to temporary location first
        temp_path = self.UPLOAD_DIR / f"temp_{uuid.uuid4()}"
        try:
            # Write file data
            with open(temp_path, 'wb') as f:
                file_data.seek(0)
                shutil.copyfileobj(file_data, f)
            
            # Get file size
            file_size = temp_path.stat().st_size
            
            # Validate size
            is_valid, error = self._validate_file_size(file_size)
            if not is_valid:
                temp_path.unlink()
                raise ValueError(error)
            
            # Validate MIME type
            is_valid, mime_type, error = self._validate_mime_type(temp_path, extension)
            if not is_valid:
                temp_path.unlink()
                raise ValueError(error)
            
            # Generate final storage path
            file_id, final_path, relative_path = self._generate_storage_path(extension)
            
            # Move to final location
            shutil.move(str(temp_path), str(final_path))
            
            # Store metadata in database
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO files (file_id, original_name, file_type, mime_type, file_size, storage_path, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (file_id, original_filename, extension, mime_type, file_size, relative_path, uploaded_by))
            
            file_db_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'id': file_db_id,
                'file_id': file_id,
                'original_name': original_filename,
                'file_type': extension,
                'mime_type': mime_type,
                'file_size': file_size,
                'storage_path': relative_path,
                'created_at': datetime.now()
            }
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """
        Get full file path from file_id
        
        Args:
            file_id: UUID file identifier
        
        Returns:
            Full path to file or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT storage_path FROM files WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self.UPLOAD_DIR / row['storage_path']
    
    def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """
        Get file metadata from database
        
        Args:
            file_id: UUID file identifier
        
        Returns:
            Dictionary with file metadata or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Try with file_references join first
            cursor.execute("""
                SELECT f.*, COUNT(fr.id) as reference_count
                FROM files f
                LEFT JOIN file_references fr ON f.id = fr.file_id
                WHERE f.file_id = ?
                GROUP BY f.id
            """, (file_id,))
            
            row = cursor.fetchone()
        except sqlite3.OperationalError as e:
            # If file_references table doesn't exist, query without it
            if "no such table" in str(e):
                cursor.execute("""
                    SELECT *, 0 as reference_count
                    FROM files
                    WHERE file_id = ?
                """, (file_id,))
                
                row = cursor.fetchone()
            else:
                raise
        
        conn.close()
        
        if not row:
            return None
        
        return dict(row)
    
    def delete_file(self, file_id: str) -> Tuple[bool, Optional[str], Optional[list]]:
        """
        Delete file from storage and database
        
        Args:
            file_id: UUID file identifier
        
        Returns:
            (success, error_message, referencing_playlists)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if file exists
            cursor.execute("SELECT id, storage_path, file_id FROM files WHERE file_id = ?", (file_id,))
            file_row = cursor.fetchone()
            
            if not file_row:
                return False, f"File not found with file_id={file_id}", None
            
            file_db_id = file_row['id']
            storage_path = file_row['storage_path']
            
            # Check for references (only if table exists)
            try:
                cursor.execute("""
                    SELECT DISTINCT p.id, p.name
                    FROM file_references fr
                    JOIN content_items ci ON fr.content_item_id = ci.id
                    JOIN playlists p ON ci.playlist_id = p.id
                    WHERE fr.file_id = ?
                """, (file_db_id,))
                
                references = cursor.fetchall()
                
                if references:
                    playlist_list = [{'id': r['id'], 'name': r['name']} for r in references]
                    return False, "File is referenced in playlists", playlist_list
            except sqlite3.OperationalError as e:
                # Table doesn't exist yet, skip reference check
                if "no such table" not in str(e):
                    raise
            
            # Delete from database
            cursor.execute("DELETE FROM files WHERE id = ?", (file_db_id,))
            conn.commit()
            
            # Delete from filesystem
            file_path = self.UPLOAD_DIR / storage_path
            if file_path.exists():
                file_path.unlink()
            
            return True, None, None
            
        except Exception as e:
            conn.rollback()
            return False, str(e), None
        finally:
            conn.close()
    
    def list_files(self, file_type: Optional[str] = None, search: Optional[str] = None, 
                   limit: int = 50, offset: int = 0) -> Tuple[list, int]:
        """
        List files with optional filtering and pagination
        
        Args:
            file_type: Filter by file type (pdf, jpg, etc.)
            search: Search in original filename
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            (list of file dicts, total count)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build query
        where_clauses = []
        params = []
        
        if file_type:
            where_clauses.append("file_type = ?")
            params.append(file_type)
        
        if search:
            where_clauses.append("original_name LIKE ?")
            params.append(f"%{search}%")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as count FROM files WHERE {where_sql}", params)
        total = cursor.fetchone()['count']
        
        # Get files
        cursor.execute(f"""
            SELECT * FROM files
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        files = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return files, total
