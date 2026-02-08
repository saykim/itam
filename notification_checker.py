"""
ITAM - Notification Checker
알림 자동 생성 배치 모듈
"""
import sqlite3
from datetime import datetime, date, timedelta

DB_PATH = 'itam.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def create_notification(conn, notification_type, severity, target_user_id, title, message, ref_type=None, ref_id=None):
    """알림 생성 (중복 방지)"""
    cursor = conn.cursor()
    # 같은 날 동일 유형+대상 알림이 있으면 스킵
    existing = cursor.execute('''
        SELECT 1 FROM Notification 
        WHERE notification_type = ? AND reference_type = ? AND reference_id = ? 
        AND DATE(created_at) = DATE('now')
    ''', (notification_type, ref_type, ref_id)).fetchone()
    
    if not existing:
        cursor.execute('''
            INSERT INTO Notification (notification_type, severity, target_user_id, title, message, 
                                       reference_type, reference_id, is_read, is_sent)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0)
        ''', (notification_type, severity, target_user_id, title, message, ref_type, ref_id))
        return True
    return False

def check_license_expiring():
    """라이선스 만료 임박 체크 (D-60, D-30, D-14, D-7, D-1)"""
    conn = get_db()
    today = date.today()
    alert_days = [60, 30, 14, 7, 1]
    created_count = 0
    
    for days in alert_days:
        target_date = today + timedelta(days=days)
        severity = 'critical' if days <= 7 else 'warning'
        
        licenses = conn.execute('''
            SELECT sl.*, u.user_id as manager_id
            FROM SoftwareLicense sl
            LEFT JOIN User u ON sl.license_manager_id = u.user_id
            WHERE sl.is_deleted = 0 AND sl.is_subscription = 1 
            AND sl.subscription_end = ?
        ''', (target_date.isoformat(),)).fetchall()
        
        for lic in licenses:
            title = f"라이선스 만료 D-{days}: {lic['software_name']}"
            message = f"{lic['software_name']} 라이선스가 {days}일 후 ({lic['subscription_end']}) 만료됩니다. 갱신을 검토해주세요."
            if create_notification(conn, 'LICENSE_EXPIRING', severity, lic['manager_id'] or 1, 
                                   title, message, 'LICENSE', lic['license_id']):
                created_count += 1
    
    conn.commit()
    conn.close()
    return created_count

def check_warranty_expiring():
    """보증 만료 임박 체크 (D-90, D-30, D-7)"""
    conn = get_db()
    today = date.today()
    alert_days = [90, 30, 7]
    created_count = 0
    
    for days in alert_days:
        target_date = today + timedelta(days=days)
        severity = 'critical' if days == 7 else 'warning' if days == 30 else 'info'
        
        assets = conn.execute('''
            SELECT a.*, u.user_id as manager_id
            FROM Asset a
            LEFT JOIN User u ON a.asset_manager_id = u.user_id
            WHERE a.is_deleted = 0 AND a.warranty_end = ?
        ''', (target_date.isoformat(),)).fetchall()
        
        for asset in assets:
            title = f"보증 만료 D-{days}: {asset['asset_number']}"
            message = f"{asset['asset_name']} ({asset['asset_number']}) 보증이 {days}일 후 만료됩니다."
            if create_notification(conn, 'WARRANTY_EXPIRING', severity, asset['manager_id'] or 1,
                                   title, message, 'ASSET', asset['asset_id']):
                created_count += 1
    
    conn.commit()
    conn.close()
    return created_count

def check_useful_life_expired():
    """사용연한 초과 자산 체크"""
    conn = get_db()
    created_count = 0
    
    # 사용연한 초과 자산 (이번 달에 만료된 건만)
    assets = conn.execute('''
        SELECT a.*, u.user_id as manager_id
        FROM Asset a
        LEFT JOIN User u ON a.asset_manager_id = u.user_id
        WHERE a.is_deleted = 0 
        AND a.useful_life_expire_date IS NOT NULL
        AND a.useful_life_expire_date < DATE('now')
        AND a.useful_life_expire_date >= DATE('now', '-30 days')
    ''').fetchall()
    
    for asset in assets:
        title = f"사용연한 초과: {asset['asset_number']}"
        message = f"{asset['asset_name']} ({asset['asset_number']})의 사용연한이 초과되었습니다. 교체/폐기를 검토해주세요."
        if create_notification(conn, 'USEFUL_LIFE_EXPIRED', 'warning', asset['manager_id'] or 1,
                               title, message, 'ASSET', asset['asset_id']):
            created_count += 1
    
    conn.commit()
    conn.close()
    return created_count

def check_eos_expired():
    """OS EOS 경과 자산 체크"""
    conn = get_db()
    created_count = 0
    
    assets = conn.execute('''
        SELECT a.*, e.product_name, e.eos_date, u.user_id as manager_id
        FROM Asset a
        JOIN EOSInfo e ON a.eos_id = e.eos_id
        LEFT JOIN User u ON a.asset_manager_id = u.user_id
        WHERE a.is_deleted = 0 
        AND e.eos_date < DATE('now')
        AND e.eos_date >= DATE('now', '-30 days')
    ''').fetchall()
    
    for asset in assets:
        title = f"OS EOS 경과: {asset['asset_number']}"
        message = f"{asset['asset_name']}의 {asset['product_name']}가 EOS({asset['eos_date']})를 경과했습니다. 업그레이드/교체를 검토해주세요."
        if create_notification(conn, 'OS_EOS_EXPIRED', 'critical', asset['manager_id'] or 1,
                               title, message, 'ASSET', asset['asset_id']):
            created_count += 1
    
    conn.commit()
    conn.close()
    return created_count

def check_license_exceeded():
    """라이선스 초과 체크"""
    conn = get_db()
    created_count = 0
    
    licenses = conn.execute('''
        SELECT sl.*, u.user_id as manager_id
        FROM SoftwareLicense sl
        LEFT JOIN User u ON sl.license_manager_id = u.user_id
        WHERE sl.is_deleted = 0 AND sl.used_quantity > sl.total_quantity
    ''').fetchall()
    
    for lic in licenses:
        title = f"라이선스 초과: {lic['software_name']}"
        message = f"{lic['software_name']} 라이선스가 초과되었습니다. (사용: {lic['used_quantity']}, 보유: {lic['total_quantity']})"
        if create_notification(conn, 'LICENSE_EXCEEDED', 'critical', lic['manager_id'] or 1,
                               title, message, 'LICENSE', lic['license_id']):
            created_count += 1
    
    conn.commit()
    conn.close()
    return created_count

def run_all_checks():
    """모든 알림 체크 실행"""
    results = {
        'license_expiring': check_license_expiring(),
        'warranty_expiring': check_warranty_expiring(),
        'useful_life_expired': check_useful_life_expired(),
        'eos_expired': check_eos_expired(),
        'license_exceeded': check_license_exceeded()
    }
    total = sum(results.values())
    print(f"✅ 알림 생성 완료: 총 {total}건")
    for k, v in results.items():
        if v > 0:
            print(f"   - {k}: {v}건")
    return results

if __name__ == '__main__':
    run_all_checks()
