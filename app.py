"""
ITAM PoC - Flask API Server
Phase1-03~14: All Backend APIs
"""
from flask import Flask, request, jsonify, send_file, render_template
from functools import wraps
import sqlite3
import json
from datetime import datetime, date
import os

app = Flask(__name__)
DB_PATH = 'itam_prod.db'

# ========================================
# Database Helpers
# ========================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(row) for row in rows]

def api_response(success=True, data=None, message=None, status=200):
    return jsonify({"success": success, "data": data, "message": message}), status

def log_history(conn, ref_type, ref_id, action_type, detail, prev_vals=None, new_vals=None, action_by=1):
    """Insert audit trail record"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO AssetHistory (reference_type, reference_id, action_type, action_detail, 
                                   previous_values, new_values, action_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (ref_type, ref_id, action_type, detail, 
          json.dumps(prev_vals, ensure_ascii=False) if prev_vals else None,
          json.dumps(new_vals, ensure_ascii=False) if new_vals else None, action_by))

# ========================================
# Location API (사업장)
# ========================================
@app.route('/api/locations', methods=['GET'])
def get_locations():
    conn = get_db()
    rows = conn.execute('SELECT * FROM Location WHERE is_active = 1 ORDER BY location_id').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/locations', methods=['POST'])
def create_location():
    data = request.json
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Location (location_code, location_name, address, building, floor, room)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['location_code'], data['location_name'], data.get('address'),
              data.get('building'), data.get('floor'), data.get('room')))
        conn.commit()
        return api_response(data={"location_id": cursor.lastrowid}, message="사업장 등록 완료", status=201)
    except sqlite3.IntegrityError as e:
        return api_response(False, message=f"중복 오류: {str(e)}", status=400)
    finally:
        conn.close()

@app.route('/api/locations/<int:id>', methods=['GET'])
def get_location(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM Location WHERE location_id = ?', (id,)).fetchone()
    conn.close()
    if row:
        return api_response(data=row_to_dict(row))
    return api_response(False, message="사업장을 찾을 수 없습니다", status=404)

@app.route('/api/locations/<int:id>', methods=['PUT'])
def update_location(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Location SET location_code=?, location_name=?, address=?, building=?, floor=?, room=?, updated_at=CURRENT_TIMESTAMP
        WHERE location_id=?
    ''', (data['location_code'], data['location_name'], data.get('address'),
          data.get('building'), data.get('floor'), data.get('room'), id))
    conn.commit()
    conn.close()
    return api_response(message="사업장 수정 완료")

@app.route('/api/locations/<int:id>', methods=['DELETE'])
def delete_location(id):
    conn = get_db()
    conn.execute('UPDATE Location SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE location_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="사업장 비활성화 완료")

# ========================================
# Department API (부서)
# ========================================
@app.route('/api/departments', methods=['GET'])
def get_departments():
    conn = get_db()
    rows = conn.execute('''
        SELECT d.*, l.location_name, p.dept_name as parent_dept_name
        FROM Department d
        LEFT JOIN Location l ON d.location_id = l.location_id
        LEFT JOIN Department p ON d.parent_dept_id = p.dept_id
        WHERE d.is_active = 1
        ORDER BY d.dept_id
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/departments', methods=['POST'])
def create_department():
    data = request.json
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Department (dept_code, dept_name, dept_level, parent_dept_id, location_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['dept_code'], data['dept_name'], data['dept_level'],
              data.get('parent_dept_id'), data['location_id']))
        conn.commit()
        return api_response(data={"dept_id": cursor.lastrowid}, message="부서 등록 완료", status=201)
    except sqlite3.IntegrityError as e:
        return api_response(False, message=f"중복 오류: {str(e)}", status=400)
    finally:
        conn.close()

@app.route('/api/departments/<int:id>', methods=['GET'])
def get_department(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM Department WHERE dept_id = ?', (id,)).fetchone()
    conn.close()
    return api_response(data=row_to_dict(row)) if row else api_response(False, message="부서 없음", status=404)

@app.route('/api/departments/<int:id>', methods=['PUT'])
def update_department(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE Department SET dept_code=?, dept_name=?, dept_level=?, parent_dept_id=?, location_id=?, updated_at=CURRENT_TIMESTAMP
        WHERE dept_id=?
    ''', (data['dept_code'], data['dept_name'], data['dept_level'], data.get('parent_dept_id'), data['location_id'], id))
    conn.commit()
    conn.close()
    return api_response(message="부서 수정 완료")

@app.route('/api/departments/<int:id>', methods=['DELETE'])
def delete_department(id):
    conn = get_db()
    conn.execute('UPDATE Department SET is_active = 0 WHERE dept_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="부서 비활성화 완료")

# ========================================
# User API (사용자)
# ========================================
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db()
    rows = conn.execute('''
        SELECT u.*, d.dept_name, l.location_name
        FROM User u
        LEFT JOIN Department d ON u.dept_id = d.dept_id
        LEFT JOIN Location l ON u.location_id = l.location_id
        ORDER BY u.user_id
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO User (employee_no, user_name, email, phone, mobile, dept_id, location_id, 
                              position, job_title, hire_date, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['employee_no'], data['user_name'], data['email'], data.get('phone'),
              data.get('mobile'), data['dept_id'], data['location_id'], data.get('position'),
              data.get('job_title'), data.get('hire_date'), data.get('role', 'user')))
        conn.commit()
        return api_response(data={"user_id": cursor.lastrowid}, message="사용자 등록 완료", status=201)
    except sqlite3.IntegrityError as e:
        return api_response(False, message=f"중복 오류: {str(e)}", status=400)
    finally:
        conn.close()

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    conn = get_db()
    row = conn.execute('''
        SELECT u.*, d.dept_name, l.location_name
        FROM User u
        LEFT JOIN Department d ON u.dept_id = d.dept_id
        LEFT JOIN Location l ON u.location_id = l.location_id
        WHERE u.user_id = ?
    ''', (id,)).fetchone()
    conn.close()
    return api_response(data=row_to_dict(row)) if row else api_response(False, message="사용자 없음", status=404)

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE User SET employee_no=?, user_name=?, email=?, phone=?, mobile=?, dept_id=?, location_id=?,
                        position=?, job_title=?, hire_date=?, resign_date=?, is_active=?, role=?, updated_at=CURRENT_TIMESTAMP
        WHERE user_id=?
    ''', (data['employee_no'], data['user_name'], data['email'], data.get('phone'), data.get('mobile'),
          data['dept_id'], data['location_id'], data.get('position'), data.get('job_title'),
          data.get('hire_date'), data.get('resign_date'), data.get('is_active', 1), data.get('role', 'user'), id))
    conn.commit()
    conn.close()
    return api_response(message="사용자 수정 완료")

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db()
    conn.execute('UPDATE User SET is_active = 0, resign_date = DATE("now"), updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="사용자 비활성화 완료")

@app.route('/api/users/<int:id>/assets', methods=['GET'])
def get_user_assets(id):
    conn = get_db()
    rows = conn.execute('''
        SELECT a.*, c.category_name, l.location_name
        FROM Asset a
        JOIN AssetAssignment aa ON a.asset_id = aa.asset_id
        LEFT JOIN AssetCategory c ON a.category_id = c.category_id
        LEFT JOIN Location l ON a.location_id = l.location_id
        WHERE aa.user_id = ? AND aa.is_active = 1 AND a.is_deleted = 0
    ''', (id,)).fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/users/<int:id>/licenses', methods=['GET'])
def get_user_licenses(id):
    conn = get_db()
    rows = conn.execute('''
        SELECT sl.*, la.assigned_date, la.assignment_id
        FROM SoftwareLicense sl
        JOIN LicenseAssignment la ON sl.license_id = la.license_id
        WHERE la.user_id = ? AND la.is_active = 1 AND sl.is_deleted = 0
    ''', (id,)).fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/users/<int:id>/bulk-return', methods=['POST'])
def bulk_return_user(id):
    """일괄 회수 - 퇴직 시나리오"""
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    # 자산 회수
    cursor.execute('''
        UPDATE AssetAssignment SET is_active = 0, returned_date = ? WHERE user_id = ? AND is_active = 1
    ''', (today, id))
    asset_count = cursor.rowcount
    
    # 자산 상태 변경
    cursor.execute('''
        UPDATE Asset SET asset_status = '여유', current_user_id = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE asset_id IN (SELECT asset_id FROM AssetAssignment WHERE user_id = ? AND returned_date = ?)
    ''', (id, today))
    
    # 라이선스 회수
    cursor.execute('''
        UPDATE LicenseAssignment SET is_active = 0, revoked_date = ? WHERE user_id = ? AND is_active = 1
    ''', (today, id))
    license_count = cursor.rowcount
    
    # 라이선스 수량 업데이트
    cursor.execute('''
        UPDATE SoftwareLicense SET 
            used_quantity = (SELECT COUNT(*) FROM LicenseAssignment WHERE license_id = SoftwareLicense.license_id AND is_active = 1),
            available_quantity = total_quantity - (SELECT COUNT(*) FROM LicenseAssignment WHERE license_id = SoftwareLicense.license_id AND is_active = 1),
            compliance_status = CASE 
                WHEN total_quantity >= (SELECT COUNT(*) FROM LicenseAssignment WHERE license_id = SoftwareLicense.license_id AND is_active = 1) THEN '정상'
                ELSE '초과' END,
            updated_at = CURRENT_TIMESTAMP
    ''')
    
    # 사용자 비활성화
    cursor.execute('UPDATE User SET is_active = 0, resign_date = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (today, id))
    
    conn.commit()
    conn.close()
    return api_response(message=f"일괄 회수 완료: 자산 {asset_count}건, 라이선스 {license_count}건")

# ========================================
# Category API (카테고리)
# ========================================
@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    rows = conn.execute('''
        SELECT c.*, p.category_name as parent_category_name
        FROM AssetCategory c
        LEFT JOIN AssetCategory p ON c.parent_category_id = p.category_id
        WHERE c.is_active = 1
        ORDER BY c.category_level, c.category_id
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO AssetCategory (category_code, category_name, category_level, parent_category_id, asset_type, useful_life_months)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['category_code'], data['category_name'], data['category_level'],
              data.get('parent_category_id'), data['asset_type'], data.get('useful_life_months')))
        conn.commit()
        return api_response(data={"category_id": cursor.lastrowid}, message="카테고리 등록 완료", status=201)
    except sqlite3.IntegrityError as e:
        return api_response(False, message=str(e), status=400)
    finally:
        conn.close()

@app.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM AssetCategory WHERE category_id = ?', (id,)).fetchone()
    conn.close()
    if row:
        return api_response(data=dict(row))
    return api_response(False, message="카테고리를 찾을 수 없습니다", status=404)

@app.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE AssetCategory SET category_code=?, category_name=?, category_level=?, parent_category_id=?, 
                                  asset_type=?, useful_life_months=?
        WHERE category_id=?
    ''', (data['category_code'], data['category_name'], data['category_level'],
          data.get('parent_category_id'), data['asset_type'], data.get('useful_life_months'), id))
    conn.commit()
    conn.close()
    return api_response(message="카테고리 수정 완료")

@app.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    conn = get_db()
    conn.execute('UPDATE AssetCategory SET is_active = 0 WHERE category_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="카테고리 비활성화 완료")

# ========================================
# Vendor API (공급업체)
# ========================================
@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    conn = get_db()
    rows = conn.execute('SELECT * FROM Vendor WHERE is_active = 1').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/vendors', methods=['POST'])
def create_vendor():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Vendor (vendor_name, vendor_type, contact_name, contact_phone, contact_email, contract_info)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['vendor_name'], data['vendor_type'], data.get('contact_name'),
          data.get('contact_phone'), data.get('contact_email'), data.get('contract_info')))
    conn.commit()
    conn.close()
    return api_response(data={"vendor_id": cursor.lastrowid}, message="공급업체 등록 완료", status=201)

@app.route('/api/vendors/<int:id>', methods=['PUT'])
def update_vendor(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE Vendor SET vendor_name=?, vendor_type=?, contact_name=?, contact_phone=?, contact_email=?, contract_info=?
        WHERE vendor_id=?
    ''', (data['vendor_name'], data['vendor_type'], data.get('contact_name'),
          data.get('contact_phone'), data.get('contact_email'), data.get('contract_info'), id))
    conn.commit()
    conn.close()
    return api_response(message="공급업체 수정 완료")

@app.route('/api/vendors/<int:id>', methods=['DELETE'])
def delete_vendor(id):
    conn = get_db()
    conn.execute('UPDATE Vendor SET is_active = 0 WHERE vendor_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="공급업체 비활성화 완료")

# ========================================
# EOS Info API
# ========================================
@app.route('/api/eos-info', methods=['GET'])
def get_eos_info():
    conn = get_db()
    rows = conn.execute('SELECT * FROM EOSInfo ORDER BY eos_date').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/eos-info', methods=['POST'])
def create_eos_info():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO EOSInfo (product_name, product_type, vendor, mainstream_end, extended_end, eos_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['product_name'], data['product_type'], data.get('vendor'),
          data.get('mainstream_end'), data.get('extended_end'), data['eos_date'], data.get('notes')))
    conn.commit()
    conn.close()
    return api_response(data={"eos_id": cursor.lastrowid}, message="EOS 정보 등록 완료", status=201)

@app.route('/api/eos-info/<int:id>', methods=['PUT'])
def update_eos_info(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE EOSInfo SET product_name=?, product_type=?, vendor=?, mainstream_end=?, extended_end=?, eos_date=?, notes=?
        WHERE eos_id=?
    ''', (data['product_name'], data['product_type'], data.get('vendor'),
          data.get('mainstream_end'), data.get('extended_end'), data['eos_date'], data.get('notes'), id))
    conn.commit()
    conn.close()
    return api_response(message="EOS 정보 수정 완료")

@app.route('/api/eos-info/<int:id>', methods=['DELETE'])
def delete_eos_info(id):
    conn = get_db()
    conn.execute('DELETE FROM EOSInfo WHERE eos_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="EOS 정보 삭제 완료")

# ========================================
# Asset API (자산)
# ========================================
def generate_asset_number(conn, location_code, category_code):
    year = datetime.now().year
    prefix = f"{location_code}-{category_code}-{year}"
    row = conn.execute("SELECT asset_number FROM Asset WHERE asset_number LIKE ? ORDER BY asset_number DESC LIMIT 1", (f"{prefix}-%",)).fetchone()
    if row:
        last_num = int(row['asset_number'].split('-')[-1])
        return f"{prefix}-{str(last_num + 1).zfill(4)}"
    return f"{prefix}-0001"

@app.route('/api/assets', methods=['GET'])
def get_assets():
    conn = get_db()
    location_id = request.args.get('location_id')
    category_id = request.args.get('category_id')
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    
    query = '''
        SELECT a.*, c.category_name, c.category_code, c.asset_type, l.location_name, l.location_code,
               u.user_name as current_user_name, m.user_name as manager_name, e.product_name as eos_product_name
        FROM Asset a
        LEFT JOIN AssetCategory c ON a.category_id = c.category_id
        LEFT JOIN Location l ON a.location_id = l.location_id
        LEFT JOIN User u ON a.current_user_id = u.user_id
        LEFT JOIN User m ON a.asset_manager_id = m.user_id
        LEFT JOIN EOSInfo e ON a.eos_id = e.eos_id
        WHERE a.is_deleted = 0
    '''
    params = []
    if location_id:
        query += ' AND a.location_id = ?'
        params.append(location_id)
    if category_id:
        query += ' AND a.category_id = ?'
        params.append(category_id)
    if status:
        query += ' AND a.asset_status = ?'
        params.append(status)
    if keyword:
        query += ' AND (a.asset_number LIKE ? OR a.asset_name LIKE ? OR a.serial_number LIKE ? OR a.ip_address LIKE ?)'
        kw = f'%{keyword}%'
        params.extend([kw, kw, kw, kw])
    query += ' ORDER BY a.asset_id DESC'
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/assets', methods=['POST'])
def create_asset():
    data = request.json
    conn = get_db()
    try:
        cursor = conn.cursor()
        loc = conn.execute('SELECT location_code FROM Location WHERE location_id = ?', (data['location_id'],)).fetchone()
        cat = conn.execute('SELECT category_code, useful_life_months FROM AssetCategory WHERE category_id = ?', (data['category_id'],)).fetchone()
        asset_number = data.get('asset_number') or generate_asset_number(conn, loc['location_code'], cat['category_code'])
        useful_life = data.get('useful_life_months') or cat['useful_life_months']
        
        cursor.execute('''
            INSERT INTO Asset (asset_number, asset_name, category_id, asset_status, location_id, install_location,
                              manufacturer, model_name, serial_number, specifications, purchase_date, purchase_cost,
                              purchase_vendor_id, warranty_start, warranty_end, useful_life_months, current_user_id,
                              asset_manager_id, sub_manager_id, ip_address, mac_address, hostname, os_info, eos_id,
                              notes, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (asset_number, data['asset_name'], data['category_id'], data.get('asset_status', '신규'),
              data['location_id'], data.get('install_location'), data.get('manufacturer'), data.get('model_name'),
              data.get('serial_number'), json.dumps(data.get('specifications', {}), ensure_ascii=False) if data.get('specifications') else None,
              data.get('purchase_date'), data.get('purchase_cost'), data.get('purchase_vendor_id'),
              data.get('warranty_start'), data.get('warranty_end'), useful_life, data.get('current_user_id'),
              data['asset_manager_id'], data.get('sub_manager_id'), data.get('ip_address'), data.get('mac_address'),
              data.get('hostname'), data.get('os_info'), data.get('eos_id'), data.get('notes'), 1, 1))
        asset_id = cursor.lastrowid
        log_history(conn, 'ASSET', asset_id, 'CREATED', f'자산 등록: {asset_number}', None, data, 1)
        conn.commit()
        return api_response(data={"asset_id": asset_id, "asset_number": asset_number}, message="자산 등록 완료", status=201)
    except Exception as e:
        return api_response(False, message=str(e), status=400)
    finally:
        conn.close()

@app.route('/api/assets/<int:id>', methods=['GET'])
def get_asset(id):
    conn = get_db()
    row = conn.execute('''
        SELECT a.*, c.category_name, c.asset_type, l.location_name, u.user_name as current_user_name,
               m.user_name as manager_name, e.product_name as eos_product_name, e.eos_date
        FROM Asset a
        LEFT JOIN AssetCategory c ON a.category_id = c.category_id
        LEFT JOIN Location l ON a.location_id = l.location_id
        LEFT JOIN User u ON a.current_user_id = u.user_id
        LEFT JOIN User m ON a.asset_manager_id = m.user_id
        LEFT JOIN EOSInfo e ON a.eos_id = e.eos_id
        WHERE a.asset_id = ?
    ''', (id,)).fetchone()
    conn.close()
    return api_response(data=row_to_dict(row)) if row else api_response(False, message="자산 없음", status=404)

@app.route('/api/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    data = request.json
    conn = get_db()
    old = conn.execute('SELECT * FROM Asset WHERE asset_id = ?', (id,)).fetchone()
    conn.execute('''
        UPDATE Asset SET asset_name=?, category_id=?, asset_status=?, location_id=?, install_location=?,
                        manufacturer=?, model_name=?, serial_number=?, specifications=?, purchase_date=?,
                        purchase_cost=?, purchase_vendor_id=?, warranty_start=?, warranty_end=?, useful_life_months=?,
                        asset_manager_id=?, sub_manager_id=?, ip_address=?, mac_address=?, hostname=?, os_info=?,
                        eos_id=?, notes=?, updated_at=CURRENT_TIMESTAMP, updated_by=?
        WHERE asset_id=?
    ''', (data['asset_name'], data['category_id'], data['asset_status'], data['location_id'], data.get('install_location'),
          data.get('manufacturer'), data.get('model_name'), data.get('serial_number'),
          json.dumps(data.get('specifications', {}), ensure_ascii=False) if data.get('specifications') else None,
          data.get('purchase_date'), data.get('purchase_cost'), data.get('purchase_vendor_id'),
          data.get('warranty_start'), data.get('warranty_end'), data.get('useful_life_months'),
          data['asset_manager_id'], data.get('sub_manager_id'), data.get('ip_address'), data.get('mac_address'),
          data.get('hostname'), data.get('os_info'), data.get('eos_id'), data.get('notes'), 1, id))
    log_history(conn, 'ASSET', id, 'UPDATED', '자산 수정', row_to_dict(old), data, 1)
    conn.commit()
    conn.close()
    return api_response(message="자산 수정 완료")

@app.route('/api/assets/<int:id>', methods=['DELETE'])
def delete_asset(id):
    conn = get_db()
    conn.execute('UPDATE Asset SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP WHERE asset_id = ?', (id,))
    log_history(conn, 'ASSET', id, 'DELETED', '자산 논리삭제', None, None, 1)
    conn.commit()
    conn.close()
    return api_response(message="자산 삭제 완료")

@app.route('/api/assets/<int:id>/assign', methods=['POST'])
def assign_asset(id):
    data = request.json
    conn = get_db()
    today = date.today().isoformat()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO AssetAssignment (asset_id, user_id, is_primary, assignment_type, assigned_date, is_active, assigned_by)
        VALUES (?, ?, ?, ?, ?, 1, ?)
    ''', (id, data['user_id'], data.get('is_primary', 1), data.get('assignment_type', '전용'), today, 1))
    conn.execute('UPDATE Asset SET asset_status = ?, current_user_id = ?, assigned_date = ?, updated_at = CURRENT_TIMESTAMP WHERE asset_id = ?',
                 ('사용중', data['user_id'], today, id))
    log_history(conn, 'ASSET', id, 'ASSIGNED', f"자산 배정: user_id={data['user_id']}", None, data, 1)
    conn.commit()
    conn.close()
    return api_response(message="자산 배정 완료")

@app.route('/api/assets/<int:id>/return', methods=['POST'])
def return_asset(id):
    conn = get_db()
    today = date.today().isoformat()
    conn.execute('UPDATE AssetAssignment SET is_active = 0, returned_date = ? WHERE asset_id = ? AND is_active = 1', (today, id))
    conn.execute('UPDATE Asset SET asset_status = ?, current_user_id = NULL, updated_at = CURRENT_TIMESTAMP WHERE asset_id = ?', ('여유', id))
    log_history(conn, 'ASSET', id, 'RETURNED', '자산 회수', None, None, 1)
    conn.commit()
    conn.close()
    return api_response(message="자산 회수 완료")

@app.route('/api/assets/<int:id>/change-status', methods=['POST'])
def change_asset_status(id):
    data = request.json
    conn = get_db()
    old = conn.execute('SELECT asset_status FROM Asset WHERE asset_id = ?', (id,)).fetchone()
    conn.execute('UPDATE Asset SET asset_status = ?, notes = COALESCE(notes, "") || ? || "\n", updated_at = CURRENT_TIMESTAMP WHERE asset_id = ?',
                 (data['new_status'], f"[상태변경] {old['asset_status']} → {data['new_status']}: {data.get('reason', '')}", id))
    log_history(conn, 'ASSET', id, 'STATUS_CHANGED', f"{old['asset_status']} → {data['new_status']}", {'status': old['asset_status']}, {'status': data['new_status']}, 1)
    conn.commit()
    conn.close()
    return api_response(message="상태 변경 완료")

@app.route('/api/assets/<int:id>/history', methods=['GET'])
def get_asset_history(id):
    conn = get_db()
    rows = conn.execute('''
        SELECT h.*, u.user_name as action_by_name
        FROM AssetHistory h LEFT JOIN User u ON h.action_by = u.user_id
        WHERE h.reference_type = 'ASSET' AND h.reference_id = ?
        ORDER BY h.action_date DESC
    ''', (id,)).fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/assets/expired-useful-life', methods=['GET'])
def get_expired_useful_life_assets():
    conn = get_db()
    rows = conn.execute('''
        SELECT a.*, c.category_name, l.location_name, u.user_name as current_user_name
        FROM Asset a
        LEFT JOIN AssetCategory c ON a.category_id = c.category_id
        LEFT JOIN Location l ON a.location_id = l.location_id
        LEFT JOIN User u ON a.current_user_id = u.user_id
        WHERE a.is_deleted = 0 AND a.useful_life_expire_date IS NOT NULL AND a.useful_life_expire_date < DATE('now')
        ORDER BY a.useful_life_expire_date
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/assets/eos-expired', methods=['GET'])
def get_eos_expired_assets():
    conn = get_db()
    rows = conn.execute('''
        SELECT a.*, c.category_name, l.location_name, u.user_name as current_user_name, e.product_name, e.eos_date
        FROM Asset a
        LEFT JOIN AssetCategory c ON a.category_id = c.category_id
        LEFT JOIN Location l ON a.location_id = l.location_id
        LEFT JOIN User u ON a.current_user_id = u.user_id
        LEFT JOIN EOSInfo e ON a.eos_id = e.eos_id
        WHERE a.is_deleted = 0 AND e.eos_date IS NOT NULL AND e.eos_date < DATE('now')
        ORDER BY e.eos_date
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

# ========================================
# License API (라이선스)
# ========================================
def generate_license_number(conn):
    year = datetime.now().year
    prefix = f"HQ-SW-{year}"
    row = conn.execute("SELECT license_number FROM SoftwareLicense WHERE license_number LIKE ? ORDER BY license_number DESC LIMIT 1", (f"{prefix}-%",)).fetchone()
    if row:
        last_num = int(row['license_number'].split('-')[-1])
        return f"{prefix}-{str(last_num + 1).zfill(4)}"
    return f"{prefix}-0001"

@app.route('/api/licenses', methods=['GET'])
def get_licenses():
    conn = get_db()
    rows = conn.execute('''
        SELECT sl.*, c.category_name, v.vendor_name, u.user_name as manager_name
        FROM SoftwareLicense sl
        LEFT JOIN AssetCategory c ON sl.category_id = c.category_id
        LEFT JOIN Vendor v ON sl.vendor_id = v.vendor_id
        LEFT JOIN User u ON sl.license_manager_id = u.user_id
        WHERE sl.is_deleted = 0
        ORDER BY sl.license_id DESC
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/licenses', methods=['POST'])
def create_license():
    data = request.json
    conn = get_db()
    try:
        cursor = conn.cursor()
        license_number = data.get('license_number') or generate_license_number(conn)
        total = data['total_quantity']
        cursor.execute('''
            INSERT INTO SoftwareLicense (license_number, software_name, category_id, vendor_id, version, license_type,
                                         license_metric, license_key, total_quantity, used_quantity, available_quantity,
                                         purchase_date, purchase_cost, subscription_start, subscription_end, is_subscription,
                                         auto_renewal, renewal_cost, parent_license_id, license_manager_id, compliance_status,
                                         alert_days_before, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (license_number, data['software_name'], data['category_id'], data.get('vendor_id'), data.get('version'),
              data['license_type'], data['license_metric'], data.get('license_key'), total, total,
              data.get('purchase_date'), data.get('purchase_cost'), data.get('subscription_start'), data.get('subscription_end'),
              1 if data.get('subscription_end') else 0, data.get('auto_renewal'), data.get('renewal_cost'),
              data.get('parent_license_id'), data['license_manager_id'], '정상', data.get('alert_days_before', 30), data.get('notes')))
        license_id = cursor.lastrowid
        log_history(conn, 'LICENSE', license_id, 'CREATED', f'라이선스 등록: {license_number}', None, data, 1)
        conn.commit()
        return api_response(data={"license_id": license_id, "license_number": license_number}, message="라이선스 등록 완료", status=201)
    except Exception as e:
        return api_response(False, message=str(e), status=400)
    finally:
        conn.close()

@app.route('/api/licenses/<int:id>', methods=['GET'])
def get_license(id):
    conn = get_db()
    row = conn.execute('''
        SELECT sl.*, c.category_name, v.vendor_name, u.user_name as manager_name
        FROM SoftwareLicense sl
        LEFT JOIN AssetCategory c ON sl.category_id = c.category_id
        LEFT JOIN Vendor v ON sl.vendor_id = v.vendor_id
        LEFT JOIN User u ON sl.license_manager_id = u.user_id
        WHERE sl.license_id = ?
    ''', (id,)).fetchone()
    conn.close()
    return api_response(data=row_to_dict(row)) if row else api_response(False, message="라이선스 없음", status=404)

@app.route('/api/licenses/<int:id>', methods=['PUT'])
def update_license(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE SoftwareLicense SET software_name=?, category_id=?, vendor_id=?, version=?, license_type=?,
                                   license_metric=?, license_key=?, total_quantity=?, purchase_date=?, purchase_cost=?,
                                   subscription_start=?, subscription_end=?, is_subscription=?, auto_renewal=?, renewal_cost=?,
                                   parent_license_id=?, license_manager_id=?, alert_days_before=?, notes=?, updated_at=CURRENT_TIMESTAMP
        WHERE license_id=?
    ''', (data['software_name'], data['category_id'], data.get('vendor_id'), data.get('version'), data['license_type'],
          data['license_metric'], data.get('license_key'), data['total_quantity'], data.get('purchase_date'),
          data.get('purchase_cost'), data.get('subscription_start'), data.get('subscription_end'),
          1 if data.get('subscription_end') else 0, data.get('auto_renewal'), data.get('renewal_cost'),
          data.get('parent_license_id'), data['license_manager_id'], data.get('alert_days_before', 30), data.get('notes'), id))
    # Recalculate
    conn.execute('''UPDATE SoftwareLicense SET available_quantity = total_quantity - used_quantity,
                    compliance_status = CASE WHEN total_quantity >= used_quantity THEN '정상' ELSE '초과' END WHERE license_id = ?''', (id,))
    conn.commit()
    conn.close()
    return api_response(message="라이선스 수정 완료")

@app.route('/api/licenses/<int:id>', methods=['DELETE'])
def delete_license(id):
    conn = get_db()
    conn.execute('UPDATE SoftwareLicense SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP WHERE license_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="라이선스 삭제 완료")

@app.route('/api/licenses/<int:id>/assignments', methods=['GET'])
def get_license_assignments(id):
    conn = get_db()
    rows = conn.execute('''
        SELECT la.*, u.user_name, u.employee_no, d.dept_name
        FROM LicenseAssignment la
        LEFT JOIN User u ON la.user_id = u.user_id
        LEFT JOIN Department d ON u.dept_id = d.dept_id
        WHERE la.license_id = ? AND la.is_active = 1
    ''', (id,)).fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/licenses/<int:id>/assign', methods=['POST'])
def assign_license(id):
    data = request.json
    conn = get_db()
    today = date.today().isoformat()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO LicenseAssignment (license_id, user_id, asset_id, assigned_date, is_active, assigned_by) VALUES (?, ?, ?, ?, 1, ?)',
                   (id, data.get('user_id'), data.get('asset_id'), today, 1))
    conn.execute('''UPDATE SoftwareLicense SET used_quantity = used_quantity + 1, available_quantity = available_quantity - 1,
                    compliance_status = CASE WHEN available_quantity - 1 >= 0 THEN '정상' ELSE '초과' END, updated_at = CURRENT_TIMESTAMP WHERE license_id = ?''', (id,))
    log_history(conn, 'LICENSE', id, 'LICENSE_ASSIGNED', f"라이선스 할당: user_id={data.get('user_id')}", None, data, 1)
    conn.commit()
    conn.close()
    return api_response(message="라이선스 할당 완료")

@app.route('/api/licenses/<int:id>/revoke', methods=['POST'])
def revoke_license(id):
    data = request.json
    conn = get_db()
    today = date.today().isoformat()
    conn.execute('UPDATE LicenseAssignment SET is_active = 0, revoked_date = ? WHERE assignment_id = ?', (today, data['assignment_id']))
    conn.execute('''UPDATE SoftwareLicense SET used_quantity = used_quantity - 1, available_quantity = available_quantity + 1,
                    compliance_status = CASE WHEN available_quantity + 1 >= 0 THEN '정상' ELSE '초과' END, updated_at = CURRENT_TIMESTAMP WHERE license_id = ?''', (id,))
    log_history(conn, 'LICENSE', id, 'LICENSE_REVOKED', f"라이선스 회수: assignment_id={data['assignment_id']}", None, data, 1)
    conn.commit()
    conn.close()
    return api_response(message="라이선스 회수 완료")

# ========================================
# Inventory API (실사)
# ========================================
@app.route('/api/inventories', methods=['GET'])
def get_inventories():
    conn = get_db()
    rows = conn.execute('''
        SELECT i.*, u.user_name as manager_name, l.location_name, c.category_name
        FROM InventorySchedule i
        LEFT JOIN User u ON i.assigned_manager_id = u.user_id
        LEFT JOIN Location l ON i.target_location_id = l.location_id
        LEFT JOIN AssetCategory c ON i.target_category_id = c.category_id
        ORDER BY i.start_date DESC
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/inventories', methods=['POST'])
def create_inventory():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO InventorySchedule (schedule_name, schedule_type, frequency, start_date, end_date,
                                        target_category_id, target_location_id, assigned_manager_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['schedule_name'], data['schedule_type'], data['frequency'], data['start_date'], data['end_date'],
          data.get('target_category_id'), data.get('target_location_id'), data['assigned_manager_id'], '예정'))
    conn.commit()
    conn.close()
    return api_response(data={"schedule_id": cursor.lastrowid}, message="실사 일정 등록 완료", status=201)

@app.route('/api/inventories/<int:id>', methods=['PUT'])
def update_inventory(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE InventorySchedule SET schedule_name=?, schedule_type=?, frequency=?, start_date=?, end_date=?,
               target_category_id=?, target_location_id=?, assigned_manager_id=?, status=?, updated_at=CURRENT_TIMESTAMP
        WHERE schedule_id=?
    ''', (data['schedule_name'], data['schedule_type'], data['frequency'], data['start_date'], data['end_date'],
          data.get('target_category_id'), data.get('target_location_id'), data['assigned_manager_id'], data['status'], id))
    conn.commit()
    conn.close()
    return api_response(message="실사 일정 수정 완료")

# ========================================
# Dashboard API
# ========================================
@app.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) as cnt FROM Asset WHERE is_deleted = 0').fetchone()['cnt']
    in_use = conn.execute("SELECT COUNT(*) as cnt FROM Asset WHERE is_deleted = 0 AND asset_status = '사용중'").fetchone()['cnt']
    available = conn.execute("SELECT COUNT(*) as cnt FROM Asset WHERE is_deleted = 0 AND asset_status = '여유'").fetchone()['cnt']
    repair = conn.execute("SELECT COUNT(*) as cnt FROM Asset WHERE is_deleted = 0 AND asset_status = '수리중'").fetchone()['cnt']
    pending = conn.execute("SELECT COUNT(*) as cnt FROM Asset WHERE is_deleted = 0 AND asset_status = '폐기예정'").fetchone()['cnt']
    conn.close()
    return api_response(data={"total": total, "in_use": in_use, "available": available, "repair": repair, "pending_disposal": pending})

@app.route('/api/dashboard/by-category', methods=['GET'])
def dashboard_by_category():
    conn = get_db()
    rows = conn.execute('''
        SELECT c.category_name, c.asset_type, COUNT(a.asset_id) as count
        FROM AssetCategory c LEFT JOIN Asset a ON c.category_id = a.category_id AND a.is_deleted = 0
        WHERE c.category_level = 3 AND c.is_active = 1
        GROUP BY c.category_id ORDER BY count DESC
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/dashboard/by-location', methods=['GET'])
def dashboard_by_location():
    conn = get_db()
    rows = conn.execute('''
        SELECT l.location_name, COUNT(a.asset_id) as count
        FROM Location l LEFT JOIN Asset a ON l.location_id = a.location_id AND a.is_deleted = 0
        WHERE l.is_active = 1 GROUP BY l.location_id
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/dashboard/license-status', methods=['GET'])
def dashboard_license_status():
    conn = get_db()
    rows = conn.execute('''
        SELECT software_name, total_quantity, used_quantity, available_quantity, compliance_status, subscription_end
        FROM SoftwareLicense WHERE is_deleted = 0 ORDER BY compliance_status DESC, software_name
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/dashboard/useful-life-expired', methods=['GET'])
def dashboard_useful_life():
    conn = get_db()
    rows = conn.execute('''
        SELECT c.category_name, COUNT(*) as count
        FROM Asset a JOIN AssetCategory c ON a.category_id = c.category_id
        WHERE a.is_deleted = 0 AND a.useful_life_expire_date < DATE('now')
        GROUP BY c.category_id
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/dashboard/eos-status', methods=['GET'])
def dashboard_eos_status():
    conn = get_db()
    rows = conn.execute('''
        SELECT e.product_name, e.eos_date, COUNT(a.asset_id) as count
        FROM EOSInfo e JOIN Asset a ON e.eos_id = a.eos_id
        WHERE a.is_deleted = 0 GROUP BY e.eos_id ORDER BY e.eos_date
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/dashboard/recent-activity', methods=['GET'])
def dashboard_recent_activity():
    conn = get_db()
    rows = conn.execute('''
        SELECT h.*, u.user_name as action_by_name FROM AssetHistory h
        LEFT JOIN User u ON h.action_by = u.user_id ORDER BY h.action_date DESC LIMIT 20
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/dashboard/by-department', methods=['GET'])
def dashboard_by_department():
    conn = get_db()
    rows = conn.execute('''
        SELECT d.dept_name, COUNT(a.asset_id) as count
        FROM Department d LEFT JOIN User u ON d.dept_id = u.dept_id
        LEFT JOIN Asset a ON u.user_id = a.current_user_id AND a.is_deleted = 0
        WHERE d.is_active = 1 GROUP BY d.dept_id ORDER BY count DESC LIMIT 10
    ''').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

# ========================================
# Notification API
# ========================================
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    conn = get_db()
    rows = conn.execute('SELECT * FROM Notification ORDER BY created_at DESC LIMIT 50').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))

@app.route('/api/notifications/<int:id>/read', methods=['PUT'])
def read_notification(id):
    conn = get_db()
    conn.execute('UPDATE Notification SET is_read = 1 WHERE notification_id = ?', (id,))
    conn.commit()
    conn.close()
    return api_response(message="읽음 처리 완료")

@app.route('/api/notifications/read-all', methods=['POST'])
def read_all_notifications():
    conn = get_db()
    conn.execute('UPDATE Notification SET is_read = 1')
    conn.commit()
    conn.close()
    return api_response(message="모두 읽음 처리 완료")

# ========================================
# Config API
# ========================================
@app.route('/api/config', methods=['GET'])
def get_config():
    conn = get_db()
    rows = conn.execute('SELECT * FROM SystemConfig').fetchall()
    conn.close()
    return api_response(data={row['config_key']: row['config_value'] for row in rows})

@app.route('/api/config/<key>', methods=['PUT'])
def update_config(key):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE SystemConfig SET config_value = ?, updated_at = CURRENT_TIMESTAMP WHERE config_key = ?', (data['value'], key))
    conn.commit()
    conn.close()
    return api_response(message="설정 수정 완료")

# ========================================
# Import/Export API
# ========================================
@app.route('/api/assets/import', methods=['POST'])
def import_assets():
    from import_handler import import_hw_assets
    if 'file' not in request.files:
        return api_response(False, message="파일이 없습니다", status=400)
    file = request.files['file']
    try:
        results = import_hw_assets(file.read())
        return api_response(data=results, message=f"Import 완료: 성공 {results['success']}건, 실패 {len(results['errors'])}건")
    except Exception as e:
        return api_response(False, message=str(e), status=500)

@app.route('/api/assets/export', methods=['GET'])
def export_assets():
    from import_handler import export_assets as do_export
    from io import BytesIO
    try:
        content = do_export()
        return send_file(BytesIO(content), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=f'assets_export_{date.today().isoformat()}.xlsx')
    except Exception as e:
        return api_response(False, message=str(e), status=500)

@app.route('/api/assets/import-template/<type>', methods=['GET'])
def get_asset_template(type):
    from import_handler import create_hw_template
    from io import BytesIO
    content = create_hw_template()
    return send_file(BytesIO(content), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=f'template_hw_{type}.xlsx')

@app.route('/api/licenses/import', methods=['POST'])
def import_licenses_api():
    from import_handler import import_licenses
    if 'file' not in request.files:
        return api_response(False, message="파일이 없습니다", status=400)
    file = request.files['file']
    try:
        results = import_licenses(file.read())
        return api_response(data=results, message=f"Import 완료: 성공 {results['success']}건, 실패 {len(results['errors'])}건")
    except Exception as e:
        return api_response(False, message=str(e), status=500)

@app.route('/api/licenses/export', methods=['GET'])
def export_licenses():
    from import_handler import export_licenses as do_export
    from io import BytesIO
    try:
        content = do_export()
        return send_file(BytesIO(content), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=f'licenses_export_{date.today().isoformat()}.xlsx')
    except Exception as e:
        return api_response(False, message=str(e), status=500)

@app.route('/api/licenses/import-template', methods=['GET'])
def get_license_template():
    from import_handler import create_license_template
    from io import BytesIO
    content = create_license_template()
    return send_file(BytesIO(content), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='template_license.xlsx')

@app.route('/api/notifications/generate', methods=['POST'])
def generate_notifications():
    from notification_checker import run_all_checks
    try:
        results = run_all_checks()
        total = sum(results.values())
        return api_response(data=results, message=f"알림 생성 완료: 총 {total}건")
    except Exception as e:
        return api_response(False, message=str(e), status=500)

# ========================================
# Main Entry Point
# ========================================
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 서버 시작 시 알림 체크 실행
    try:
        from notification_checker import run_all_checks
        print("🔔 Checking notifications on startup...")
        run_all_checks()
    except Exception as e:
        print(f"⚠️ Notification check failed: {e}")
    
    app.run(debug=True, port=5000)
