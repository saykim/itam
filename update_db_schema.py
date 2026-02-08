
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'itam_prod.db')

def add_license_status_column():
    print(f"🔄 Updating license schema in {DB_PATH}...")
    try:
        if not os.path.exists(DB_PATH):
            print(f"❌ Database not found at {DB_PATH}")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(SoftwareLicense)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'license_status' not in columns:
            cursor.execute("ALTER TABLE SoftwareLicense ADD COLUMN license_status VARCHAR(20) NOT NULL DEFAULT '활성'")
            print("✅ 'license_status' column added successfully.")
            
            # Create index for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_status ON SoftwareLicense(license_status)")
            print("✅ Index 'idx_license_status' created.")
        else:
            print("ℹ️ 'license_status' column already exists.")

        # Create per-key inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LicenseKey (
                license_key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id INTEGER NOT NULL,
                key_value VARCHAR(500) NOT NULL,
                key_status VARCHAR(20) NOT NULL DEFAULT '가용',
                assigned_assignment_id INTEGER,
                assigned_date DATE,
                revoked_date DATE,
                notes TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(license_id, key_value),
                FOREIGN KEY (license_id) REFERENCES SoftwareLicense(license_id)
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_key_license ON LicenseKey(license_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_license_key_status ON LicenseKey(key_status)")
        print("✅ LicenseKey table/indexes checked.")

        # Add key link to assignment
        cursor.execute("PRAGMA table_info(LicenseAssignment)")
        la_columns = [info[1] for info in cursor.fetchall()]
        if 'license_key_id' not in la_columns:
            cursor.execute("ALTER TABLE LicenseAssignment ADD COLUMN license_key_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignment_licensekey ON LicenseAssignment(license_key_id)")
            print("✅ 'license_key_id' column added to LicenseAssignment.")
        else:
            print("ℹ️ 'license_key_id' column already exists.")

        conn.commit()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    add_license_status_column()
