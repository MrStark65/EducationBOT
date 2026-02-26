# Implementation Plan: Advanced Scheduler and File Management

## Overview

This implementation extends the Officer Priya CDS System with multi-playlist management, file upload/storage capabilities, and advanced scheduling features. The approach follows an incremental build strategy: database schema → backend APIs → file management → scheduling → Telegram integration → frontend components → analytics.

## Tasks

- [x] 1. Set up database schema and core data models
  - [x] 1.1 Create database migration for new tables
    - Add playlists, files, content_items, schedules, deliveries, user_interactions, file_references tables
    - Create all indexes as specified in design
    - _Requirements: 1.1, 2.5, 5.1, 7.7, 8.2_
  
  - [x] 1.2 Create Pydantic models for all entities
    - Implement PlaylistCreate, PlaylistUpdate, PlaylistResponse models
    - Implement FileUploadResponse, ContentItemCreate, ContentItemResponse models
    - Implement ScheduleCreate, ScheduleResponse, DeliveryResponse models
    - Implement AnalyticsResponse, EngagementResponse models
    - _Requirements: 1.3, 2.5, 4.4, 5.2, 7.7_
  
  - [ ]* 1.3 Write property test for database schema
    - **Property 1: Playlist CRUD Operations**
    - **Validates: Requirements 1.3, 1.4, 1.5, 1.6**

- [x] 2. Implement file management backend
  - [x] 2.1 Create FileManager class with file storage logic
    - Implement save_file method with UUID generation and directory structure
    - Implement get_file_path method for file retrieval
    - Implement delete_file method with reference checking
    - Configure upload directory structure (year/month/file_id.ext)
    - _Requirements: 2.5, 3.7, 9.4_
  
  - [x] 2.2 Implement file validation logic
    - Add file type validation (allowed: pdf, doc, docx, jpg, jpeg, png, zip)
    - Add forbidden extension checking (exe, bat, sh, cmd, app, com, scr)
    - Add file size validation (max 50MB)
    - Add MIME type detection and validation using python-magic
    - _Requirements: 2.3, 2.4, 2.6, 9.1, 9.2, 9.3_
  
  - [ ]* 2.3 Write property tests for file validation
    - **Property 3: File Type Validation**
    - **Property 4: File MIME Type Validation**
    - **Property 5: File Size Limit Enforcement**
    - **Validates: Requirements 2.3, 2.4, 2.6, 2.7, 9.1, 9.2, 9.3**
  
  - [x] 2.4 Create file upload API endpoint
    - Implement POST /api/files/upload with multipart/form-data handling
    - Add error handling for invalid file types, oversized files, MIME mismatches
    - Return FileUploadResponse with file metadata
    - _Requirements: 2.1, 2.2, 2.5, 2.8_
  
  - [ ]* 2.5 Write property test for file upload round trip
    - **Property 6: File Upload Round Trip**
    - **Validates: Requirements 2.5, 3.7**

- [x] 3. Implement file library API endpoints
  - [x] 3.1 Create GET /api/files endpoint
    - Implement pagination with limit and offset
    - Add search by filename functionality
    - Add filtering by file type
    - Return file list with metadata
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 3.2 Create GET /api/files/{file_id} endpoint
    - Return file metadata and reference count
    - _Requirements: 3.4_
  
  - [x] 3.3 Create GET /api/files/{file_id}/download endpoint
    - Validate admin authentication
    - Return file binary with appropriate Content-Type header
    - _Requirements: 3.7, 9.6_
  
  - [x] 3.4 Create DELETE /api/files/{file_id} endpoint
    - Check file references in playlists
    - Return error with referencing playlists if file is in use
    - Delete file from filesystem and database if no references
    - _Requirements: 3.5, 3.6_
  
  - [ ]* 3.5 Write property tests for file library operations
    - **Property 7: File Library Completeness**
    - **Property 8: File Deletion Protection**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6**

