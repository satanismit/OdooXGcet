"""
Database Cleanup Script
Removes all unnecessary test databases
"""
from pymongo import MongoClient

MONGODB_URL = "mongodb://localhost:27017"
KEEP_DATABASE = "dayflow_hrms"  # The only database we need

# Databases to remove
TEST_DATABASES = [
    "dayflow_hrms_test",
    "dayflow_hrms_test_full_system",
    "dayflow_hrms_test_phase2",
    "dayflow_hrms_test_phase4",
    "dayflow_hrms_test_phase5",
    "dayflow_hrms_test_phase6",
]

print("\n" + "="*80)
print("🗑️  DATABASE CLEANUP".center(80))
print("="*80)

client = MongoClient(MONGODB_URL)

# List all databases before cleanup
print("\n📊 Current Databases:")
all_dbs = client.list_database_names()
for db in all_dbs:
    if db not in ['admin', 'config', 'local']:
        print(f"  - {db}")

print(f"\n✅ KEEPING: {KEEP_DATABASE}")
print(f"🗑️  REMOVING: {len(TEST_DATABASES)} test databases")

# Remove test databases
removed = 0
for db_name in TEST_DATABASES:
    if db_name in all_dbs:
        print(f"\n  Dropping {db_name}...", end=" ")
        client.drop_database(db_name)
        print("✅ Deleted")
        removed += 1
    else:
        print(f"\n  {db_name} not found (already deleted)")

# List databases after cleanup
print("\n" + "="*80)
print("📊 Databases After Cleanup:")
final_dbs = client.list_database_names()
for db in final_dbs:
    if db not in ['admin', 'config', 'local']:
        icon = "✅" if db == KEEP_DATABASE else "⚠️"
        print(f"  {icon} {db}")

print("\n" + "="*80)
print(f"✅ CLEANUP COMPLETE!")
print(f"   Removed: {removed} databases")
print(f"   Remaining: {KEEP_DATABASE}")
print("="*80)

client.close()
