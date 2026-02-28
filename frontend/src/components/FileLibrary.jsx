import { useState, useEffect } from 'react';
import './FileLibrary.css';

function FileLibrary({ chatId, authToken }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendingFileId, setSendingFileId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('09:00');
  const [scheduledFiles, setScheduledFiles] = useState([]);
  const [showScheduledFiles, setShowScheduledFiles] = useState(false);

  const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    if (authToken) {
      fetchFiles();
      fetchScheduledFiles();
    }
  }, [searchTerm, filterType, authToken]);

  const fetchScheduledFiles = async () => {
    if (!authToken) return;
    
    try {
      const response = await fetch(`${API_URL}/api/scheduled-files`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setScheduledFiles(data.schedules || []);
      }
    } catch (err) {
      console.error('Failed to fetch scheduled files:', err);
    }
  };

  const fetchFiles = async () => {
    if (!authToken) {
      setLoading(false);
      return;
    }
    
    try {
      let url = `${API_URL}/api/files?limit=100`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
      if (filterType !== 'all') url += `&type=${filterType}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.status === 401) {
        // Token expired or invalid - redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expires');
        window.location.reload();
        return;
      }

      if (!response.ok) {
        throw new Error(`Failed to fetch files: ${response.status}`);
      }

      const data = await response.json();
      setFiles(data.files || []);
      setLoading(false);
    } catch (err) {
      setError('Failed to load files: ' + err.message);
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      alert('File size must be less than 50MB');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/files/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        body: formData
      });

      if (response.status === 401) {
        // Token expired or invalid - redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expires');
        window.location.reload();
        return;
      }

      if (response.ok) {
        setSuccess('File uploaded successfully!');
        fetchFiles();
        e.target.value = '';
      } else {
        const data = await response.json();
        setError(data.detail || 'Upload failed');
      }
    } catch (err) {
      setError('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      const response = await fetch(`${API_URL}/api/files/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.status === 401) {
        // Token expired or invalid - redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expires');
        window.location.reload();
        return;
      }

      if (response.ok) {
        setSuccess('File deleted successfully');
        fetchFiles();
      } else {
        const data = await response.json();
        setError(`Failed to delete file: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setError(`Failed to delete file: ${err.message}`);
    }
  };

  const handleDownloadFile = (fileId, fileName) => {
    const url = `${API_URL}/api/files/${fileId}/download`;
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
  };

  const handleSendFile = async (file) => {
    setSending(true);
    setSendingFileId(file.file_id);
    setError('');
    setSuccess('');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch(`${API_URL}/api/admin/send-file`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ file_id: file.file_id }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        setSuccess(`File sent to ${data.sent_count} user(s)`);
      } else {
        setError('Failed to send file');
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timeout - file may still be sending');
      } else {
        setError('Failed to send file');
      }
    } finally {
      setSending(false);
      setSendingFileId(null);
    }
  };

  const openScheduleModal = (file) => {
    setSelectedFile(file);
    setShowScheduleModal(true);
  };

  const handleScheduleFile = async () => {
    if (!scheduleDate || !scheduleTime) {
      setError('Please select both date and time');
      return;
    }

    try {
      const scheduledDateTime = `${scheduleDate} ${scheduleTime}`;
      
      const response = await fetch(`${API_URL}/api/admin/schedule-file`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          file_id: selectedFile.file_id,
          scheduled_time: scheduledDateTime
        })
      });

      if (response.ok) {
        setSuccess(`File scheduled for ${scheduleDate} at ${scheduleTime}`);
        setShowScheduleModal(false);
        setSelectedFile(null);
        setScheduleDate('');
        setScheduleTime('09:00');
        fetchScheduledFiles(); // Refresh scheduled files list
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to schedule file');
      }
    } catch (err) {
      setError('Failed to schedule file');
    }
  };

  if (loading) {
    return <div className="loading">Loading files...</div>;
  }

  if (!authToken) {
    return (
      <div className="file-library">
        <div className="alert alert-error">
          Authentication required. Please log out and log back in.
        </div>
      </div>
    );
  }

  return (
    <div className="file-library">
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Scheduled Files Section */}
      <div className="scheduled-files-section">
        <button 
          className="toggle-scheduled-btn"
          onClick={() => setShowScheduledFiles(!showScheduledFiles)}
        >
          📅 Scheduled Files ({scheduledFiles.filter(f => f.status === 'pending').length})
          {showScheduledFiles ? ' ▼' : ' ▶'}
        </button>
        
        {showScheduledFiles && (
          <div className="scheduled-files-list">
            {scheduledFiles.length === 0 ? (
              <p className="empty-hint">No scheduled files</p>
            ) : (
              <table className="scheduled-table">
                <thead>
                  <tr>
                    <th>File Name</th>
                    <th>Scheduled Time</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {scheduledFiles.map((schedule) => (
                    <tr key={schedule.id} className={`status-${schedule.status}`}>
                      <td>{schedule.file_name}</td>
                      <td>{schedule.scheduled_time}</td>
                      <td>
                        <span className={`status-badge status-${schedule.status}`}>
                          {schedule.status === 'pending' && '⏳ Pending'}
                          {schedule.status === 'sent' && '✅ Sent'}
                          {schedule.status === 'failed' && '❌ Failed'}
                        </span>
                      </td>
                      <td>{new Date(schedule.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      <div className="file-controls">
        <div className="search-filter">
          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="pdf">PDF</option>
            <option value="video">Video</option>
            <option value="image">Image</option>
            <option value="audio">Audio</option>
          </select>
        </div>

        <label className="upload-button">
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          {uploading ? 'Uploading...' : '📤 Upload File'}
        </label>
      </div>

      {files.length === 0 ? (
        <div className="empty-state">
          <p>📁 No files uploaded yet</p>
          <p className="empty-hint">Upload your first file to get started</p>
        </div>
      ) : (
        <div className="files-grid">
          {files.map((file) => (
            <div key={file.file_id} className="file-card">
              <div className="file-icon">
                {file.file_type === 'pdf' && '📄'}
                {file.file_type === 'video' && '🎥'}
                {file.file_type === 'image' && '🖼️'}
                {file.file_type === 'audio' && '🎵'}
                {!['pdf', 'video', 'image', 'audio'].includes(file.file_type) && '📎'}
              </div>
              <div className="file-info">
                <h4 className="file-name">{file.original_name}</h4>
                <p className="file-meta">
                  {(file.file_size / 1024 / 1024).toFixed(2)} MB • {file.file_type}
                </p>
                <p className="file-date">
                  {new Date(file.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="file-actions">
                <button
                  onClick={() => handleDownloadFile(file.file_id, file.original_name)}
                  className="btn-download"
                  title="Download"
                >
                  ⬇️
                </button>
                <button
                  onClick={() => handleSendFile(file)}
                  className="btn-send"
                  disabled={sending && sendingFileId === file.file_id}
                  title="Send to all users now"
                >
                  {sending && sendingFileId === file.file_id ? '⏳' : '📤'}
                </button>
                <button
                  onClick={() => openScheduleModal(file)}
                  className="btn-schedule"
                  title="Schedule for later"
                >
                  📅
                </button>
                <button
                  onClick={() => handleDeleteFile(file.file_id)}
                  className="btn-delete"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showScheduleModal && (
        <div className="modal-overlay" onClick={() => setShowScheduleModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📅 Schedule File Delivery</h3>
              <button className="modal-close" onClick={() => setShowScheduleModal(false)}>×</button>
            </div>
            
            {selectedFile && (
              <div className="modal-file-info">
                <p><strong>File:</strong> {selectedFile.original_name}</p>
                <p><strong>Size:</strong> {(selectedFile.file_size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            )}
            
            <div className="modal-body">
              <div className="form-group">
                <label>📅 Select Date:</label>
                <input
                  type="date"
                  value={scheduleDate}
                  onChange={(e) => setScheduleDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>⏰ Select Time:</label>
                <input
                  type="time"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  required
                />
              </div>
              
              <div className="schedule-preview">
                {scheduleDate && scheduleTime && (
                  <p className="preview-text">
                    📤 File will be sent on <strong>{new Date(scheduleDate).toLocaleDateString()}</strong> at <strong>{scheduleTime}</strong>
                  </p>
                )}
              </div>
            </div>
            
            <div className="modal-actions">
              <button onClick={() => setShowScheduleModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button 
                onClick={handleScheduleFile} 
                className="btn-primary"
                disabled={!scheduleDate || !scheduleTime}
              >
                📅 Schedule Delivery
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FileLibrary;
