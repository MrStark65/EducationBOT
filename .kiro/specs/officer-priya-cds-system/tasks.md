# Implementation Plan: Officer Priya CDS Preparation Automation System

## Overview

This implementation plan breaks down the Officer Priya CDS system into incremental coding tasks. The system will be built in Python with FastAPI for the backend, React for the frontend, and SQLite for data persistence. Tasks are organized to build core functionality first, then add automation, and finally integrate the admin dashboard.

## Tasks

- [x] 1. Set up project structure and database foundation
  - Create project directory structure: `backend/`, `frontend/`, `database/`, `tests/`
  - Set up Python virtual environment and install dependencies: `fastapi`, `uvicorn`, `python-telegram-bot`, `sqlite3`, `pytest`, `hypothesis`
  - Create SQLite database schema with `config` and `daily_logs` tables
  - Implement database initialization script that creates tables if they don't exist
  - _Requirements: 10.1, 10.2, 10.5_

- [ ]* 1.1 Write unit tests for database initialization
  - Test database file creation
  - Test table schema correctness
  - Test constraint enforcement (unique day_number, status enum)
  - _Requirements: 10.5_

- [x] 2. Implement core data models and database operations
  - [x] 2.1 Create Python dataclasses for `Config` and `DailyLog` models
    - Implement `Config` with all playlist URLs, indices, day count, streak
    - Implement `DailyLog` with day number, date, video numbers, status
    - Add helper methods: `get_current_gk_subject()`, `is_completed()`, `is_pending()`
    - _Requirements: 10.1, 10.2_

  - [x] 2.2 Implement database repository class with CRUD operations
    - `get_config()`: Load configuration from database
    - `update_config()`: Persist configuration changes
    - `insert_log()`: Create new daily log entry
    - `update_log_status()`: Update completion status
    - `get_all_logs()`: Retrieve all logs ordered by day descending
    - `get_recent_logs(limit)`: Get most recent N logs
    - `clear_all_logs()`: Delete all log entries
    - _Requirements: 10.3, 5.2, 5.3_

  - [ ]* 2.3 Write property test for state persistence
    - **Property 12: State Persistence**
    - **Validates: Requirements 10.3**
    - Test that any config update followed by immediate read returns the updated value
    - Test that any log insert followed by immediate read returns the inserted log

  - [ ]* 2.4 Write property test for log entry uniqueness
    - **Property 8: Log Entry Uniqueness**
    - **Validates: Requirements 5.2**
    - Test that inserting duplicate day numbers raises IntegrityError

- [x] 3. Implement video selection and rotation logic
  - [x] 3.1 Create `VideoSelector` class with selection methods
    - `select_next_english(current_index)`: Return next English video number and URL
    - `select_next_gk(rotation_index, subject_indices)`: Return GK subject, video number, URL
    - `advance_rotation(current_index)`: Return next rotation index (0-3)
    - Implement playlist URL parsing to extract video links
    - _Requirements: 1.2, 1.3, 1.8_

  - [ ]* 3.2 Write property test for video index monotonicity
    - **Property 1: Video Index Monotonicity**
    - **Validates: Requirements 1.6**
    - Test that for any starting index, next English video is index + 1

  - [ ]* 3.3 Write property test for GK rotation cycle consistency
    - **Property 2: GK Rotation Cycle Consistency**
    - **Validates: Requirements 1.8**
    - Test that rotation follows History → Polity → Geography → Economics → History pattern

  - [ ]* 3.4 Write property test for video index wrapping
    - **Property 15: Video Index Wrapping**
    - **Validates: Requirements 15.2**
    - Test that when index exceeds playlist length, it wraps to 0

