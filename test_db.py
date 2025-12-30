import os
import db_manager as db

# Setup: Remove test db if exists to start fresh
if os.path.exists('stock_app.db'):
    # We won't delete the actual DB if it exists, to avoid losing user data.
    # Instead, we will test with a specific test user.
    print("Database exists. Proceeding with test user.")
else:
    print("Initializing database...")
    db.init_db()

test_user = "test_user_001"
test_pass = "password123"

print(f"\n--- Testing User Registration: {test_user} ---")
# Try to register (might fail if already exists from previous run, which is fine)
success = db.register_user(test_user, test_pass)
if success:
    print("Registration successful.")
else:
    print("User already exists (expected if running test multiple times).")

print("\n--- Testing Login ---")
user_id = db.login_user(test_user, test_pass)
if user_id:
    print(f"Login successful! User ID: {user_id}")
else:
    print("Login failed!")
    exit(1)

print("\n--- Testing Watchlist Retrieval ---")
watchlist = db.get_user_watchlist(user_id)
print(f"Current Watchlist: {watchlist}")

print("\n--- Testing Watchlist Update ---")
new_watchlist = "AAPL, GOOG, MSFT"
print(f"Updating watchlist to: {new_watchlist}")
db.update_user_watchlist(user_id, new_watchlist)

print("\n--- Verifying Persistence ---")
updated_watchlist = db.get_user_watchlist(user_id)
print(f"Retrieved Watchlist: {updated_watchlist}")

if updated_watchlist == new_watchlist:
    print("SUCCESS: Watchlist updated and persisted correctly!")
else:
    print("FAILURE: Watchlist did not match expected value.")

print("\n--- Test Complete ---")
