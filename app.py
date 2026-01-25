from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'student_management.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status TEXT DEFAULT 'present',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE(student_id, date)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS leave_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Insert sample students if table is empty
        cursor = conn.execute('SELECT COUNT(*) as count FROM students')
        if cursor.fetchone()['count'] == 0:
            sample_students = [
                ('STU001', 'John Doe', 'john@example.com'),
                ('STU002', 'Jane Smith', 'jane@example.com'),
                ('STU003', 'Mike Johnson', 'mike@example.com')
            ]
            conn.executemany(
                'INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)',
                sample_students
            )
        conn.commit()

# Initialize database on startup
init_db()

# ==================== STUDENT ROUTES ====================

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    with get_db() as conn:
        students = conn.execute('SELECT * FROM students ORDER BY student_id').fetchall()
        return jsonify([dict(s) for s in students])

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get specific student by ID"""
    with get_db() as conn:
        student = conn.execute(
            'SELECT * FROM students WHERE student_id = ?', 
            (student_id,)
        ).fetchone()
        if student:
            return jsonify(dict(student))
        return jsonify({'error': 'Student not found'}), 404

@app.route('/api/students/register', methods=['POST'])
def register_student():
    """Register a new student"""
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')
    email = data.get('email')
    
    if not all([student_id, name, email]):
        return jsonify({'error': 'All fields are required (student_id, name, email)'}), 400
    
    # Validate student ID format (3 letters followed by numbers)
    if not student_id or len(student_id) < 4:
        return jsonify({'error': 'Invalid student ID format'}), 400
    
    try:
        with get_db() as conn:
            # Check if student ID already exists
            existing = conn.execute(
                'SELECT * FROM students WHERE student_id = ?',
                (student_id,)
            ).fetchone()
            
            if existing:
                return jsonify({'error': 'Student ID already exists'}), 400
            
            # Check if email already exists
            existing_email = conn.execute(
                'SELECT * FROM students WHERE email = ?',
                (email,)
            ).fetchone()
            
            if existing_email:
                return jsonify({'error': 'Email already registered'}), 400
            
            conn.execute(
                'INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)',
                (student_id.upper(), name, email)
            )
            conn.commit()
            
            return jsonify({
                'message': 'Student registered successfully',
                'student': {
                    'student_id': student_id.upper(),
                    'name': name,
                    'email': email
                }
            }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student (optional endpoint)"""
    try:
        with get_db() as conn:
            # Check if student exists
            student = conn.execute(
                'SELECT * FROM students WHERE student_id = ?',
                (student_id,)
            ).fetchone()
            
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            # Delete student and related records
            conn.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
            conn.execute('DELETE FROM leave_applications WHERE student_id = ?', (student_id,))
            conn.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            conn.commit()
            
            return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ATTENDANCE ROUTES ====================

@app.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance for a student"""
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400
    
    today = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')
    
    try:
        with get_db() as conn:
            # Check if student exists
            student = conn.execute(
                'SELECT * FROM students WHERE student_id = ?',
                (student_id,)
            ).fetchone()
            
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            # Check if attendance already marked today
            existing = conn.execute(
                'SELECT * FROM attendance WHERE student_id = ? AND date = ?',
                (student_id, today)
            ).fetchone()
            
            if existing:
                return jsonify({'error': 'Attendance already marked for today'}), 400
            
            conn.execute(
                'INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)',
                (student_id, today, current_time)
            )
            conn.commit()
            
            return jsonify({
                'message': 'Attendance marked successfully',
                'student_id': student_id,
                'student_name': student['name'],
                'date': today,
                'time': current_time
            }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/<student_id>', methods=['GET'])
def get_attendance(student_id):
    """Get attendance history for a specific student"""
    with get_db() as conn:
        # Check if student exists
        student = conn.execute(
            'SELECT * FROM students WHERE student_id = ?',
            (student_id,)
        ).fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        attendance = conn.execute(
            'SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC',
            (student_id,)
        ).fetchall()
        return jsonify([dict(a) for a in attendance])

@app.route('/api/attendance/all', methods=['GET'])
def get_all_attendance():
    """Get all attendance records"""
    with get_db() as conn:
        attendance = conn.execute(
            '''SELECT a.*, s.name 
               FROM attendance a
               JOIN students s ON a.student_id = s.student_id
               ORDER BY a.date DESC, a.time DESC'''
        ).fetchall()
        return jsonify([dict(a) for a in attendance])

@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance records"""
    today = datetime.now().strftime('%Y-%m-%d')
    with get_db() as conn:
        attendance = conn.execute(
            '''SELECT a.*, s.name 
               FROM attendance a
               JOIN students s ON a.student_id = s.student_id
               WHERE a.date = ?
               ORDER BY a.time ASC''',
            (today,)
        ).fetchall()
        return jsonify([dict(a) for a in attendance])

# ==================== LEAVE APPLICATION ROUTES ====================

