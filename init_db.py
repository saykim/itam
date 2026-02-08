"""
ITAM PoC - Database Initialization
Phase1-01: DB Schema + Phase1-02: Initial Data
"""
import sqlite3
from datetime import datetime, date

DB_PATH = 'itam.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create all tables according to PRD v2.0 Data Model"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # ========================================
    # 7.1 기준정보 (Master Data)
    # ========================================
    
    # 7.1.1 사업장 (Location)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Location (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_code VARCHAR(20) NOT NULL UNIQUE,
        location_name VARCHAR(100) NOT NULL,
        address VARCHAR(500),
        building VARCHAR(100),
        floor VARCHAR(20),
        room VARCHAR(50),
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 7.1.2 부서 (Department)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Department (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_code VARCHAR(20) NOT NULL UNIQUE,
        dept_name VARCHAR(100) NOT NULL,
        dept_level VARCHAR(20) NOT NULL,
        parent_dept_id INTEGER,
        location_id INTEGER NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_dept_id) REFERENCES Department(dept_id),
        FOREIGN KEY (location_id) REFERENCES Location(location_id)
    )
    ''')
    
    # 7.1.3 사용자 (User)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_no VARCHAR(20) NOT NULL UNIQUE,
        user_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(20),
        mobile VARCHAR(20),
        dept_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        position VARCHAR(50),
        job_title VARCHAR(50),
        hire_date DATE,
        resign_date DATE,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dept_id) REFERENCES Department(dept_id),
        FOREIGN KEY (location_id) REFERENCES Location(location_id)
    )
    ''')
    
    # 7.1.4 자산 카테고리 (AssetCategory)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AssetCategory (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_code VARCHAR(20) NOT NULL UNIQUE,
        category_name VARCHAR(100) NOT NULL,
        category_level INTEGER NOT NULL,
        parent_category_id INTEGER,
        asset_type VARCHAR(20) NOT NULL,
        useful_life_months INTEGER,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (parent_category_id) REFERENCES AssetCategory(category_id)
    )
    ''')
    
    # 7.1.5 공급업체 (Vendor)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vendor (
        vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name VARCHAR(200) NOT NULL,
        vendor_type VARCHAR(50) NOT NULL,
        contact_name VARCHAR(50),
        contact_phone VARCHAR(20),
        contact_email VARCHAR(100),
        contract_info TEXT,
        is_active BOOLEAN NOT NULL DEFAULT 1
    )
    ''')
    
    # 7.1.6 EOS 정보 (EOSInfo)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EOSInfo (
        eos_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name VARCHAR(200) NOT NULL,
        product_type VARCHAR(20) NOT NULL,
        vendor VARCHAR(100),
        mainstream_end DATE,
        extended_end DATE,
        eos_date DATE NOT NULL,
        notes TEXT
    )
    ''')
    
    # ========================================
    # 7.2 핵심 테이블 (Core Tables)
    # ========================================
    
    # 7.2.1 자산 마스터 (Asset)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Asset (
        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_number VARCHAR(50) NOT NULL UNIQUE,
        asset_name VARCHAR(200) NOT NULL,
        category_id INTEGER NOT NULL,
        asset_status VARCHAR(20) NOT NULL DEFAULT '신규',
        location_id INTEGER NOT NULL,
        install_location VARCHAR(200),
        manufacturer VARCHAR(100),
        model_name VARCHAR(100),
        serial_number VARCHAR(100),
        specifications TEXT,
        purchase_date DATE,
        purchase_cost DECIMAL(15,2),
        purchase_vendor_id INTEGER,
        warranty_start DATE,
        warranty_end DATE,
        useful_life_months INTEGER,
        useful_life_expire_date DATE,
        current_user_id INTEGER,
        assigned_date DATE,
        asset_manager_id INTEGER NOT NULL,
        sub_manager_id INTEGER,
        ip_address VARCHAR(50),
        mac_address VARCHAR(50),
        hostname VARCHAR(100),
        os_info VARCHAR(100),
        eos_id INTEGER,
        last_inventory_date DATE,
        next_inventory_date DATE,
        disposal_date DATE,
        disposal_reason TEXT,
        notes TEXT,
        is_deleted BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER NOT NULL,
        updated_by INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES AssetCategory(category_id),
        FOREIGN KEY (location_id) REFERENCES Location(location_id),
        FOREIGN KEY (purchase_vendor_id) REFERENCES Vendor(vendor_id),
        FOREIGN KEY (current_user_id) REFERENCES User(user_id),
        FOREIGN KEY (asset_manager_id) REFERENCES User(user_id),
        FOREIGN KEY (sub_manager_id) REFERENCES User(user_id),
        FOREIGN KEY (eos_id) REFERENCES EOSInfo(eos_id),
        FOREIGN KEY (created_by) REFERENCES User(user_id),
        FOREIGN KEY (updated_by) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.2 자산 배정 (AssetAssignment)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AssetAssignment (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        is_primary BOOLEAN NOT NULL DEFAULT 1,
        assignment_type VARCHAR(20) NOT NULL DEFAULT '전용',
        assigned_date DATE NOT NULL,
        returned_date DATE,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        assigned_by INTEGER NOT NULL,
        notes TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (asset_id) REFERENCES Asset(asset_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (assigned_by) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.3 OT 장비 확장 (AssetOTDetail)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AssetOTDetail (
        ot_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL UNIQUE,
        firmware_version VARCHAR(50),
        protocol VARCHAR(50),
        connected_equipment VARCHAR(200),
        control_network_segment VARCHAR(100),
        safety_level VARCHAR(20),
        plc_program_version VARCHAR(50),
        last_firmware_update DATE,
        io_count VARCHAR(50),
        FOREIGN KEY (asset_id) REFERENCES Asset(asset_id)
    )
    ''')
    
    # 7.2.4 네트워크 장비 확장 (AssetNetworkDetail)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AssetNetworkDetail (
        network_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL UNIQUE,
        port_count INTEGER,
        port_speed VARCHAR(20),
        vlan_info TEXT,
        management_ip VARCHAR(50),
        firmware_version VARCHAR(50),
        ssid VARCHAR(100),
        channel VARCHAR(20),
        coverage_area VARCHAR(200),
        throughput VARCHAR(50),
        policy_count INTEGER,
        uplink_info VARCHAR(200),
        FOREIGN KEY (asset_id) REFERENCES Asset(asset_id)
    )
    ''')
    
    # 7.2.5 소프트웨어 라이선스 (SoftwareLicense)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SoftwareLicense (
        license_id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_number VARCHAR(50) NOT NULL UNIQUE,
        software_name VARCHAR(200) NOT NULL,
        category_id INTEGER NOT NULL,
        vendor_id INTEGER,
        version VARCHAR(50),
        license_type VARCHAR(30) NOT NULL,
        license_metric VARCHAR(20) NOT NULL,
        license_key VARCHAR(500),
        total_quantity INTEGER NOT NULL,
        used_quantity INTEGER NOT NULL DEFAULT 0,
        available_quantity INTEGER NOT NULL,
        purchase_date DATE,
        purchase_cost DECIMAL(15,2),
        subscription_start DATE,
        subscription_end DATE,
        is_subscription BOOLEAN NOT NULL DEFAULT 0,
        auto_renewal BOOLEAN,
        renewal_cost DECIMAL(15,2),
        parent_license_id INTEGER,
        license_manager_id INTEGER NOT NULL,
        compliance_status VARCHAR(20) NOT NULL DEFAULT '정상',
        alert_days_before INTEGER DEFAULT 30,
        notes TEXT,
        is_deleted BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES AssetCategory(category_id),
        FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id),
        FOREIGN KEY (parent_license_id) REFERENCES SoftwareLicense(license_id),
        FOREIGN KEY (license_manager_id) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.6 라이선스 계약 (LicenseContract)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LicenseContract (
        contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_id INTEGER NOT NULL,
        contract_number VARCHAR(100),
        contract_type VARCHAR(20) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_cost DECIMAL(15,2),
        total_cost DECIMAL(15,2),
        contract_start DATE NOT NULL,
        contract_end DATE,
        vendor_id INTEGER,
        document_path VARCHAR(500),
        notes TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (license_id) REFERENCES SoftwareLicense(license_id),
        FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id)
    )
    ''')
    
    # 7.2.7 라이선스 할당 (LicenseAssignment)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LicenseAssignment (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_id INTEGER NOT NULL,
        user_id INTEGER,
        asset_id INTEGER,
        assigned_date DATE NOT NULL,
        revoked_date DATE,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        assigned_by INTEGER NOT NULL,
        notes TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (license_id) REFERENCES SoftwareLicense(license_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (asset_id) REFERENCES Asset(asset_id),
        FOREIGN KEY (assigned_by) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.8 자산 이력 (AssetHistory) - INSERT ONLY
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AssetHistory (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_type VARCHAR(20) NOT NULL,
        reference_id INTEGER NOT NULL,
        action_type VARCHAR(30) NOT NULL,
        action_detail TEXT,
        changed_fields TEXT,
        previous_values TEXT,
        new_values TEXT,
        action_by INTEGER NOT NULL,
        action_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (action_by) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.9 실사 일정 (InventorySchedule)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InventorySchedule (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_name VARCHAR(200) NOT NULL,
        schedule_type VARCHAR(20) NOT NULL,
        frequency VARCHAR(20) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        target_category_id INTEGER,
        target_location_id INTEGER,
        assigned_manager_id INTEGER NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT '예정',
        total_asset_count INTEGER,
        checked_count INTEGER DEFAULT 0,
        completion_rate DECIMAL(5,2) DEFAULT 0,
        notes TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (target_category_id) REFERENCES AssetCategory(category_id),
        FOREIGN KEY (target_location_id) REFERENCES Location(location_id),
        FOREIGN KEY (assigned_manager_id) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.10 실사 상세 (InventoryDetail)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InventoryDetail (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id INTEGER NOT NULL,
        asset_id INTEGER NOT NULL,
        check_status VARCHAR(20) NOT NULL DEFAULT '미확인',
        checked_by INTEGER,
        checked_date DATETIME,
        location_match BOOLEAN,
        status_match BOOLEAN,
        actual_location VARCHAR(200),
        actual_status VARCHAR(20),
        notes TEXT,
        FOREIGN KEY (schedule_id) REFERENCES InventorySchedule(schedule_id),
        FOREIGN KEY (asset_id) REFERENCES Asset(asset_id),
        FOREIGN KEY (checked_by) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.11 알림 (Notification)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Notification (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        notification_type VARCHAR(30) NOT NULL,
        severity VARCHAR(10) NOT NULL,
        target_user_id INTEGER NOT NULL,
        title VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        reference_type VARCHAR(20),
        reference_id INTEGER,
        is_read BOOLEAN NOT NULL DEFAULT 0,
        is_sent BOOLEAN NOT NULL DEFAULT 0,
        sent_at DATETIME,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (target_user_id) REFERENCES User(user_id)
    )
    ''')
    
    # 7.2.12 시스템 설정 (SystemConfig)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SystemConfig (
        config_id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key VARCHAR(100) NOT NULL UNIQUE,
        config_value TEXT NOT NULL,
        description VARCHAR(500),
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_by INTEGER,
        FOREIGN KEY (updated_by) REFERENCES User(user_id)
    )
    ''')
    
    # ========================================
    # Create Indexes for Performance
    # ========================================
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_status ON Asset(asset_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_category ON Asset(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_location ON Asset(location_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_manager ON Asset(asset_manager_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_current_user ON Asset(current_user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_deleted ON Asset(is_deleted)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_license_compliance ON SoftwareLicense(compliance_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_license_subscription_end ON SoftwareLicense(subscription_end)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_user ON Notification(target_user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_read ON Notification(is_read)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_ref ON AssetHistory(reference_type, reference_id)')
    
    conn.commit()
    conn.close()
    print("✅ 테이블 생성 완료")

def insert_initial_data():
    """Insert initial master data according to PRD v2.0"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # ========================================
    # 사업장 (Location)
    # ========================================
    locations = [
        ('HQ', '본사', '서울시 강남구 테헤란로 123', 'A동', None, None),
        ('FAC1', '제1공장', '경기도 평택시 산단로 456', 'B동', None, None),
        ('FAC2', '제2공장', '경기도 안산시 산업로 789', 'C동', None, None),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Location (location_code, location_name, address, building, floor, room)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', locations)
    
    # ========================================
    # 부서 (Department)
    # ========================================
    departments = [
        ('IT', 'IT인프라팀', '팀', None, 1),
        ('HR', '인사팀', '팀', None, 1),
        ('PROD1', '생산1팀', '팀', None, 2),
        ('PROD2', '생산2팀', '팀', None, 3),
        ('QA', '품질관리팀', '팀', None, 1),
        ('ENG', '설비팀', '팀', None, 2),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Department (dept_code, dept_name, dept_level, parent_dept_id, location_id)
        VALUES (?, ?, ?, ?, ?)
    ''', departments)
    
    # ========================================
    # 사용자 (User) - Admin + Sample
    # ========================================
    users = [
        ('ADMIN', '시스템관리자', 'admin@company.com', None, None, 1, 1, '팀장', '과장', '2020-01-01', None, 1, 'admin'),
        ('EMP001', '박과장', 'park@company.com', None, None, 1, 1, 'IT담당', '과장', '2021-03-01', None, 1, 'manager'),
        ('EMP002', '김사원', 'kim@company.com', None, None, 2, 1, None, '사원', '2024-03-15', None, 1, 'user'),
        ('EMP003', '이대리', 'lee@company.com', None, None, 6, 2, '설비담당', '대리', '2022-06-01', None, 1, 'manager'),
        ('EMP004', '최주임', 'choi@company.com', None, None, 3, 2, None, '주임', '2023-01-15', None, 1, 'user'),
        ('EMP005', '정사원', 'jung@company.com', None, None, 1, 1, None, '사원', '2023-08-01', '2026-01-31', 0, 'user'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO User (employee_no, user_name, email, phone, mobile, dept_id, location_id, 
                                     position, job_title, hire_date, resign_date, is_active, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    
    # ========================================
    # 자산 카테고리 (AssetCategory) - PRD 6장 기준
    # ========================================
    categories = [
        # 대분류 - HW
        ('HW', '하드웨어', 1, None, 'HW', None),
        # 중분류 - 사용자 단말
        ('HW-UD', '사용자 단말', 2, 1, 'HW', None),
        # 소분류
        ('NB', '노트북', 3, 2, 'HW', 36),
        ('DT', '데스크탑', 3, 2, 'HW', 60),
        ('MN', '모니터', 3, 2, 'HW', 60),
        # 중분류 - 서버
        ('HW-SRV', '서버', 2, 1, 'HW', None),
        ('SRV', '물리서버', 3, 6, 'HW', 60),
        ('VSRV', '가상서버', 3, 6, 'HW', None),
        # 중분류 - 주변기기
        ('HW-PR', '주변기기', 2, 1, 'HW', None),
        ('KSK', '키오스크', 3, 9, 'HW', 60),
        ('ETC', '전산기타', 3, 9, 'HW', 60),
        
        # 대분류 - Network
        ('NW', '네트워크 장비', 1, None, 'NETWORK', None),
        ('NW-WIRED', '유선 네트워크', 2, 12, 'NETWORK', None),
        ('SW-L2', '스위치 (L2)', 3, 13, 'NETWORK', 60),
        ('SW-L3', '스위치 (L3)', 3, 13, 'NETWORK', 60),
        ('RTR', '라우터', 3, 13, 'NETWORK', 60),
        ('FW', '방화벽', 3, 13, 'NETWORK', 60),
        ('NW-WIRELESS', '무선 네트워크', 2, 12, 'NETWORK', None),
        ('AP', 'Access Point', 3, 18, 'NETWORK', 60),
        ('NW-SEC', '보안장비', 2, 12, 'NETWORK', None),
        ('SEC', 'IPS/IDS', 3, 20, 'NETWORK', 60),
        
        # 대분류 - OT
        ('OT', 'OT 장비', 1, None, 'OT', None),
        ('PLC', 'PLC', 2, 22, 'OT', 120),
        ('HMI', 'HMI', 2, 22, 'OT', 84),
        ('OPC', 'OPC Server/Gateway', 2, 22, 'OT', 84),
        ('EQP', '설비전산장비', 2, 22, 'OT', 84),
        
        # 대분류 - SW
        ('SW', '소프트웨어 라이선스', 1, None, 'SW', None),
        ('SW-OS', 'OS', 2, 27, 'SW', None),
        ('SW-OFF', '오피스/생산성', 2, 27, 'SW', None),
        ('SW-CAD', '설계/엔지니어링', 2, 27, 'SW', None),
        ('SW-DEV', '개발도구', 2, 27, 'SW', None),
        ('SW-SEC', '보안 소프트웨어', 2, 27, 'SW', None),
        ('SW-INFRA', '인프라 SW', 2, 27, 'SW', None),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO AssetCategory (category_code, category_name, category_level, 
                                              parent_category_id, asset_type, useful_life_months)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', categories)
    
    # ========================================
    # EOS 정보 (EOSInfo) - 부록 A
    # ========================================
    eos_info = [
        ('Windows 7 SP1', 'OS', 'Microsoft', None, '2020-01-14', '2020-01-14', '연장 지원 종료'),
        ('Windows 8.1', 'OS', 'Microsoft', None, '2023-01-10', '2023-01-10', '연장 지원 종료'),
        ('Windows 10 21H2', 'OS', 'Microsoft', None, '2024-06-11', '2024-06-11', 'Enterprise/Education'),
        ('Windows 10 22H2', 'OS', 'Microsoft', None, '2025-10-14', '2025-10-14', '마지막 Win10 버전'),
        ('Windows 11 22H2', 'OS', 'Microsoft', None, '2025-10-14', '2025-10-14', None),
        ('Windows 11 23H2', 'OS', 'Microsoft', None, '2026-11-10', '2026-11-10', None),
        ('Windows Server 2012 R2', 'OS', 'Microsoft', None, '2023-10-10', '2023-10-10', '연장 지원 종료'),
        ('Windows Server 2016', 'OS', 'Microsoft', None, '2027-01-12', '2027-01-12', '연장 지원 종료 예정'),
        ('Windows Server 2019', 'OS', 'Microsoft', None, '2029-01-09', '2029-01-09', '연장 지원 종료 예정'),
        ('Windows Server 2022', 'OS', 'Microsoft', None, '2031-10-14', '2031-10-14', '연장 지원 종료 예정'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO EOSInfo (product_name, product_type, vendor, mainstream_end, extended_end, eos_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', eos_info)
    
    # ========================================
    # 공급업체 (Vendor)
    # ========================================
    vendors = [
        ('한국레노버', '제조사', '김담당', '02-1234-5678', 'sales@lenovo.kr', None),
        ('한국HP', '제조사', '박담당', '02-2345-6789', 'sales@hp.kr', None),
        ('한국델', '제조사', '이담당', '02-3456-7890', 'sales@dell.kr', None),
        ('한국마이크로소프트', '공급사', '최담당', '02-4567-8901', 'sales@microsoft.kr', None),
        ('(주)IT솔루션', '유지보수', '정담당', '02-5678-9012', 'support@itsol.kr', None),
        ('AVEVA Korea', '공급사', '강담당', '02-6789-0123', 'sales@aveva.kr', None),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Vendor (vendor_name, vendor_type, contact_name, contact_phone, contact_email, contract_info)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', vendors)
    
    # ========================================
    # 시스템 설정 (SystemConfig) - 부록 C
    # ========================================
    configs = [
        ('license_exceed_policy', 'warn', '라이선스 초과 시 정책 (warn/block)'),
        ('default_inventory_cycle_months', '6', '기본 실사 주기 (월)'),
        ('alert_license_expire_days', '60,30,14,7,1', '라이선스 만료 알림 기준일'),
        ('alert_warranty_expire_days', '90,30,7', '보증 만료 알림 기준일'),
        ('asset_stale_threshold_days', '180', '자산 미갱신 판단 기준일'),
        ('default_useful_life_notebook', '36', '노트북 기본 사용연한 (월)'),
        ('default_useful_life_desktop', '60', '데스크탑 기본 사용연한 (월)'),
        ('default_useful_life_monitor', '60', '모니터 기본 사용연한 (월)'),
        ('default_useful_life_server', '60', '서버 기본 사용연한 (월)'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO SystemConfig (config_key, config_value, description)
        VALUES (?, ?, ?)
    ''', configs)
    
    conn.commit()
    conn.close()
    print("✅ 초기 데이터 삽입 완료")

def insert_sample_data():
    """Insert sample assets and licenses for testing"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today = date.today().strftime('%Y-%m-%d')
    
    # ========================================
    # 샘플 자산 (Asset)
    # ========================================
    sample_assets = [
        # 노트북 - 본사
        ('HQ-NB-2024-0001', '박과장 노트북', 3, '사용중', 1, 'A동 3층', 'Lenovo', 'ThinkPad T14s Gen3', 'PF3ABC123', 
         '{"cpu": "i7-1365U", "ram_gb": 16, "storage_type": "SSD", "storage_gb": 512}', 
         '2024-01-15', 2100000, 1, '2024-01-15', '2027-01-14', 36, '2027-01-15', 2, '2024-01-15', 1, None,
         '192.168.1.101', 'AA:BB:CC:11:22:33', 'NB-PARK-01', 'Windows 11 23H2', 6, 0, 1, 1),
        ('HQ-NB-2024-0002', '김사원 노트북', 3, '사용중', 1, 'A동 2층', 'Lenovo', 'ThinkPad T14s Gen4', 'PF4DEF456',
         '{"cpu": "i7-13700", "ram_gb": 32, "storage_type": "SSD", "storage_gb": 1024}',
         '2024-03-20', 2500000, 1, '2024-03-20', '2027-03-19', 36, '2027-03-20', 3, '2024-03-20', 1, None,
         '192.168.1.102', 'AA:BB:CC:11:22:34', 'NB-KIM-01', 'Windows 11 23H2', 6, 0, 1, 1),
        ('HQ-NB-2023-0001', '여유 노트북#1', 3, '여유', 1, 'A동 1층 IT창고', 'HP', 'EliteBook 850 G8', 'HP1GHI789',
         '{"cpu": "i5-1145G7", "ram_gb": 16, "storage_type": "SSD", "storage_gb": 256}',
         '2023-06-01', 1800000, 2, '2023-06-01', '2026-05-31', 36, '2026-06-01', None, None, 1, None,
         None, None, None, 'Windows 10 22H2', 4, 0, 1, 1),
         
        # 모니터 - 본사  
        ('HQ-MN-2024-0001', '박과장 모니터', 5, '사용중', 1, 'A동 3층', 'LG', '27UL850', 'LG1234567',
         '{"size_inch": 27, "resolution": "3840x2160", "panel_type": "IPS"}',
         '2024-01-15', 450000, None, '2024-01-15', '2026-01-14', 60, '2029-01-15', 2, '2024-01-15', 1, None,
         None, None, None, None, None, 0, 1, 1),
        ('HQ-MN-2024-0002', '김사원 모니터', 5, '사용중', 1, 'A동 2층', 'Dell', 'U2723QE', 'DELL987654',
         '{"size_inch": 27, "resolution": "3840x2160", "panel_type": "IPS"}',
         '2024-03-20', 480000, None, '2024-03-20', '2026-03-19', 60, '2029-03-20', 3, '2024-03-20', 1, None,
         None, None, None, None, None, 0, 1, 1),
         
        # 서버 - 본사
        ('HQ-SRV-2022-0001', '메인 DB 서버', 7, '사용중', 1, '본사 서버실 R01-U15', 'Dell', 'PowerEdge R750', 'SRV001ABC',
         '{"cpu": "Xeon Gold 6326", "cpu_count": 2, "ram_gb": 256, "storage": "SSD 1TB x4 RAID10"}',
         '2022-06-01', 15000000, 3, '2022-06-01', '2025-05-31', 60, '2027-06-01', None, None, 1, None,
         '10.0.0.10', 'AA:BB:CC:00:00:10', 'DB-MAIN-01', 'Windows Server 2022', 10, 0, 1, 1),
         
        # PLC - 제1공장
        ('FAC1-PLC-2020-0001', '1호기 메인 PLC', 23, '사용중', 2, 'B동 1층 MCC실', 'Siemens', 'S7-1500', 'PLC2020001',
         '{}', '2020-03-01', 8000000, None, '2020-03-01', '2025-02-28', 120, '2030-03-01', None, None, 4, None,
         '192.168.100.10', None, 'PLC-FAC1-01', None, None, 0, 1, 1),
        ('FAC1-PLC-2020-0002', '2호기 컨베이어 PLC', 23, '사용중', 2, 'B동 2층 MCC실', 'Rockwell', 'ControlLogix', 'PLC2020002',
         '{}', '2020-06-15', 7500000, None, '2020-06-15', '2025-06-14', 120, '2030-06-15', None, None, 4, None,
         '192.168.100.11', None, 'PLC-FAC1-02', None, None, 0, 1, 1),
         
        # 네트워크 - 본사
        ('HQ-NW-2023-0001', '본사 코어 스위치', 15, '사용중', 1, '본사 서버실 R01-U01', 'Cisco', 'Catalyst 9300', 'NW2023001',
         '{}', '2023-01-15', 12000000, None, '2023-01-15', '2028-01-14', 60, '2028-01-15', None, None, 1, None,
         '10.0.0.1', 'CC:DD:EE:00:00:01', 'SW-CORE-01', None, None, 0, 1, 1),
    ]
    
    for asset in sample_assets:
        try:
            cursor.execute('''
                INSERT INTO Asset (asset_number, asset_name, category_id, asset_status, location_id, install_location,
                                   manufacturer, model_name, serial_number, specifications, purchase_date, purchase_cost,
                                   purchase_vendor_id, warranty_start, warranty_end, useful_life_months, useful_life_expire_date,
                                   current_user_id, assigned_date, asset_manager_id, sub_manager_id, ip_address, mac_address,
                                   hostname, os_info, eos_id, is_deleted, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', asset)
        except sqlite3.IntegrityError:
            pass  # Skip if already exists
    
    # ========================================
    # OT 확장 정보 (AssetOTDetail)
    # ========================================
    ot_details = [
        (7, 'v4.5.1', 'Profinet', '1호기 메인라인', 'OT-Zone1', 'SIL2', 'v2.1.0', '2024-06-01', 'DI64/DO32/AI16'),
        (8, 'v21.011', 'EtherNet/IP', '2호기 컨베이어', 'OT-Zone2', 'SIL1', 'v3.0.2', '2024-08-15', 'DI32/DO16/AI8'),
    ]
    for ot in ot_details:
        try:
            cursor.execute('''
                INSERT INTO AssetOTDetail (asset_id, firmware_version, protocol, connected_equipment, 
                                           control_network_segment, safety_level, plc_program_version, 
                                           last_firmware_update, io_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ot)
        except sqlite3.IntegrityError:
            pass
    
    # ========================================
    # 네트워크 확장 정보 (AssetNetworkDetail)
    # ========================================
    nw_details = [
        (9, 48, '1G', 'VLAN10(업무), VLAN20(게스트), VLAN100(서버)', '10.0.0.1', 'IOS-XE 17.9.1', None, None, None, '40Gbps', None, 'Uplink to ISP Router'),
    ]
    for nw in nw_details:
        try:
            cursor.execute('''
                INSERT INTO AssetNetworkDetail (asset_id, port_count, port_speed, vlan_info, management_ip, 
                                                 firmware_version, ssid, channel, coverage_area, throughput, 
                                                 policy_count, uplink_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', nw)
        except sqlite3.IntegrityError:
            pass
    
    # ========================================
    # 자산 배정 이력 (AssetAssignment)
    # ========================================
    assignments = [
        (1, 2, 1, '전용', '2024-01-15', None, 1, 1, None),
        (2, 3, 1, '전용', '2024-03-20', None, 1, 1, None),
        (4, 2, 1, '전용', '2024-01-15', None, 1, 1, None),
        (5, 3, 1, '전용', '2024-03-20', None, 1, 1, None),
    ]
    for assign in assignments:
        try:
            cursor.execute('''
                INSERT INTO AssetAssignment (asset_id, user_id, is_primary, assignment_type, assigned_date, 
                                              returned_date, is_active, assigned_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', assign)
        except sqlite3.IntegrityError:
            pass
    
    # ========================================
    # 샘플 라이선스 (SoftwareLicense)
    # ========================================
    licenses = [
        ('HQ-SW-2024-0001', 'Microsoft 365 E3', 29, 4, None, '구독', 'per_user', None, 100, 3, 97,
         '2024-01-01', 50000000, '2024-01-01', '2024-12-31', 1, 1, 48000000, None, 1, '정상', 30, None, 0),
        ('HQ-SW-2024-0002', 'Windows 11 Pro', 28, 4, None, '볼륨', 'per_device', None, 150, 5, 145,
         '2024-01-01', 30000000, None, None, 0, None, None, None, 1, '정상', 30, None, 0),
        ('HQ-SW-2024-0003', 'AutoCAD 2024', 30, None, '2024', '구독', 'per_user', None, 15, 8, 7,
         '2024-03-01', 25000000, '2024-03-01', '2025-02-28', 1, 1, 24000000, None, 1, '정상', 30, None, 0),
        ('HQ-SW-2024-0004', 'AVEVA Edge', 30, 6, '2023', '구독', 'concurrent', None, 10, 11, -1,
         '2024-01-01', 80000000, '2024-01-01', '2024-12-31', 1, 1, 75000000, None, 1, '초과', 30, '동시 접속자 초과', 0),
    ]
    for lic in licenses:
        try:
            cursor.execute('''
                INSERT INTO SoftwareLicense (license_number, software_name, category_id, vendor_id, version, 
                                              license_type, license_metric, license_key, total_quantity, used_quantity, 
                                              available_quantity, purchase_date, purchase_cost, subscription_start, 
                                              subscription_end, is_subscription, auto_renewal, renewal_cost, 
                                              parent_license_id, license_manager_id, compliance_status, alert_days_before, 
                                              notes, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', lic)
        except sqlite3.IntegrityError:
            pass
    
    # ========================================
    # 라이선스 할당 (LicenseAssignment) 
    # ========================================
    license_assigns = [
        (1, 2, None, '2024-01-15', None, 1, 1, None),  # M365 -> 박과장
        (1, 3, None, '2024-03-20', None, 1, 1, None),  # M365 -> 김사원
        (1, 6, None, '2023-09-01', None, 1, 1, None),  # M365 -> 정사원 (퇴사자)
        (3, 2, None, '2024-03-01', None, 1, 1, None),  # AutoCAD -> 박과장
        (4, 2, None, '2024-01-15', None, 1, 1, None),  # AVEVA -> 박과장
        (4, 3, None, '2024-03-20', None, 1, 1, None),  # AVEVA -> 김사원
        (4, 4, None, '2024-02-01', None, 1, 1, None),  # AVEVA -> 이대리
        (4, 5, None, '2024-02-15', None, 1, 1, None),  # AVEVA -> 최주임
        (4, 6, None, '2023-09-01', None, 1, 1, None),  # AVEVA -> 정사원 (퇴사자)
    ]
    for la in license_assigns:
        try:
            cursor.execute('''
                INSERT INTO LicenseAssignment (license_id, user_id, asset_id, assigned_date, revoked_date, 
                                                is_active, assigned_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', la)
        except sqlite3.IntegrityError:
            pass
    
    # Update used/available quantities for AVEVA
    cursor.execute('''
        UPDATE SoftwareLicense 
        SET used_quantity = (SELECT COUNT(*) FROM LicenseAssignment WHERE license_id = 4 AND is_active = 1),
            available_quantity = total_quantity - (SELECT COUNT(*) FROM LicenseAssignment WHERE license_id = 4 AND is_active = 1)
        WHERE license_id = 4
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 샘플 데이터 삽입 완료")

def main():
    """Initialize database with schema and data"""
    print("🚀 ITAM Database 초기화 시작...")
    create_tables()
    insert_initial_data()
    insert_sample_data()
    print("🎉 모든 초기화 작업 완료!")
    print(f"📁 Database: {DB_PATH}")

if __name__ == '__main__':
    main()
