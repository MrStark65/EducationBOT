# Requirements Document

## Introduction

The Officer Priya CDS Preparation Automation System is a Telegram-based study management platform designed to automate daily video delivery for Combined Defence Services (CDS) OTA examination preparation. The system follows an officer-style disciplined training approach, delivering structured content across English and General Knowledge subjects (History, Polity, Geography, Economics) while tracking completion, maintaining study streaks, and providing administrative oversight through a web dashboard.

## Glossary

- **System**: The Officer Priya CDS Preparation Automation System
- **Admin_Dashboard**: Web-based React interface for monitoring and managing study progress
- **Telegram_Bot**: Automated bot that delivers daily study content via Telegram
- **Backend_Server**: FastAPI-based automation server handling scheduling and data management
- **Database**: SQLite database storing playlists, progress, and logs
- **Study_Day**: A single day's study session consisting of one English video and one GK video
- **GK_Subject**: General Knowledge subject (History, Polity, Geography, or Economics)
- **Completion_Status**: Status of a study day (DONE, NOT_DONE, or PENDING)
- **Study_Streak**: Consecutive days of completed study sessions
- **Video_Index**: Current position in a subject's playlist
- **GK_Rotation**: Sequential cycling through GK subjects (History → Polity → Geography → Economics)

## Requirements

### Requirement 1: Daily Video Delivery

**User Story:** As Officer Priya, I want to receive daily study videos automatically via Telegram, so that I maintain a consistent study routine without manual effort.

#### Acceptance Criteria

1. THE Telegram_Bot SHALL send exactly one message per day containing study content
2. WHEN a Study_Day begins, THE System SHALL select the next English video sequentially from the English playlist
3. WHEN a Study_Day begins, THE System SHALL select the next GK video based on GK_Rotation order
4. THE Telegram_Bot SHALL format messages as: "Officer Priya – Day X\n[English Video Link]\n[GK Video Link]"
5. THE Telegram_Bot SHALL include interactive buttons labeled "✅ Done" and "❌ Not Done" with each message
6. THE System SHALL increment Video_Index for English after each delivery
7. THE System SHALL increment Video_Index for the current GK_Subject after each delivery
8. THE System SHALL advance GK_Rotation to the next subject after each delivery following the pattern: History → Polity → Geography → Economics → History

### Requirement 2: Completion Tracking

**User Story:** As Officer Priya, I want to mark my daily study completion via button clicks, so that my progress is automatically recorded.

#### Acceptance Criteria

1. WHEN Officer Priya clicks "✅ Done", THE System SHALL update Completion_Status to DONE for that Study_Day
2. WHEN Officer Priya clicks "❌ Not Done", THE System SHALL update Completion_Status to NOT_DONE for that Study_Day
3. WHEN Completion_Status is updated, THE System SHALL record the timestamp in the Database
4. WHEN Completion_Status changes from PENDING to DONE or NOT_DONE, THE System SHALL persist the change immediately
5. THE System SHALL prevent duplicate status updates for the same Study_Day

### Requirement 3: Study Streak Management

**User Story:** As Officer Priya, I want my study streak to be automatically calculated, so that I can track my consistency and stay motivated.

#### Acceptance Criteria

1. WHEN a Study_Day is marked DONE, THE System SHALL increment Study_Streak by one if the previous day was also DONE
2. WHEN a Study_Day is marked NOT_DONE, THE System SHALL reset Study_Streak to zero
3. WHEN a Study_Day is marked DONE after a gap, THE System SHALL set Study_Streak to one
4. THE System SHALL calculate Study_Streak based on consecutive DONE days without gaps
5. THE System SHALL persist Study_Streak value in the Database after each update

### Requirement 4: Progress Visualization

**User Story:** As an administrator, I want to view comprehensive progress metrics on a dashboard, so that I can monitor Officer Priya's study performance.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL display the current Study_Day number
2. THE Admin_Dashboard SHALL calculate and display overall completion percentage as (DONE days / total days) × 100
3. THE Admin_Dashboard SHALL calculate and display weekly completion percentage for the most recent 7 days
4. THE Admin_Dashboard SHALL display the current Study_Streak value
5. THE Admin_Dashboard SHALL refresh metrics automatically when Database changes occur

### Requirement 5: Daily Log Management

**User Story:** As an administrator, I want to view a detailed log of all study days, so that I can review historical progress and identify patterns.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL display a table with columns: Day, Date, English Video #, GK Subject, GK Video #, Status
2. WHEN a new Study_Day is created, THE System SHALL add a new row to the daily log table
3. THE Admin_Dashboard SHALL display log entries in descending order by day number (most recent first)
4. THE Admin_Dashboard SHALL show Completion_Status using visual indicators (DONE, NOT_DONE, PENDING)
5. THE Admin_Dashboard SHALL display the date in a human-readable format (YYYY-MM-DD)

### Requirement 6: Playlist Configuration

**User Story:** As an administrator, I want to modify playlist URLs, so that I can update study content when needed.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide input fields for each subject's playlist URL (English, History, Polity, Geography, Economics)
2. WHEN an administrator updates a playlist URL, THE System SHALL validate the URL format
3. WHEN a valid playlist URL is submitted, THE System SHALL persist the change to the Database
4. WHEN a playlist URL is changed, THE System SHALL reset the corresponding Video_Index to zero
5. THE System SHALL reject invalid YouTube playlist URLs and display an error message

### Requirement 7: Progress Reset Capability

