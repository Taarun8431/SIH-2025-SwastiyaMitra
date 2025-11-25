from app.database import engine
from sqlalchemy import inspect, text

def check_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('migrants')
    print("Columns in 'migrants' table:")
    found_location = False
    for column in columns:
        print(f"- {column['name']} ({column['type']})")
        if column['name'] == 'location':
            found_location = True
    
    if not found_location:
        print("\n❌ 'location' column is MISSING!")
    else:
        print("\n✅ 'location' column FOUND.")

    # Also check if PostGIS extension is enabled
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT PostGIS_Version();"))
            print(f"\n✅ PostGIS Version: {result.scalar()}")
        except Exception as e:
            print(f"\n❌ PostGIS check failed: {e}")

if __name__ == "__main__":
    check_schema()