- [x] 4. Implement streak calculation logic
  - [x] 4.1 Create `StreakCalculator` class
    - `calculate_streak(logs)`: Calculate consecutive DONE days from most recent
    - `update_streak_on_completion(current_streak, new_status, previous_status)`: Update streak based on status change
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 4.2 Write property test for streak calculation correctness
    - **Property 5: Streak Calculation Correctness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    - Test that for any sequence of statuses, calculated streak equals consecutive DONE from end

  - [ ]* 4.3 Write unit tests for streak edge cases
    - Test streak with all DONE days
    - Test streak with all NOT_DONE days
    - Test streak with single DONE after NOT_DONE
    - Test streak with empty logs
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 5. Implement completion percentage calculations
  - [x] 5.1 Create `CompletionCalculator` class
    - `calculate_overall(logs)`: Return percentage of DONE days out of total
    - `calculate_weekly(logs)`: Return percentage of DONE days in last 7 days
    - _Requirements: 4.2, 4.3_

  - [ ]* 5.2 Write property test for completion percentage bounds
    - **Property 6: Completion Percentage Bounds**
    - **Validates: Requirements 4.2**
    - Test that for any log sequence, overall completion is between 0 and 100

  - [ ]* 5.3 Write property test for weekly completion calculation
    - **Property 7: Weekly Completion Calculation**
    - **Validates: Requirements 4.3**
    - Test that weekly completion only considers last 7 days and is between 0 and 100

- [x] 6. Implement Telegram Bot integration
  - [x] 6.1 Create `TelegramBot` class with message sending
    - Initialize bot with API token from environment variable
    - `send_daily_message(chat_id, day, english_link, gk_link)`: Send formatted message with buttons
    - Format message as: "Officer Priya – Day X\n📚 English: {link}\n📖 GK ({subject}): {link}"
    - Add inline keyboard with "✅ Done" and "❌ Not Done" buttons
    - _Requirements: 1.1, 1.4, 1.5, 11.1, 11.2_

  - [x] 6.2 Implement webhook callback handler
    - `handle_callback(callback_query)`: Parse callback data and return action
    - Parse JSON callback data: `{"action": "complete", "day": X, "status": "DONE"}`
    - Validate callback data structure
    - _Requirements: 11.3, 11.4_

  - [x] 6.3 Implement confirmation message sending
    - `send_confirmation(chat_id, message)`: Send simple text confirmation
    - _Requirements: 11.5_

  - [ ]* 6.4 Write unit tests for message formatting
    - Test message format matches expected pattern
    - Test buttons are included with correct labels
    - Test callback data is properly formatted
    - _Requirements: 1.4, 1.5_

- [x] 7. Checkpoint - Ensure core logic tests pass
  - Run all unit and property tests
  - Verify database operations work correctly
  - Verify video selection and rotation logic
  - Ask the user if questions arise

- [x] 8. Implement FastAPI backend server
  - [x] 8.1 Create FastAPI application with core endpoints
    - Set up FastAPI app with CORS middleware
    - Initialize database connection on startup
    - Load configuration from database on startup
    - _Requirements: 16.1, 16.2_

  - [x] 8.2 Implement daily send endpoint
    - `POST /api/send-daily`: Execute daily video delivery workflow
    - Load current config from database
    - Select next English and GK videos using VideoSelector
    - Send message via TelegramBot
    - Create new daily log entry with PENDING status
    - Increment day count and video indices
    - Advance GK rotation
    - Update config in database
    - Return response with day number and video details
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 1.7, 1.8, 8.3, 8.4_

  - [ ]* 8.3 Write property test for day counter monotonicity
    - **Property 3: Day Counter Monotonicity**
    - **Validates: Requirements 1.1, 8.3**
    - Test that day counter increases monotonically with each send

  - [ ]* 8.4 Write property test for manual send deduplication
    - **Property 11: Manual Send Deduplication**
    - **Validates: Requirements 8.5**
    - Test that multiple sends on same day create only one log entry

  - [x] 8.5 Implement webhook endpoint for Telegram callbacks
    - `POST /api/telegram/webhook`: Handle button click callbacks
    - Parse callback query from Telegram
    - Extract day number and status from callback data
    - Update log entry status in database
    - Recalculate and update streak
    - Send confirmation message via bot
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 11.4_

  - [ ]* 8.6 Write property test for status update idempotence
    - **Property 4: Status Update Idempotence**
    - **Validates: Requirements 2.5**
    - Test that updating status multiple times with same value results in same state

