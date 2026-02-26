# Requirements Document

## Introduction

This document specifies requirements for enhancing the Officer Priya CDS System with advanced scheduler capabilities and comprehensive file management features. The system currently sends daily video links for CDS exam preparation through a Telegram bot. This enhancement will enable administrators to manage multiple playlists, schedule content with advanced options, and send various file types (PDFs, documents, images) to users through the admin portal.

## Glossary

- **Admin_Portal**: The React-based web interface used by administrators to manage the system
- **Scheduler**: The backend component that sends scheduled messages to Telegram users
- **Playlist**: A collection of content items (videos, files, or messages) to be sent to users
- **Content_Item**: A single piece of content (video link, PDF, document, or other file) within a playlist
- **File_Manager**: The backend component that handles file uploads, storage, and retrieval
- **Telegram_Bot**: The python-telegram-bot service that delivers content to users
- **User**: A student receiving CDS exam preparation content via Telegram
- **Administrator**: A person managing content and schedules through the Admin_Portal

## Requirements

### Requirement 1: Multiple Playlist Management

**User Story:** As an Administrator, I want to create and manage multiple playlists through the Admin_Portal, so that I can organize different types of content for different subjects or user groups.

#### Acceptance Criteria

1. THE Admin_Portal SHALL display a list of all existing playlists with their names and content counts
2. WHEN an Administrator clicks "Create Playlist", THE Admin_Portal SHALL display a form to enter playlist name and description
3. WHEN an Administrator submits a valid playlist form, THE Admin_Portal SHALL create the playlist and display a success confirmation
4. WHEN an Administrator selects a playlist, THE Admin_Portal SHALL display all Content_Items in that playlist
5. THE Admin_Portal SHALL allow Administrators to edit playlist names and descriptions
6. THE Admin_Portal SHALL allow Administrators to delete playlists that contain no scheduled items
7. WHEN an Administrator attempts to delete a playlist with scheduled items, THE Admin_Portal SHALL display a warning and require confirmation

### Requirement 2: File Upload and Storage

**User Story:** As an Administrator, I want to upload PDF files and other document types through the Admin_Portal, so that I can share study materials with users.

#### Acceptance Criteria

1. THE Admin_Portal SHALL provide a file upload interface that accepts PDF, DOC, DOCX, JPG, PNG, and ZIP file formats
2. WHEN an Administrator selects a file for upload, THE Admin_Portal SHALL display the file name, size, and type before upload
3. WHEN an Administrator uploads a file, THE File_Manager SHALL validate the file type against allowed formats
4. IF an unsupported file type is uploaded, THEN THE File_Manager SHALL reject the upload and return an error message
5. WHEN a valid file is uploaded, THE File_Manager SHALL store the file with a unique identifier and return the file metadata
6. THE File_Manager SHALL enforce a maximum file size limit of 50MB per file
7. IF a file exceeds the size limit, THEN THE File_Manager SHALL reject the upload and return an error message
8. WHEN a file upload completes successfully, THE Admin_Portal SHALL display the uploaded file in the file library

### Requirement 3: File Library Management

**User Story:** As an Administrator, I want to view and manage all uploaded files in a centralized library, so that I can reuse files across multiple playlists and schedules.

#### Acceptance Criteria

1. THE Admin_Portal SHALL display a file library showing all uploaded files with thumbnails, names, types, sizes, and upload dates
2. THE Admin_Portal SHALL allow Administrators to search files by name or type
3. THE Admin_Portal SHALL allow Administrators to filter files by type (PDF, image, document, etc.)
4. WHEN an Administrator selects a file, THE Admin_Portal SHALL display file details and a preview where applicable
5. THE Admin_Portal SHALL allow Administrators to delete files that are not referenced in any playlist
6. WHEN an Administrator attempts to delete a file used in a playlist, THE Admin_Portal SHALL display which playlists reference the file and require confirmation
7. THE Admin_Portal SHALL allow Administrators to download any uploaded file

### Requirement 4: Add Content Items to Playlists

**User Story:** As an Administrator, I want to add video links and uploaded files to playlists, so that I can organize content for scheduled delivery.

#### Acceptance Criteria

1. WHEN an Administrator views a playlist, THE Admin_Portal SHALL display an "Add Content" button
2. WHEN an Administrator clicks "Add Content", THE Admin_Portal SHALL display options to add a video link or select a file from the library
3. WHEN an Administrator adds a video link, THE Admin_Portal SHALL validate the URL format
4. WHEN an Administrator selects a file from the library, THE Admin_Portal SHALL add the file reference to the playlist
5. THE Admin_Portal SHALL allow Administrators to specify a caption or description for each Content_Item
6. THE Admin_Portal SHALL allow Administrators to reorder Content_Items within a playlist using drag-and-drop
7. THE Admin_Portal SHALL allow Administrators to remove Content_Items from a playlist
8. WHEN a Content_Item is removed from a playlist, THE File_Manager SHALL retain the underlying file in the library

### Requirement 5: Advanced Schedule Configuration

**User Story:** As an Administrator, I want to configure detailed scheduling options for playlists, so that I can control when and how content is delivered to users.

#### Acceptance Criteria

1. THE Admin_Portal SHALL allow Administrators to create multiple schedules for different playlists
2. WHEN creating a schedule, THE Admin_Portal SHALL allow Administrators to select a playlist, start date, end date, and delivery time
3. THE Admin_Portal SHALL allow Administrators to specify delivery frequency (daily, weekdays only, specific days of week, or custom interval)
4. THE Admin_Portal SHALL allow Administrators to configure whether to send all Content_Items at once or one per scheduled time
5. THE Admin_Portal SHALL allow Administrators to specify a timezone for schedule execution
6. WHEN an Administrator saves a schedule, THE Scheduler SHALL validate that the start date is not in the past
7. IF schedule dates are invalid, THEN THE Admin_Portal SHALL display validation errors and prevent saving
8. THE Admin_Portal SHALL display all active and upcoming schedules with their next execution time