**User Story:** As an administrator, I want to reset all progress data, so that I can restart the study program from the beginning.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide a "Reset Progress" button with confirmation dialog
2. WHEN progress reset is confirmed, THE System SHALL set all Video_Index values to zero
3. WHEN progress reset is confirmed, THE System SHALL set Study_Streak to zero
4. WHEN progress reset is confirmed, THE System SHALL set day count to zero
5. WHEN progress reset is confirmed, THE System SHALL clear all entries from the daily log table
6. WHEN progress reset is confirmed, THE System SHALL set GK_Rotation index to zero (History)

### Requirement 8: Manual Message Trigger

**User Story:** As an administrator, I want to manually trigger the daily message, so that I can send study content outside the automated schedule if needed.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL provide a "Send Now" button
2. WHEN "Send Now" is clicked, THE System SHALL execute the same logic as automated daily delivery
3. WHEN manual send is triggered, THE System SHALL increment the day count
4. WHEN manual send is triggered, THE System SHALL create a new daily log entry
5. THE System SHALL prevent multiple manual sends within the same day

### Requirement 9: Automated Scheduling

**User Story:** As Officer Priya, I want videos delivered automatically at a consistent time each day, so that I maintain a regular study schedule without manual intervention.

#### Acceptance Criteria

1. THE Backend_Server SHALL schedule daily message delivery using GitHub Actions
2. THE System SHALL execute daily delivery at a configured time each day
3. WHEN the scheduled time arrives, THE System SHALL trigger the daily video delivery workflow
4. THE System SHALL log each automated execution with timestamp
5. IF automated delivery fails, THE System SHALL retry up to three times with exponential backoff

### Requirement 10: Data Persistence

**User Story:** As a system administrator, I want all data stored reliably in a database, so that progress is never lost.

#### Acceptance Criteria

1. THE Database SHALL store configuration data including playlist URLs, Video_Index values, GK_Rotation index, day count, and Study_Streak
2. THE Database SHALL store daily log entries with day number, date, English video number, GK subject, GK video number, Completion_Status, and timestamp
3. WHEN any data changes, THE System SHALL persist changes to the Database immediately
4. THE Database SHALL use SQLite format for lightweight storage
5. THE System SHALL create the Database file automatically if it does not exist

### Requirement 11: Telegram Bot Integration

**User Story:** As Officer Priya, I want to interact with the system through Telegram, so that I can access study content and track progress from my mobile device.

#### Acceptance Criteria

1. THE Telegram_Bot SHALL authenticate using a valid Telegram Bot API token
2. THE Telegram_Bot SHALL send messages to a configured chat ID
3. WHEN Officer Priya clicks a button, THE Telegram_Bot SHALL receive the callback via webhook
4. THE Telegram_Bot SHALL process button callbacks and update the Database accordingly
5. THE Telegram_Bot SHALL send confirmation messages after status updates

### Requirement 12: Zero-Cost Architecture

**User Story:** As a system administrator, I want the entire system to run on free infrastructure, so that there are no ongoing operational costs.

#### Acceptance Criteria

1. THE Admin_Dashboard SHALL be hosted on Vercel or Netlify free tier
2. THE Backend_Server SHALL be hosted on Render free tier
3. THE System SHALL use GitHub Actions free tier for scheduling
4. THE System SHALL use SQLite for data storage without requiring paid database services
5. THE System SHALL use Telegram Bot API which is free

### Requirement 13: Real-Time Dashboard Updates

**User Story:** As an administrator, I want the dashboard to update automatically when data changes, so that I always see current information without manual refresh.

#### Acceptance Criteria

1. WHEN the Database is updated, THE Admin_Dashboard SHALL reflect changes within 5 seconds
2. THE Admin_Dashboard SHALL poll the Backend_Server for updates at regular intervals
3. WHEN Completion_Status changes, THE Admin_Dashboard SHALL update the corresponding log entry
4. WHEN Study_Streak changes, THE Admin_Dashboard SHALL update the streak display
5. THE Admin_Dashboard SHALL display a loading indicator during data fetches

### Requirement 14: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error logging, so that I can diagnose and fix issues quickly.

#### Acceptance Criteria

1. WHEN an error occurs in the Backend_Server, THE System SHALL log the error with timestamp, error type, and stack trace
2. WHEN Telegram_Bot message delivery fails, THE System SHALL log the failure reason
3. WHEN Database operations fail, THE System SHALL log the SQL error and affected operation
4. THE System SHALL store logs in a persistent file accessible to administrators
5. THE Admin_Dashboard SHALL display recent errors in a dedicated section

### Requirement 15: Video Link Validation

**User Story:** As Officer Priya, I want to receive valid video links, so that I can access study content without encountering broken links.

#### Acceptance Criteria

1. WHEN selecting a video, THE System SHALL verify the Video_Index is within the playlist bounds
2. WHEN a Video_Index exceeds playlist length, THE System SHALL wrap around to the beginning of that playlist
3. THE System SHALL construct valid YouTube video URLs from playlist data
4. WHEN a playlist URL is invalid, THE System SHALL log an error and skip that subject for the day
5. THE System SHALL validate that video links are accessible before sending to Telegram

### Requirement 16: Configuration State Management

**User Story:** As a system administrator, I want the system to maintain its state across restarts, so that progress continues seamlessly after server downtime.

#### Acceptance Criteria

1. WHEN the Backend_Server starts, THE System SHALL load all configuration from the Database
2. THE System SHALL restore Video_Index values, GK_Rotation index, day count, and Study_Streak from the Database
3. WHEN the Backend_Server restarts, THE System SHALL not duplicate daily messages already sent
4. THE System SHALL maintain state consistency between Backend_Server and Database at all times
5. THE System SHALL handle Database connection failures gracefully with retry logic