- [x] 4. Implement playlist management API endpoints
  - [x] 4.1 Create GET /api/playlists endpoint
    - Return list of all playlists with content counts
    - _Requirements: 1.1_
  
  - [x] 4.2 Create POST /api/playlists endpoint
    - Validate unique playlist name
    - Create playlist and return PlaylistResponse
    - _Requirements: 1.2, 1.3_
  
  - [x] 4.3 Create GET /api/playlists/{playlist_id} endpoint
    - Return playlist details with all content items
    - _Requirements: 1.4_
  
  - [x] 4.4 Create PUT /api/playlists/{playlist_id} endpoint
    - Update playlist name and description
    - _Requirements: 1.5_
  
  - [x] 4.5 Create DELETE /api/playlists/{playlist_id} endpoint
    - Check for active schedules
    - Return error if playlist has schedules
    - Delete playlist if no schedules exist
    - _Requirements: 1.6, 1.7_
  
  - [ ]* 4.6 Write property tests for playlist operations
    - **Property 1: Playlist CRUD Operations**
    - **Property 2: Playlist Deletion Protection**
    - **Validates: Requirements 1.3, 1.4, 1.5, 1.6, 1.7**

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement content item management API endpoints
  - [x] 6.1 Create POST /api/playlists/{playlist_id}/content endpoint
    - Validate content_type (video or file)
    - Validate video_url format if type is video
    - Validate file_id exists if type is file
    - Create content item with position
    - Create file_reference entry if type is file
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 6.2 Create PUT /api/playlists/{playlist_id}/content/{content_id} endpoint
    - Update caption and position
    - _Requirements: 4.5_
  
  - [x] 6.3 Create DELETE /api/playlists/{playlist_id}/content/{content_id} endpoint
    - Remove content item from playlist
    - Remove file_reference entry
    - Keep underlying file in library
    - _Requirements: 4.7, 4.8_
  
  - [x] 6.4 Create POST /api/playlists/{playlist_id}/content/reorder endpoint
    - Update positions for all content items based on new order
    - _Requirements: 4.6_
  
  - [ ]* 6.5 Write property tests for content item operations
    - **Property 9: Content Item Association**
    - **Property 10: Content Item Caption Persistence**
    - **Property 11: Content Item Ordering**
    - **Property 12: Content Item Removal Preserves Files**
    - **Property 13: URL Validation**
    - **Validates: Requirements 4.3, 4.4, 4.5, 4.6, 4.7, 4.8**

- [x] 7. Implement schedule management API endpoints
  - [x] 7.1 Create schedule calculation utility functions
    - Implement calculate_next_execution function for daily, weekdays, custom frequencies
    - Implement timezone conversion logic
    - _Requirements: 5.8, 6.7_
  
  - [x] 7.2 Create GET /api/schedules endpoint
    - Return list of schedules with status and next execution times
    - Support filtering by status and playlist_id
    - _Requirements: 5.8, 6.1_
  
  - [x] 7.3 Create POST /api/schedules endpoint
    - Validate start_date not in past
    - Validate end_date after start_date
    - Validate playlist_id exists
    - Calculate next_execution timestamp
    - Create schedule with status 'upcoming'
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [x] 7.4 Create GET /api/schedules/{schedule_id} endpoint
    - Return full schedule details including playlist name
    - _Requirements: 6.1_
  
  - [x] 7.5 Create PUT /api/schedules/{schedule_id} endpoint
    - Validate schedule is not active with last_execution
    - Update schedule parameters
    - Recalculate next_execution
    - _Requirements: 6.3, 6.4_
  
  - [x] 7.6 Create PATCH /api/schedules/{schedule_id}/status endpoint
    - Update status between active and paused
    - _Requirements: 6.2_
  
  - [x] 7.7 Create DELETE /api/schedules/{schedule_id} endpoint
    - Delete schedule (with confirmation for active schedules in UI)
    - _Requirements: 6.5_
  
  - [x] 7.8 Create GET /api/schedules/timeline endpoint
    - Return all scheduled deliveries in date range
    - _Requirements: 10.4_
  
  - [ ]* 7.9 Write property tests for schedule operations
    - **Property 14: Multiple Schedule Creation**
    - **Property 15: Schedule Date Validation**
    - **Property 16: Schedule Execution Time Calculation**
    - **Property 17: Schedule Status Transitions**
    - **Property 18: Schedule Edit Protection**
    - **Property 19: Schedule Deletion by Status**
    - **Property 30: Schedule Conflict Detection**
    - **Property 31: Timeline Completeness**
    - **Validates: Requirements 5.1, 5.6, 5.7, 5.8, 6.2, 6.3, 6.4, 6.5, 6.7, 10.1, 10.4**