### Requirement 6: Schedule Management and Monitoring

**User Story:** As an Administrator, I want to view and manage all schedules, so that I can monitor content delivery and make adjustments as needed.

#### Acceptance Criteria

1. THE Admin_Portal SHALL display a schedule dashboard showing all schedules with their status (active, paused, completed, upcoming)
2. THE Admin_Portal SHALL allow Administrators to pause and resume active schedules
3. THE Admin_Portal SHALL allow Administrators to edit schedule parameters before the schedule starts
4. THE Admin_Portal SHALL prevent editing schedules that are currently in progress
5. THE Admin_Portal SHALL allow Administrators to delete schedules that have not started
6. WHEN an Administrator deletes an active schedule, THE Admin_Portal SHALL require confirmation
7. THE Admin_Portal SHALL display the last execution time and next execution time for each schedule
8. THE Admin_Portal SHALL display delivery statistics (messages sent, files delivered, errors) for each schedule

### Requirement 7: File Delivery via Telegram

**User Story:** As a User, I want to receive PDF files and other documents through the Telegram_Bot, so that I can access study materials directly in Telegram.

#### Acceptance Criteria

1. WHEN the Scheduler sends a Content_Item containing a file, THE Telegram_Bot SHALL retrieve the file from the File_Manager
2. WHEN sending a PDF file, THE Telegram_Bot SHALL send it as a document with the specified caption
3. WHEN sending an image file, THE Telegram_Bot SHALL send it as a photo with the specified caption
4. WHEN sending other document types, THE Telegram_Bot SHALL send them as documents with the specified caption
5. IF a file fails to send to a User, THEN THE Telegram_Bot SHALL log the error and retry up to 3 times
6. IF a file fails after all retries, THEN THE Telegram_Bot SHALL log the failure and continue with the next User
7. WHEN a file is successfully delivered, THE Telegram_Bot SHALL record the delivery in the database

### Requirement 8: User Interaction with Files

**User Story:** As a User, I want to interact with received files in Telegram, so that I can track my progress and provide feedback.

#### Acceptance Criteria

1. WHEN the Telegram_Bot sends a file, THE Telegram_Bot SHALL include inline buttons for "Completed" and "Need Help"
2. WHEN a User clicks "Completed", THE Telegram_Bot SHALL record the completion status in the database
3. WHEN a User clicks "Need Help", THE Telegram_Bot SHALL record the help request and notify Administrators
4. THE Telegram_Bot SHALL allow Users to download and view files directly in Telegram
5. WHEN a User receives a file, THE Telegram_Bot SHALL include the file caption or description if provided

### Requirement 9: File Type Validation and Security

**User Story:** As an Administrator, I want the system to validate and secure uploaded files, so that malicious files cannot be distributed to users.

#### Acceptance Criteria

1. WHEN a file is uploaded, THE File_Manager SHALL verify the file extension matches the declared file type
2. THE File_Manager SHALL scan file content to verify it matches the declared MIME type
3. THE File_Manager SHALL reject files with executable extensions (exe, bat, sh, cmd, app)
4. THE File_Manager SHALL generate unique file identifiers to prevent filename collisions
5. THE File_Manager SHALL store files in a secure directory inaccessible via direct web URLs
6. WHEN serving files to the Telegram_Bot, THE File_Manager SHALL validate the request originates from an authenticated Administrator session
7. THE File_Manager SHALL log all file upload and download operations with timestamps and user identifiers

### Requirement 10: Schedule Conflict Detection

**User Story:** As an Administrator, I want the system to detect scheduling conflicts, so that I can avoid overwhelming users with too many messages at once.

#### Acceptance Criteria

1. WHEN an Administrator creates a schedule, THE Scheduler SHALL check for other schedules with the same delivery time
2. IF multiple schedules target the same time, THEN THE Admin_Portal SHALL display a warning about potential message clustering
3. THE Admin_Portal SHALL allow Administrators to proceed with conflicting schedules after acknowledging the warning
4. THE Admin_Portal SHALL display a timeline view showing all scheduled deliveries across all playlists
5. THE Admin_Portal SHALL highlight time slots with multiple scheduled deliveries

### Requirement 11: Bulk Operations

**User Story:** As an Administrator, I want to perform bulk operations on playlists and schedules, so that I can efficiently manage large amounts of content.

#### Acceptance Criteria

1. THE Admin_Portal SHALL allow Administrators to select multiple Content_Items within a playlist
2. WHEN multiple Content_Items are selected, THE Admin_Portal SHALL display options to delete, move to another playlist, or reorder them
3. THE Admin_Portal SHALL allow Administrators to duplicate an existing playlist with all its Content_Items
4. THE Admin_Portal SHALL allow Administrators to export playlist data as JSON for backup purposes
5. THE Admin_Portal SHALL allow Administrators to import playlist data from JSON files

### Requirement 12: Delivery History and Analytics

**User Story:** As an Administrator, I want to view delivery history and analytics, so that I can understand content engagement and system performance.

#### Acceptance Criteria

1. THE Admin_Portal SHALL display a delivery history showing all sent messages and files with timestamps
2. THE Admin_Portal SHALL display completion rates for each Content_Item (percentage of users who marked as completed)
3. THE Admin_Portal SHALL display help request counts for each Content_Item
4. THE Admin_Portal SHALL allow Administrators to filter delivery history by date range, playlist, or content type
5. THE Admin_Portal SHALL display aggregate statistics including total deliveries, success rate, and error rate
6. THE Admin_Portal SHALL allow Administrators to export delivery history as CSV files
