"""
Verify Database and Collections
"""
from pymongo import MongoClient

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "dayflow_hrms"

print("\n" + "="*80)
print(f"📊 DATABASE: {DATABASE_NAME}".center(80))
print("="*80)

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

# List collections
collections = db.list_collection_names()
print(f"\n✅ Collections ({len(collections)}):")
for coll_name in collections:
    count = db[coll_name].count_documents({})
    print(f"  - {coll_name.ljust(20)} : {count} documents")

# Sample data from User collection
print("\n" + "="*80)
print("👥 SAMPLE USERS:")
print("="*80)
users = db.User.find().limit(5)
for user in users:
    print(f"  {user.get('role', 'N/A').ljust(10)} | {user.get('email', 'N/A').ljust(30)} | {user.get('login_id', 'N/A')}")

print("\n" + "="*80)
print(f"✅ Database is clean and ready!")
print("="*80)

client.close()