- [x] 8. Implement scheduler execution logic
  - [x] 8.1 Create schedule executor service
    - Implement job that runs every minute to check for due schedules
    - Query schedules where next_execution <= current time and status = 'active'
    - For each due schedule, retrieve playlist content items
    - Handle sequential vs all_at_once delivery modes
    - Update current_position for sequential mode
    - Calculate and update next_execution timestamp
    - _Requirements: 5.4, 7.1_
  
  - [x] 8.2 Integrate scheduler with APScheduler
    - Add schedule executor job to APScheduler
    - Configure job to run every minute
    - _Requirements: 5.1_
  
  - [ ]* 8.3 Write unit tests for scheduler execution
    - Test sequential delivery mode progression
    - Test all_at_once delivery mode
    - Test next_execution calculation for different frequencies
    - _Requirements: 5.4_

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Telegram bot file delivery
  - [x] 10.1 Extend Telegram bot to handle file content items
    - Implement send_content_item function that handles both video and file types
    - For file type 'jpg', 'jpeg', 'png': use bot.send_photo
    - For file type 'pdf', 'doc', 'docx', 'zip': use bot.send_document
    - Include caption in all messages
    - Add inline keyboard with "Completed" and "Need Help" buttons
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.4, 8.5_
  
  - [x] 10.2 Implement delivery recording
    - Create delivery record with status 'sent' on successful send
    - Create delivery record with status 'failed' on error
    - Record error message and retry count
    - _Requirements: 7.7_
  
  - [x] 10.3 Implement retry logic for failed deliveries
    - Retry up to 3 times with exponential backoff (1s, 2s, 4s)
    - Log each retry attempt
    - Mark as 'failed' after 3 failed attempts
    - Continue with next user after failure
    - _Requirements: 7.5, 7.6_
  
  - [x] 10.4 Implement callback handlers for user interactions
    - Handle "Completed" button callback
    - Handle "Need Help" button callback
    - Record interactions in user_interactions table
    - Update message to remove buttons after interaction
    - _Requirements: 8.2, 8.3_
  
  - [ ]* 10.5 Write property tests for delivery operations
    - **Property 21: File Retrieval for Delivery**
    - **Property 22: File Type Delivery Mapping**
    - **Property 23: Delivery Retry Logic**
    - **Property 24: Delivery Recording**
    - **Property 25: User Interaction Recording**
    - **Property 26: Caption Inclusion in Delivery**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 8.2, 8.3, 8.5**

- [x] 11. Implement analytics and delivery history API endpoints
  - [x] 11.1 Create GET /api/analytics/deliveries endpoint
    - Calculate total deliveries, successful, failed counts
    - Calculate success rate
    - Group deliveries by date
    - Support filtering by date range, playlist_id, schedule_id
    - _Requirements: 6.8, 12.5_
  
  - [x] 11.2 Create GET /api/analytics/engagement endpoint
    - Calculate total sent, completed count, completion rate
    - Count help requests
    - Group engagement metrics by content item
    - _Requirements: 12.2, 12.3_
  
  - [x] 11.3 Create GET /api/deliveries/history endpoint
    - Return paginated delivery history
    - Support filtering by chat_id, schedule_id, status
    - Include interaction data for each delivery
    - _Requirements: 12.1, 12.4_
  
  - [x] 11.4 Create POST /api/deliveries/export endpoint
    - Generate CSV export of delivery history
    - Support date range filtering
    - Return file download
    - _Requirements: 12.6_
  
  - [ ]* 11.5 Write property tests for analytics operations
    - **Property 20: Delivery Statistics Accuracy**
    - **Property 34: Delivery History Completeness**
    - **Property 35: Completion Rate Calculation**
    - **Property 36: Help Request Count Accuracy**
    - **Property 37: Delivery History Export**
    - **Validates: Requirements 6.8, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6**

- [x] 12. Implement bulk operations API endpoints
  - [x] 12.1 Create POST /api/playlists/{playlist_id}/duplicate endpoint
    - Duplicate playlist with all content items
    - Generate new unique name
    - _Requirements: 11.3_
  
  - [x] 12.2 Create POST /api/playlists/export endpoint
    - Export playlist data as JSON
    - Include all content items and metadata
    - _Requirements: 11.4_
  
  - [x] 12.3 Create POST /api/playlists/import endpoint
    - Import playlist from JSON
    - Validate JSON structure
    - Create playlist and content items
    - _Requirements: 11.5_
  
  - [ ]* 12.4 Write property tests for bulk operations
    - **Property 32: Playlist Duplication**
    - **Property 33: Playlist Export/Import Round Trip**
    - **Validates: Requirements 11.3, 11.4, 11.5**

- [x] 13. Implement security and logging
  - [x] 13.1 Add authentication middleware for file operations
    - Validate admin session for file upload/download
    - Return 401 for unauthenticated requests
    - _Requirements: 9.6_
  
  - [x] 13.2 Implement file operation logging
    - Log all file uploads with timestamp and user identifier
    - Log all file downloads with timestamp and user identifier
    - Store logs in error_logs table
    - _Requirements: 9.7_
  
  - [ ]* 13.3 Write property tests for security features
    - **Property 27: Unique File Identifiers**
    - **Property 28: File Access Authentication**
    - **Property 29: File Operation Logging**
    - **Validates: Requirements 9.4, 9.6, 9.7**

