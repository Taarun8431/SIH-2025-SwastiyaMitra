from app.database import SessionLocal
from app import crud

def check_admin():
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, "admin")
        if user:
            print(f"✅ User found: {user.username} (Role: {user.role})")
        else:
            print("❌ User 'admin' NOT found!")
    except Exception as e:
        print(f"❌ Error checking user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()
