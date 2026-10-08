import sqlite3
import json
from datetime import datetime

class DeviceDatabase:
    def __init__(self, db_path='devices.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                model TEXT,
                android_version TEXT,
                battery TEXT,
                location TEXT,
                last_seen TEXT,
                data TEXT
            )
        ''')
        self.conn.commit()
    
    def update_device(self, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (device_id, user_id, name, model, android_version, battery, location, last_seen, data) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('device_id'),
            data.get('user_id'),
            data.get('name'),
            data.get('model'),
            data.get('android_version'),
            data.get('battery'),
            json.dumps(data.get('location', {})),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            json.dumps(data)
        ))
        self.conn.commit()
    
    def get_device(self, device_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'device_id': row[0],
                'user_id': row[1],
                'name': row[2],
                'model': row[3],
                'android_version': row[4],
                'battery': row[5],
                'location': json.loads(row[6]) if row[6] else {},
                'last_seen': row[7],
                'data': json.loads(row[8]) if row[8] else {}
            }
        return None
    
    def get_devices(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE user_id = ?', (str(user_id),))
        rows = cursor.fetchall()
        
        devices = []
        for row in rows:
            devices.append({
                'device_id': row[0],
                'user_id': row[1],
                'name': row[2],
                'model': row[3],
                'android_version': row[4],
                'battery': row[5],
                'location': json.loads(row[6]) if row[6] else {},
                'last_seen': row[7]
            })
        return devices