- [x] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Create frontend playlist management components
  - [x] 15.1 Create PlaylistManager component
    - Display list of playlists in card view
    - Show playlist name, description, content count
    - Add "Create Playlist" button
    - Add edit and delete actions for each playlist
    - _Requirements: 1.1, 1.2_
  
  - [ ] 15.2 Create PlaylistDetail component
    - Display all content items in playlist
    - Show content type, caption, position
    - Add "Add Content" button
    - Implement drag-and-drop reordering
    - Add remove content item action
    - _Requirements: 1.4, 4.6, 4.7_
  
  - [ ] 15.3 Create playlist form modal
    - Input fields for name and description
    - Validation for required fields
    - Submit to POST /api/playlists
    - Display success/error messages
    - _Requirements: 1.2, 1.3, 1.5_

- [ ] 16. Create frontend file management components
  - [x] 16.1 Create FileUploader component
    - Drag-and-drop upload zone
    - File type and size validation on client side
    - Upload progress indicator
    - Multiple file support
    - Preview before upload
    - _Requirements: 2.1, 2.2_
  
  - [x] 16.2 Create FileLibrary component
    - Grid view of uploaded files
    - Display thumbnails, names, types, sizes, upload dates
    - Search by filename
    - Filter by file type
    - File preview modal
    - Download and delete actions
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.7_
  
  - [ ] 16.3 Create ContentItemModal component
    - Options to add video URL or select file from library
    - URL validation for video type
    - File library browser within modal
    - Caption input field
    - Submit to POST /api/playlists/{playlist_id}/content
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 17. Create frontend schedule management components
  - [x] 17.1 Create ScheduleManager component
    - Dashboard view of all schedules
    - Display schedule name, playlist, status, next execution
    - Status indicators (active, paused, upcoming, completed)
    - Quick actions (pause/resume/delete)
    - "Create Schedule" button
    - _Requirements: 5.8, 6.1, 6.2, 6.5_
  
  - [ ] 17.2 Create ScheduleForm component
    - Multi-step wizard for schedule creation
    - Step 1: Name and playlist selection
    - Step 2: Start date, end date, delivery time
    - Step 3: Frequency (daily, weekdays, custom days)
    - Step 4: Delivery mode (sequential, all_at_once)
    - Step 5: Review and confirm
    - Validation at each step
    - Submit to POST /api/schedules
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [ ] 17.3 Create ScheduleTimeline component
    - Calendar view of scheduled deliveries
    - Display all schedules in date range
    - Highlight conflicts (multiple schedules at same time)
    - Filter by playlist
    - Click to view schedule details
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 18. Create frontend analytics components
  - [ ] 18.1 Create AnalyticsDashboard component
    - Summary cards (total deliveries, success rate, engagement)
    - Charts for deliveries over time
    - Charts for completion rates
    - Display top performing content
    - Display recent help requests
    - _Requirements: 6.8, 12.5_
  
  - [ ] 18.2 Create DeliveryHistory component
    - Paginated table of deliveries
    - Display schedule name, content caption, chat_id, status, timestamp
    - Filters for date range, status, schedule
    - Export button
    - Click to view delivery details
    - _Requirements: 12.1, 12.4, 12.6_

- [x] 19. Update App.jsx with navigation and routing
  - [x] 19.1 Add navigation tabs
    - Add tabs for Playlists, Files, Schedules, Analytics
    - Maintain existing functionality for backward compatibility
    - _Requirements: 1.1, 3.1, 6.1, 12.1_
  
  - [x] 19.2 Configure routes for new views
    - Route /playlists to PlaylistManager
    - Route /playlists/:id to PlaylistDetail
    - Route /files to FileLibrary
    - Route /schedules to ScheduleManager
    - Route /schedules/timeline to ScheduleTimeline
    - Route /analytics to AnalyticsDashboard
    - Route /deliveries to DeliveryHistory

- [ ] 20. Final checkpoint - Integration testing
  - [ ] 20.1 Test end-to-end file upload and delivery workflow
    - Upload file → Add to playlist → Schedule delivery → Verify delivery recorded
    - _Requirements: 2.1, 4.4, 5.1, 7.7_
  
  - [ ] 20.2 Test playlist management workflow
    - Create playlist → Add multiple content items → Reorder → Verify order persists
    - _Requirements: 1.3, 4.4, 4.6_
  
  - [ ] 20.3 Test schedule execution workflow
    - Create schedule → Wait for execution → Verify content sent → Record interactions → Check analytics
    - _Requirements: 5.1, 7.1, 8.2, 12.2_
  
  - [ ] 20.4 Test file deletion protection
    - Upload file → Add to multiple playlists → Attempt delete → Verify rejection with references
    - _Requirements: 3.5, 3.6_

- [ ] 21. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- All backend code should be written in Python using FastAPI framework
- All frontend code should be written in JavaScript/React
- Database operations use SQLite with the existing database.py pattern
