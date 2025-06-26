"""Security Enhancements Module for Atlas Enterprise Features.

This module implements advanced security features such as encryption for data at rest,
multi-factor authentication, and enhanced audit logging for compliance
for multi-user workspace implementation (ENT-003).
"""

from typing import Dict, Optional
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, make_response
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityEnhancements:
    def __init__(self, app: Flask, key_file: str = 'encryption_key.key', audit_file: str = 'audit_logs.json'):
        self.app = app
        self.key_file = key_file
        self.audit_file = audit_file
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'mysecretkey')
        self.encryption_key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.audit_logs: Dict[str, list] = {}
        self.mfa_secrets: Dict[str, str] = {}
        self.load_audit_logs()
        self.setup_routes()

    def load_or_generate_key(self) -> bytes:
        """Load encryption key from file or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data using Fernet symmetric encryption."""
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption."""
        return self.cipher_suite.decrypt(encrypted_data).decode()

    def hash_password(self, password: str) -> bytes:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def check_password(self, password: str, hashed: bytes) -> bool:
        """Check if a password matches the hashed value using bcrypt."""
        return bcrypt.checkpw(password.encode(), hashed)

    def setup_mfa(self, user_id: str, secret: str) -> bool:
        """Setup multi-factor authentication secret for a user."""
        if user_id in self.mfa_secrets:
            return False
        self.mfa_secrets[user_id] = secret
        return True

    def verify_mfa(self, user_id: str, code: str) -> bool:
        """Verify multi-factor authentication code for a user."""
        # Placeholder for MFA verification logic
        # In a real implementation, this would interact with an MFA service or library
        if user_id not in self.mfa_secrets:
            return False
        # Simplified check - in reality, this would involve time-based codes or similar
        return self.mfa_secrets[user_id] == code

    def log_audit_event(self, user_id: str, event_type: str, details: Dict) -> None:
        """Log an audit event for compliance and monitoring."""
        if user_id not in self.audit_logs:
            self.audit_logs[user_id] = []
        
        event = {
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.audit_logs[user_id].append(event)
        self.save_audit_logs()

    def load_audit_logs(self) -> None:
        """Load audit logs from file."""
        try:
            if os.path.exists(self.audit_file):
                with open(self.audit_file, 'r') as f:
                    self.audit_logs = json.load(f)
        except Exception as e:
            print(f"Error loading audit logs: {e}")
            self.audit_logs = {}

    def save_audit_logs(self) -> None:
        """Save audit logs to file."""
        try:
            with open(self.audit_file, 'w') as f:
                json.dump(self.audit_logs, f, indent=2)
        except Exception as e:
            print(f"Error saving audit logs: {e}")

    def get_audit_logs(self, user_id: Optional[str] = None, event_type: Optional[str] = None) -> Dict[str, list]:
        """Get audit logs, optionally filtered by user or event type."""
        if user_id and event_type:
            if user_id in self.audit_logs:
                return {user_id: [log for log in self.audit_logs[user_id] if log['event_type'] == event_type]}
            return {user_id: []}
        elif user_id:
            return {user_id: self.audit_logs.get(user_id, [])}
        elif event_type:
            filtered_logs = {}
            for uid, logs in self.audit_logs.items():
                matching_logs = [log for log in logs if log['event_type'] == event_type]
                if matching_logs:
                    filtered_logs[uid] = matching_logs
            return filtered_logs
        return self.audit_logs

    def setup_routes(self):
        """Setup Flask routes for security enhancements."""
        @self.app.route('/api/security/encrypt', methods=['POST'])
        def encrypt_data_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                jwt.decode(token, self.secret_key, algorithms=['HS256'])
                data = request.get_json() if request.is_json else {}
                content = data.get('content')
                if not content:
                    return make_response(jsonify({'error': 'Missing content field'}), 400)
                
                encrypted = self.encrypt_data(content)
                return jsonify({'encrypted_data': encrypted.decode()})
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/security/decrypt', methods=['POST'])
        def decrypt_data_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                jwt.decode(token, self.secret_key, algorithms=['HS256'])
                data = request.get_json() if request.is_json else {}
                encrypted_data = data.get('encrypted_data')
                if not encrypted_data:
                    return make_response(jsonify({'error': 'Missing encrypted_data field'}), 400)
                
                decrypted = self.decrypt_data(encrypted_data.encode())
                return jsonify({'decrypted_data': decrypted})
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token or data: {str(e)}'}), 401)

        @self.app.route('/api/security/mfa/setup', methods=['POST'])
        def setup_mfa_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                user_id = decoded.get('user')
                if not user_id:
                    return make_response(jsonify({'error': 'Invalid token payload'}), 401)

                data = request.get_json() if request.is_json else {}
                secret = data.get('secret')
                if not secret:
                    return make_response(jsonify({'error': 'Missing secret field'}), 400)
                
                if self.setup_mfa(user_id, secret):
                    return jsonify({'message': f'MFA setup for user {user_id}'})
                return make_response(jsonify({'error': f'MFA already setup for user {user_id}'}), 409)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/security/mfa/verify', methods=['POST'])
        def verify_mfa_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                user_id = decoded.get('user')
                if not user_id:
                    return make_response(jsonify({'error': 'Invalid token payload'}), 401)

                data = request.get_json() if request.is_json else {}
                code = data.get('code')
                if not code:
                    return make_response(jsonify({'error': 'Missing code field'}), 400)
                
                if self.verify_mfa(user_id, code):
                    return jsonify({'message': 'MFA verified', 'verified': True})
                return make_response(jsonify({'message': 'MFA verification failed', 'verified': False}), 403)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/security/audit/log', methods=['POST'])
        def log_audit_event_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                user_id = decoded.get('user')
                if not user_id:
                    return make_response(jsonify({'error': 'Invalid token payload'}), 401)

                data = request.get_json() if request.is_json else {}
                event_type = data.get('event_type')
                details = data.get('details', {})
                if not event_type:
                    return make_response(jsonify({'error': 'Missing event_type field'}), 400)
                
                self.log_audit_event(user_id, event_type, details)
                return jsonify({'message': f'Audit event logged for user {user_id}'})
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/security/audit/logs', methods=['GET'])
        def get_audit_logs_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                user_role = decoded.get('role')
                if user_role != 'admin':
                    return make_response(jsonify({'error': 'Admin access required'}), 403)

                user_id = request.args.get('user_id')
                event_type = request.args.get('event_type')
                logs = self.get_audit_logs(user_id, event_type)
                return jsonify(logs)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)