- [x] 9. Implement dashboard API endpoints
  - [x] 9.1 Create metrics endpoint
    - `GET /api/dashboard/metrics`: Return current day, completion percentages, streak
    - Load config and all logs from database
    - Calculate overall and weekly completion using CompletionCalculator
    - Return JSON with all metrics
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 9.2 Create logs endpoint with pagination
    - `GET /api/dashboard/logs?limit=50&offset=0`: Return paginated daily logs
    - Query logs ordered by day number descending
    - Return logs array and total count
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.3 Create playlist configuration endpoints
    - `GET /api/config/playlists`: Return all playlist URLs
    - `PUT /api/config/playlists`: Update playlist URL for a subject
    - Validate YouTube playlist URL format
    - Reset corresponding video index to 0 on URL change
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 9.4 Write property test for playlist URL validation
    - **Property 9: Playlist URL Validation**
    - **Validates: Requirements 6.2, 6.5**
    - Test that invalid URLs are rejected and valid URLs are accepted

  - [x] 9.5 Create admin action endpoints
    - `POST /api/admin/reset`: Reset all progress (indices, streak, day count, logs)
    - `POST /api/admin/send-now`: Manually trigger daily send
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.2_

  - [ ]* 9.6 Write property test for reset completeness
    - **Property 10: Reset Completeness**
    - **Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6**
    - Test that after reset, all indices are 0, streak is 0, day count is 0, logs are empty

- [ ] 10. Implement error handling and logging
  - [x] 10.1 Create error logging system
    - Add `error_logs` table to database schema
    - Create `ErrorLogger` class with `log_error()` method
    - Log errors with timestamp, type, message, stack trace, context
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [x] 10.2 Add retry logic with exponential backoff
    - Create `retry_with_backoff()` decorator
    - Configure max attempts (3), base delay (1s), exponential base (2)
    - Apply to Telegram API calls and database operations
    - _Requirements: 9.5, 16.5_

  - [ ]* 10.3 Write property test for retry behavior
    - Test that retries occur up to max attempts
    - Test that backoff delay increases exponentially
    - _Requirements: 9.5_

  - [x] 10.4 Add error endpoint for dashboard
    - `GET /api/errors/recent?limit=10`: Return recent error logs
    - _Requirements: 14.5_

- [x] 11. Checkpoint - Ensure backend tests pass
  - Run all backend unit and property tests
  - Test API endpoints with manual requests
  - Verify error handling and logging
  - Ask the user if questions arise

- [ ] 12. Implement GitHub Actions scheduling
  - [x] 12.1 Create GitHub Actions workflow file
    - Create `.github/workflows/daily-send.yml`
    - Configure cron schedule for daily execution (e.g., "0 6 * * *" for 6 AM UTC)
    - Add workflow step to call backend `/api/send-daily` endpoint
    - Use repository secrets for backend URL and authentication
    - _Requirements: 9.1, 9.2, 9.3_

  - [x] 12.2 Add workflow logging
    - Log workflow execution timestamp
    - Log API response from daily send
    - Log any errors during execution
    - _Requirements: 9.4_

