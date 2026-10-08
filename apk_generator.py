import os
import json
import hashlib
from datetime import datetime

class APKGenerator:
    def __init__(self):
        self.apk_storage = "generated_apks"
        if not os.path.exists(self.apk_storage):
            os.makedirs(self.apk_storage)
    
    def generate_apk(self, apk_name, user_id):
        """
        اصل APK فائل generate کرتا ہے
        """
        # APK file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # safe filename - space hata diya
        safe_apk_name = "".join(c for c in apk_name if c.isalnum() or c in ('-', '_')).strip()
        filename = f"{user_id}_{safe_apk_name}_{timestamp}.apk"
        filepath = os.path.join(self.apk_storage, filename)
        
        # For now, creating a dummy APK file
        with open(filepath, 'wb') as f:
            f.write(b"Dummy APK Content - Replace with actual APK build process")
        
        # Download link (آپ اپنا domain استعمال کریں)
        download_link = f"https://your-server.com/download/{filename}"
        
        # Save generation record
        self.save_generation_record(user_id, apk_name, download_link)
        
        return download_link
    
    def save_generation_record(self, user_id, apk_name, download_link):
        record = {
            'user_id': user_id,
            'apk_name': apk_name,
            'download_link': download_link,
            'generated_at': datetime.now().isoformat()
        }
        
        record_file = "apk_generation_log.json"
        records = []
        
        if os.path.exists(record_file):
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        records = json.loads(content)
            except (json.JSONDecodeError, FileNotFoundError):
                records = [] # agar file khali ya kharab ho to nayi list
        
        records.append(record)
        
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2)