@app.route('/api/leave/apply', methods=['POST'])
def apply_leave():
    """Submit a leave application"""
    data = request.json
    student_id = data.get('student_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    reason = data.get('reason')
    
    if not all([student_id, start_date, end_date, reason]):
        return jsonify({'error': 'All fields are required (student_id, start_date, end_date, reason)'}), 400
    
    try:
        with get_db() as conn:
            # Check if student exists
            student = conn.execute(
                'SELECT * FROM students WHERE student_id = ?',
                (student_id,)
            ).fetchone()
            
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            conn.execute(
                '''INSERT INTO leave_applications 
                   (student_id, start_date, end_date, reason) 
                   VALUES (?, ?, ?, ?)''',
                (student_id, start_date, end_date, reason)
            )
            conn.commit()
            
            return jsonify({
                'message': 'Leave application submitted successfully',
                'student_name': student['name'],
                'status': 'pending'
            }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leave/<student_id>', methods=['GET'])
def get_leave_applications(student_id):
    """Get leave applications for a specific student"""
    with get_db() as conn:
        # Check if student exists
        student = conn.execute(
            'SELECT * FROM students WHERE student_id = ?',
            (student_id,)
        ).fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        leaves = conn.execute(
            '''SELECT * FROM leave_applications 
               WHERE student_id = ? 
               ORDER BY applied_at DESC''',
            (student_id,)
        ).fetchall()
        return jsonify([dict(l) for l in leaves])

@app.route('/api/leave/all', methods=['GET'])
def get_all_leave_applications():
    """Get all leave applications"""
    with get_db() as conn:
        leaves = conn.execute(
            '''SELECT la.*, s.name 
               FROM leave_applications la
               JOIN students s ON la.student_id = s.student_id
               ORDER BY la.applied_at DESC'''
        ).fetchall()
        return jsonify([dict(l) for l in leaves])

@app.route('/api/leave/<int:leave_id>/status', methods=['PUT'])
def update_leave_status(leave_id):
    """Update leave application status (approve/reject)"""
    data = request.json
    status = data.get('status')
    
    if status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status. Must be pending, approved, or rejected'}), 400
    
    try:
        with get_db() as conn:
            # Check if leave application exists
            leave = conn.execute(
                'SELECT * FROM leave_applications WHERE id = ?',
                (leave_id,)
            ).fetchone()
            
            if not leave:
                return jsonify({'error': 'Leave application not found'}), 404
            
            conn.execute(
                'UPDATE leave_applications SET status = ? WHERE id = ?',
                (status, leave_id)
            )
            conn.commit()
            
            return jsonify({
                'message': f'Leave application {status}',
                'leave_id': leave_id,
                'status': status
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== STATISTICS ROUTES ====================

@app.route('/api/stats/student/<student_id>', methods=['GET'])
def get_student_stats(student_id):
    """Get statistics for a specific student"""
    with get_db() as conn:
        student = conn.execute(
            'SELECT * FROM students WHERE student_id = ?',
            (student_id,)
        ).fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Count attendance
        attendance_count = conn.execute(
            'SELECT COUNT(*) as count FROM attendance WHERE student_id = ?',
            (student_id,)
        ).fetchone()['count']
        
        # Count leave applications
        leave_count = conn.execute(
            'SELECT COUNT(*) as count FROM leave_applications WHERE student_id = ?',
            (student_id,)
        ).fetchone()['count']
        
        # Count approved leaves
        approved_leaves = conn.execute(
            'SELECT COUNT(*) as count FROM leave_applications WHERE student_id = ? AND status = ?',
            (student_id, 'approved')
        ).fetchone()['count']
        
        return jsonify({
            'student_id': student_id,
            'name': student['name'],
            'total_attendance': attendance_count,
            'total_leave_applications': leave_count,
            'approved_leaves': approved_leaves
        })

@app.route('/api/stats/overview', methods=['GET'])
def get_overview_stats():
    """Get overall system statistics"""
    with get_db() as conn:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
        total_attendance = conn.execute('SELECT COUNT(*) as count FROM attendance').fetchone()['count']
        total_leaves = conn.execute('SELECT COUNT(*) as count FROM leave_applications').fetchone()['count']
        pending_leaves = conn.execute(
            'SELECT COUNT(*) as count FROM leave_applications WHERE status = ?',
            ('pending',)
        ).fetchone()['count']
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_attendance = conn.execute(
            'SELECT COUNT(*) as count FROM attendance WHERE date = ?',
            (today,)
        ).fetchone()['count']
        
        return jsonify({
            'total_students': total_students,
            'total_attendance_records': total_attendance,
            'total_leave_applications': total_leaves,
            'pending_leave_applications': pending_leaves,
            'attendance_today': today_attendance
        })

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Student Management API'
    })

@app.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return jsonify({
        'message': 'Student Management System API',
        'version': '1.0.0',
        'endpoints': {
            'students': '/api/students',
            'register': '/api/students/register',
            'attendance': '/api/attendance',
            'leave': '/api/leave',
            'stats': '/api/stats',
            'health': '/health'
        }
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
