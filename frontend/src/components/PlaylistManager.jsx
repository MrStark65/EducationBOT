import { useState, useEffect } from 'react';
import './PlaylistManager.css';

function PlaylistManager({ chatId }) {
  const [currentPlaylists, setCurrentPlaylists] = useState(null);
  const [playlistSchedules, setPlaylistSchedules] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddSubjectModal, setShowAddSubjectModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [scheduleConfig, setScheduleConfig] = useState({
    startDate: '',
    frequency: 'daily',
    selectedDays: [1, 2, 3, 4, 5, 6, 0] // All days selected by default (Mon-Sun)
  });
  const [newSubjectName, setNewSubjectName] = useState('');
  const [newSubjectUrl, setNewSubjectUrl] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchCurrentPlaylists();
    fetchPlaylistSchedules();
  }, []);

  const fetchCurrentPlaylists = async () => {
    try {
      const response = await fetch(`${API_URL}/api/config/playlists`);
      if (response.ok) {
        const data = await response.json();
        setCurrentPlaylists(data);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load current playlists:', err);
      setLoading(false);
    }
  };

  const fetchPlaylistSchedules = async () => {
    try {
      const response = await fetch(`${API_URL}/api/config/playlist-schedules`);
      if (response.ok) {
        const data = await response.json();
        setPlaylistSchedules(data);
      }
    } catch (err) {
      console.error('Failed to load playlist schedules:', err);
    }
  };

  const handleUpdatePlaylist = async (subject, url) => {
    try {
      const response = await fetch(`${API_URL}/api/config/playlists`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, url })
      });
      
      if (response.ok) {
        setSuccess(`✅ ${subject} updated globally!`);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to update');
        setTimeout(() => setError(''), 3000);
      }
    } catch (err) {
      setError('Failed to update');
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  const handleAddSubject = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/api/config/playlists`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject: newSubjectName, url: newSubjectUrl })
      });
      
      if (response.ok) {
        setShowAddSubjectModal(false);
        setNewSubjectName('');
        setNewSubjectUrl('');
        fetchCurrentPlaylists();
        setSuccess(`✅ ${newSubjectName} added globally!`);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to add subject');
      }
    } catch (err) {
      setError('Failed to add subject');
    }
  };

  const handleDeleteSubject = async (subject) => {
    if (!confirm(`Delete ${subject} globally? This affects all users.`)) return;
    
    try {
      const response = await fetch(`${API_URL}/api/config/playlists/${subject}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchCurrentPlaylists();
        setSuccess(`✅ ${subject} deleted!`);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to delete');
      }
    } catch (err) {
      setError('Failed to delete');
    }
  };

  const handleOpenSchedule = (subject) => {
    setSelectedSubject(subject);
    // Load existing schedule if any
    const existing = playlistSchedules[subject] || {};
    setScheduleConfig({
      startDate: existing.start_date || '',
      frequency: existing.frequency || 'daily',
      selectedDays: existing.selected_days || [1, 2, 3, 4, 5, 6, 0]
    });
    setShowScheduleModal(true);
  };

  const toggleDay = (day) => {
    const days = scheduleConfig.selectedDays;
    if (days.includes(day)) {
      // Remove day if already selected
      setScheduleConfig({
        ...scheduleConfig,
        selectedDays: days.filter(d => d !== day)
      });
    } else {
      // Add day if not selected
      setScheduleConfig({
        ...scheduleConfig,
        selectedDays: [...days, day].sort()
      });
    }
  };

  const handleSaveSchedule = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_URL}/api/config/playlist-schedules`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: selectedSubject,
          start_date: scheduleConfig.startDate,
          frequency: scheduleConfig.frequency,
          selected_days: scheduleConfig.selectedDays
        })
      });
      
      if (response.ok) {
        // Update local state
        setPlaylistSchedules({
          ...playlistSchedules,
          [selectedSubject]: {
            start_date: scheduleConfig.startDate,
            frequency: scheduleConfig.frequency,
            selected_days: scheduleConfig.selectedDays
          }
        });
        
        setShowScheduleModal(false);
        setSuccess(`✅ Global schedule set for ${selectedSubject}!`);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to save schedule');
        setTimeout(() => setError(''), 3000);
      }
    } catch (err) {
      setError('Failed to save schedule');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (loading) return <div className="loading">Loading playlists...</div>;

  const defaultSubjects = ['english', 'history', 'polity', 'geography', 'economics'];

  return (
    <div className="playlist-manager">
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {currentPlaylists && (
        <div className="current-playlists-section">
          <div className="section-header-with-action">
            <div>
              <h3 className="section-title">📖 Global Playlists (All Users)</h3>
              <p className="section-description">
                These playlists apply to ALL users. Paste URL and press Enter to update.
              </p>
            </div>
            <button className="btn-add-subject" onClick={() => setShowAddSubjectModal(true)}>
              + Add Subject
            </button>
          </div>
          <div className="current-playlist-grid">
            {Object.entries(currentPlaylists).map(([subject, url]) => {
              const isDefault = defaultSubjects.includes(subject.toLowerCase());
              return (
                <div key={subject} className="current-playlist-card-simple">
                  <div className="playlist-icon">
                    {subject.toLowerCase() === 'english' ? '🗣️' : 
                     subject.toLowerCase() === 'history' ? '🏛️' : 
                     subject.toLowerCase() === 'polity' ? '⚖️' : 
                     subject.toLowerCase() === 'geography' ? '🌍' : 
                     subject.toLowerCase() === 'economics' ? '💰' : '📚'}
                  </div>
                  <div className="playlist-info-simple">
                    <h4>{subject.charAt(0).toUpperCase() + subject.slice(1)}</h4>
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => {
                        setCurrentPlaylists({...currentPlaylists, [subject]: e.target.value});
                      }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleUpdatePlaylist(subject, e.target.value);
                        }
                      }}
                      onBlur={(e) => {
                        if (e.target.value !== url) {
                          handleUpdatePlaylist(subject, e.target.value);
                        }
                      }}
                      placeholder="Paste URL and press Enter"
                      className="playlist-url-input"
                    />
                    {playlistSchedules[subject] && (
                      <div className="schedule-badge">
                        📅 {playlistSchedules[subject].frequency === 'daily' ? 'Daily' : 'Alternate'} from {playlistSchedules[subject].start_date}
                        <br />
                        <small>
                          {playlistSchedules[subject].selected_days?.length === 7 ? 'All days' : 
                            playlistSchedules[subject].selected_days?.map(d => ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d]).join(', ')}
                        </small>
                      </div>
                    )}
                  </div>
                  <div className="playlist-actions-group">
                    <button 
                      className="btn-schedule-playlist"
                      onClick={() => handleOpenSchedule(subject)}
                      title="Set Schedule"
                    >
                      📅
                    </button>
                    {!isDefault && (
                      <button 
                        className="btn-delete-subject"
                        onClick={() => handleDeleteSubject(subject)}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    

      {/* Add Subject Modal */}
      {showAddSubjectModal && (
        <div className="modal-overlay" onClick={() => setShowAddSubjectModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>➕ Add New Subject</h3>
            <form onSubmit={handleAddSubject}>
              <div className="form-group">
                <label>Subject Name *</label>
                <input
                  type="text"
                  value={newSubjectName}
                  onChange={(e) => setNewSubjectName(e.target.value)}
                  required
                  placeholder="e.g., Mathematics"
                />
              </div>
              <div className="form-group">
                <label>YouTube Playlist URL *</label>
                <input
                  type="url"
                  value={newSubjectUrl}
                  onChange={(e) => setNewSubjectUrl(e.target.value)}
                  required
                  placeholder="https://www.youtube.com/playlist?list=..."
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => {
                  setShowAddSubjectModal(false);
                  setNewSubjectName('');
                  setNewSubjectUrl('');
                }}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Add Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="modal-overlay" onClick={() => setShowScheduleModal(false)}>
          <div className="modal modal-schedule" onClick={(e) => e.stopPropagation()}>
            <h3>📅 Set Schedule for {selectedSubject.charAt(0).toUpperCase() + selectedSubject.slice(1)}</h3>
            <form onSubmit={handleSaveSchedule}>
              <div className="form-group">
                <label>Start Date *</label>
                <input
                  type="date"
                  value={scheduleConfig.startDate}
                  onChange={(e) => setScheduleConfig({...scheduleConfig, startDate: e.target.value})}
                  required
                  min={new Date().toISOString().split('T')[0]}
                />
                <small>When to start sending videos from this playlist</small>
              </div>

              <div className="form-group">
                <label>Select Days *</label>
                <div className="days-selector">
                  {[
                    { day: 1, label: 'Mon', full: 'Monday' },
                    { day: 2, label: 'Tue', full: 'Tuesday' },
                    { day: 3, label: 'Wed', full: 'Wednesday' },
                    { day: 4, label: 'Thu', full: 'Thursday' },
                    { day: 5, label: 'Fri', full: 'Friday' },
                    { day: 6, label: 'Sat', full: 'Saturday' },
                    { day: 0, label: 'Sun', full: 'Sunday' }
                  ].map(({ day, label, full }) => (
                    <button
                      key={day}
                      type="button"
                      className={`day-button ${scheduleConfig.selectedDays.includes(day) ? 'selected' : ''}`}
                      onClick={() => toggleDay(day)}
                      title={full}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <small>Click days to select/deselect. Videos will only be sent on selected days.</small>
              </div>

              <div className="form-group">
                <label>Frequency *</label>
                <select
                  value={scheduleConfig.frequency}
                  onChange={(e) => setScheduleConfig({...scheduleConfig, frequency: e.target.value})}
                  required
                >
                  <option value="daily">Daily (on selected days)</option>
                  <option value="alternate">Alternate (every other selected day)</option>
                </select>
                <small>How often to send videos on the selected days</small>
              </div>

              <div className="schedule-info-box">
                <p><strong>How it works:</strong></p>
                <ul>
                  <li>Videos will be sent at the time set in "Daily Schedule"</li>
                  <li>Starting from {scheduleConfig.startDate || 'selected date'}</li>
                  <li>Only on: {scheduleConfig.selectedDays.length === 7 ? 'All days' : 
                    scheduleConfig.selectedDays.map(d => ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d]).join(', ')}</li>
                  <li>{scheduleConfig.frequency === 'daily' ? 'One video on each selected day' : 'One video every 2 selected days'}</li>
                  <li>If previous day marked DONE → next video</li>
                  <li>If previous day NOT DONE → resend same video</li>
                </ul>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowScheduleModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default PlaylistManager;
