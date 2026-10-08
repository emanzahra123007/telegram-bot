import json
import os
from datetime import datetime

class DeviceDatabase:
    def __init__(self):
        self.db_file = "devices.json"
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({}, f)
    
    def get_devices(self, user_id):
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
            return data.get(str(user_id), [])
        except:
            return []
    
    def get_device(self, device_id):
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
            
            for user_devices in data.values():
                for device in user_devices:
                    if device.get('device_id') == device_id:
                        return device
            return None
        except:
            return None
    
    def update_device(self, device_data):
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
            
            user_id = device_data.get('user_id')
            device_id = device_data.get('device_id')
            
            if user_id not in data:
                data[user_id] = []
            
            # Update existing or add new device
            found = False
            for i, dev in enumerate(data[user_id]):
                if dev.get('device_id') == device_id:
                    data[user_id][i] = {**dev, **device_data, 'last_seen': datetime.now().isoformat()}
                    found = True
                    break
            
            if not found:
                device_data['last_seen'] = datetime.now().isoformat()
                data[user_id].append(device_data)
            
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