- [x] 13. Implement React admin dashboard
  - [x] 13.1 Set up React project with Vite
    - Create React app with Vite: `npm create vite@latest frontend -- --template react`
    - Install dependencies: `axios` for API calls, styling library
    - Configure API base URL from environment variable
    - _Requirements: 4.1_

  - [x] 13.2 Create metrics display component
    - Create `MetricsPanel` component
    - Display current day, overall completion %, weekly completion %, streak
    - Add visual indicators (icons, colors) for each metric
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 13.3 Create daily logs table component
    - Create `LogsTable` component with columns: Day, Date, English #, GK Subject, GK #, Status
    - Fetch logs from `/api/dashboard/logs` endpoint
    - Display status with visual indicators (✅ DONE, ❌ NOT_DONE, ⏳ PENDING)
    - Format date as YYYY-MM-DD
    - _Requirements: 5.1, 5.3, 5.4, 5.5_

  - [x] 13.4 Implement dashboard polling for real-time updates
    - Use `useEffect` with `setInterval` to poll every 5 seconds
    - Fetch metrics and logs on each poll
    - Update state reactively when data changes
    - _Requirements: 4.5, 13.1, 13.2_

  - [ ]* 13.5 Write property test for dashboard polling freshness
    - **Property 14: Dashboard Polling Freshness**
    - **Validates: Requirements 13.1**
    - Test that updates appear within 5 seconds of database change

  - [x] 13.6 Create playlist configuration component
    - Create `ConfigPanel` component with input fields for each subject
    - Fetch current playlists from `/api/config/playlists`
    - Implement update handler that calls `PUT /api/config/playlists`
    - Display validation errors for invalid URLs
    - _Requirements: 6.1, 6.2, 6.3, 6.5_

  - [x] 13.7 Create admin actions component
    - Create `AdminActions` component with "Reset Progress" and "Send Now" buttons
    - Add confirmation dialog for reset action
    - Call `/api/admin/reset` and `/api/admin/send-now` endpoints
    - Refresh dashboard data after actions complete
    - _Requirements: 7.1, 8.1, 8.2_

  - [x] 13.8 Create error display component
    - Create `ErrorPanel` component
    - Fetch recent errors from `/api/errors/recent`
    - Display errors with timestamp, type, and message
    - _Requirements: 14.5_

  - [x] 13.9 Assemble main dashboard layout
    - Create `Dashboard` component that combines all sub-components
    - Arrange components in logical layout: metrics at top, logs in center, config and actions at bottom
    - Add loading indicators during data fetches
    - _Requirements: 4.1, 5.1, 6.1, 7.1, 8.1_

- [x] 14. Implement state restoration and consistency
  - [x] 14.1 Add startup state loading
    - Load all config from database when backend starts
    - Restore video indices, rotation index, day count, streak
    - _Requirements: 16.1, 16.2_

  - [x] 14.2 Add duplicate send prevention
    - Check if a log entry already exists for current day before sending
    - Skip send if entry exists
    - _Requirements: 16.3_

  - [ ]* 14.3 Write property test for state restoration
    - **Property 16: State Restoration After Restart**
    - **Validates: Requirements 16.1, 16.2**
    - Test that loaded config matches last persisted state

  - [ ]* 14.4 Write property test for state consistency
    - Test that server state always matches database state
    - _Requirements: 16.4_

- [x] 15. Integration and deployment preparation
  - [x] 15.1 Create environment configuration
    - Create `.env.example` files for backend and frontend
    - Document required environment variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `DATABASE_PATH`, `API_BASE_URL`
    - Create configuration loading module
    - _Requirements: 11.1, 11.2_

  - [x] 15.2 Create deployment documentation
    - Document Render deployment steps for backend
    - Document Vercel/Netlify deployment steps for frontend
    - Document GitHub Actions setup and secrets configuration
    - Document initial database setup and configuration
    - _Requirements: 12.1, 12.2, 12.3_

  - [x] 15.3 Add health check endpoint
    - `GET /api/health`: Return server status and database connectivity
    - Include version information and uptime
    - _Requirements: 16.1_

  - [ ]* 15.4 Write integration tests for complete workflows
    - Test end-to-end daily send flow: trigger → select videos → send message → create log
    - Test end-to-end completion flow: callback → update status → recalculate streak → confirm
    - Test end-to-end reset flow: reset → verify all state cleared
    - _Requirements: 1.1, 2.1, 7.2_

- [x] 16. Final checkpoint and validation
  - Run complete test suite (unit tests, property tests, integration tests)
  - Verify all API endpoints work correctly
  - Test Telegram bot message sending and callback handling
  - Test dashboard displays all data correctly
  - Verify GitHub Actions workflow triggers correctly
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use `hypothesis` library with minimum 100 iterations
- Integration tests verify end-to-end workflows
- Checkpoints ensure incremental validation at key milestones
- All code should follow Python PEP 8 style guidelines
- Frontend uses React with functional components and hooks
- Backend uses FastAPI with async/await patterns where appropriate
