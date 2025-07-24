# Tests Documentation

This document describes the test cases found in `base/tests.py` for the Circus Booking App.

## Overview

These tests cover the core functionality of the app, including:
- Trainer and client creation
- Dashboard access for both user types
- Trainer-client relationships
- Session and booking creation
- Booking sessions as a client
- Trainer creating a new client
- Display of trainers on the client dashboard

## Test Cases

### 1. `setUp`
- Creates a trainer user and profile.
- Creates a client user and profile, and links the client to the trainer.
- Creates a session for the trainer.
- Sets up a Django test client for HTTP requests.

### 2. `test_trainer_dashboard_access`
- Logs in as a trainer.
- Checks that the trainer dashboard is accessible and contains the correct heading.

### 3. `test_client_dashboard_access`
- Logs in as a client.
- Checks that the client dashboard is accessible and contains the correct heading.

### 4. `test_client_trainer_relationship`
- Verifies that the trainer is correctly linked to the client.

### 5. `test_session_creation`
- Confirms that a session is created and linked to the correct trainer.

### 6. `test_booking_creation`
- Creates a booking for the client and session.
- Checks that the booking exists and is linked to the correct client and session.

### 7. `test_client_can_book_session`
- Logs in as a client.
- Posts to the booking endpoint for a session.
- Verifies that the booking is created and the user is redirected to the client dashboard.

### 8. `test_trainer_can_create_client`
- Logs in as a trainer.
- Posts to the trainer client creation endpoint with new user data.
- Verifies that a new client user is created.

### 9. `test_client_dashboard_shows_trainers`
- Logs in as a client.
- Checks that the client dashboard displays the trainer's business name.

## Running the Tests

To run the tests, use the following command from your project root:

```sh
python manage.py test base
```

## Notes

- These tests assume the use of Django's default authentication and the model relationships as described in the codebase.
- You can expand these tests to cover more edge cases or additional features as your app grows.