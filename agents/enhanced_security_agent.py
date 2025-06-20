#!/usr/bin/env python3
"""
Enhanced Security Agent for Atlas

Monitors sensitive operations and provides security controls.
"""

import os
import re
import hashlib
import json
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
import multiprocessing
import logging

from agents.base_agent import BaseAgent


class SecurityRisk:
    """Represents a security risk assessment."""
    
    def __init__(self, risk_type: str, level: str, description: str, 
                 file_path: Optional[str] = None, command: Optional[str] = None):
        self.risk_type = risk_type  #'file_access', 'system_command', 'network', etc.
        self.level = level  #'Low', 'Medium', 'High', 'Critical'
        self.description = description
        self.file_path = file_path
        self.command = command
        self.timestamp = datetime.now()
        self.id = hashlib.md5(f"{risk_type}{description}{time.time()}".encode()).hexdigest()[:8]


class EnhancedSecurityAgent(BaseAgent):
    """Enhanced Security Agent that monitors and controls sensitive operations."""
    
    def __init__(self, connection=None, config_manager=None):
        super().__init__("EnhancedSecurityAgent", connection)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        #Security settings
        self.settings = {
            'file_access_threshold': 'Medium',
            'system_cmd_threshold': 'High',
            'network_threshold': 'Medium',
            'restricted_directories': [
                '/etc', '/usr/bin', '/System', '/Windows/System32',
                '/var', '/boot', '/root'
            ],
            'dangerous_commands': [
                'rm -rf', 'del', 'format', 'sudo rm', 'sudo chmod 777',
                'chmod 777', 'kill -9', 'killall', 'shutdown', 'reboot'
            ],
            'enable_real_time_monitoring': True,
            'auto_block_critical': True,
            'log_all_operations': True
        }
        
        #Monitoring state
        self.is_monitoring = False
        self.monitored_processes: Set[int] = set()
        self.file_access_log: List[Dict] = []
        self.security_violations: List[SecurityRisk] = []
        self.whitelist_patterns: List[str] = []
        
        #Load settings if config manager is available
        if self.config_manager:
            self.load_security_settings()
        
        #Start monitoring thread
        self.monitoring_thread = None
        
    def load_security_settings(self):
        """Load security settings from configuration."""
        try:
            config = self.config_manager.load()
            
            self.settings.update({
                'file_access_threshold': config.get('file_access_threshold', 'Medium'),
                'system_cmd_threshold': config.get('system_cmd_threshold', 'High'),
                'network_threshold': config.get('network_threshold', 'Medium'),
                'restricted_directories': config.get('restricted_directories', self.settings['restricted_directories']),
                'enable_security_agent': config.get('enable_security_agent', True)
            })
        except Exception as e:
            self.logger.error(f"Failed to load security settings: {e}")
    
    def start_monitoring(self):
        """Start security monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            self.logger.info("Security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Security monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                #Monitor for suspicious activity
                self._check_running_processes()
                self._check_recent_file_access()
                self._check_network_connections()
                
                time.sleep(1)  #Check every second
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  #Wait longer on error
    
    def assess_file_access_risk(self, file_path: str, operation: str = "read") -> SecurityRisk:
        """Assess risk level for file access operation."""
        file_path = os.path.abspath(file_path)
        
        #Check if file is in restricted directories
        for restricted_dir in self.settings['restricted_directories']:
            if file_path.startswith(restricted_dir):
                return SecurityRisk(
                    'file_access',
                    'Critical',
                    f"Attempting to {operation} file in restricted directory: {restricted_dir}",
                    file_path=file_path
                )
        
        #Check for sensitive file types
        sensitive_patterns = [
            r'\.password$', r'\.key$', r'\.pem$', r'\.p12$', r'\.pfx$',
            r'id_rsa', r'id_dsa', r'id_ecdsa', r'id_ed25519',
            r'\.env$', r'\.secrets$', r'config\.ini$'
        ]
        
        filename = os.path.basename(file_path).lower()
        for pattern in sensitive_patterns:
            if re.search(pattern, filename):
                return SecurityRisk(
                    'file_access',
                    'High',
                    f"Attempting to {operation} sensitive file: {filename}",
                    file_path=file_path
                )
        
        #Check for system files
        system_patterns = [
            r'/bin/', r'/sbin/', r'/usr/bin/', r'/usr/sbin/',
            r'System32', r'SysWOW64', r'\.exe$', r'\.dll$', r'\.sys$'
        ]
        
        for pattern in system_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return SecurityRisk(
                    'file_access',
                    'Medium',
                    f"Attempting to {operation} system file",
                    file_path=file_path
                )
        
        #Check for write operations to important directories
        if operation in ['write', 'delete', 'modify']:
            important_dirs = ['/usr', '/opt', '/Library', 'Program Files']
            for important_dir in important_dirs:
                if file_path.startswith(important_dir):
                    return SecurityRisk(
                        'file_access',
                        'Medium',
                        f"Attempting to {operation} file in important directory",
                        file_path=file_path
                    )
        
        return SecurityRisk('file_access', 'Low', f"Normal file {operation}", file_path=file_path)
    
    def assess_command_risk(self, command: str) -> SecurityRisk:
        """Assess risk level for system command execution."""
        command_lower = command.lower().strip()
        
        #Check for dangerous commands
        for dangerous_cmd in self.settings['dangerous_commands']:
            if dangerous_cmd.lower() in command_lower:
                return SecurityRisk(
                    'system_command',
                    'Critical',
                    f"Dangerous command detected: {dangerous_cmd}",
                    command=command
                )
        
        #Check for privilege escalation
        privilege_patterns = [
            r'sudo\s+', r'su\s+', r'runas\s+', r'elevate',
            r'net\s+user', r'net\s+localgroup', r'useradd', r'usermod'
        ]
        
        for pattern in privilege_patterns:
            if re.search(pattern, command_lower):
                return SecurityRisk(
                    'system_command',
                    'High',
                    "Command involves privilege escalation",
                    command=command
                )
        
        #Check for network commands
        network_patterns = [
            r'curl\s+', r'wget\s+', r'nc\s+', r'netcat', r'telnet',
            r'ssh\s+', r'scp\s+', r'rsync\s+', r'ftp\s+'
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, command_lower):
                return SecurityRisk(
                    'system_command',
                    'Medium',
                    "Command involves network communication",
                    command=command
                )
        
        #Check for file manipulation
        file_patterns = [
            r'mv\s+', r'cp\s+', r'copy\s+', r'move\s+',
            r'chmod\s+', r'chown\s+', r'attrib\s+'
        ]
        
        for pattern in file_patterns:
            if re.search(pattern, command_lower):
                return SecurityRisk(
                    'system_command',
                    'Low',
                    "Command involves file manipulation",
                    command=command
                )
        
        return SecurityRisk('system_command', 'Low', "Normal system command", command=command)
    
    def assess_network_risk(self, url: str, operation: str = "request") -> SecurityRisk:
        """Assess risk level for network operations."""
        #Check for suspicious domains
        suspicious_patterns = [
            r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$',  #Free TLDs often used maliciously
            r'bit\.ly', r'tinyurl', r'short',  #URL shorteners
            r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',  #Direct IP addresses
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url.lower()):
                return SecurityRisk(
                    'network',
                    'Medium',
                    f"Suspicious URL pattern detected in {operation}",
                    command=f"{operation}: {url}"
                )
        
        #Check for non-HTTPS connections
        if url.startswith('http://') and not url.startswith('http://localhost'):
            return SecurityRisk(
                'network',
                'Low',
                "Non-HTTPS connection detected",
                command=f"{operation}: {url}"
            )
        
        return SecurityRisk('network', 'Low', f"Normal network {operation}", command=f"{operation}: {url}")
    
    def check_operation_approval(self, risk: SecurityRisk) -> bool:
        """Check if an operation should be approved based on risk level and settings."""
        threshold_map = {
            'Low': 0,
            'Medium': 1,
            'High': 2,
            'Critical': 3
        }
        
        #Get appropriate threshold
        if risk.risk_type == 'file_access':
            threshold = self.settings['file_access_threshold']
        elif risk.risk_type == 'system_command':
            threshold = self.settings['system_cmd_threshold']
        elif risk.risk_type == 'network':
            threshold = self.settings['network_threshold']
        else:
            threshold = 'Medium'  #Default
        
        risk_level = threshold_map.get(risk.level, 0)
        threshold_level = threshold_map.get(threshold, 1)
        
        #Auto-block critical operations if enabled
        if risk.level == 'Critical' and self.settings.get('auto_block_critical', True):
            self.log_security_violation(risk, blocked=True)
            return False
        
        #Allow if risk is below threshold
        if risk_level <= threshold_level:
            return True
        
        #Log the violation
        self.log_security_violation(risk, blocked=False)
        
        #For now, allow but log - in a full implementation, this would prompt user
        return True
    
    def log_security_violation(self, risk: SecurityRisk, blocked: bool = False):
        """Log a security violation."""
        violation = {
            'id': risk.id,
            'timestamp': risk.timestamp.isoformat(),
            'risk_type': risk.risk_type,
            'level': risk.level,
            'description': risk.description,
            'file_path': risk.file_path,
            'command': risk.command,
            'blocked': blocked
        }
        
        self.security_violations.append(risk)
        
        #Log to file if enabled
        if self.settings.get('log_all_operations', True):
            self._write_security_log(violation)
        
        #Send alert for high-risk operations
        if risk.level in ['High', 'Critical']:
            self._send_security_alert(risk, blocked)
    
    def _write_security_log(self, violation: Dict):
        """Write security violation to log file."""
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "security.log")
            with open(log_file, 'a') as f:
                f.write(json.dumps(violation) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write security log: {e}")
    
    def _send_security_alert(self, risk: SecurityRisk, blocked: bool):
        """Send security alert through available channels."""
        alert_message = f"Security Alert: {risk.level} risk {risk.risk_type} operation"
        if blocked:
            alert_message += " (BLOCKED)"
        
        alert_message += f"\nDescription: {risk.description}"
        
        if risk.file_path:
            alert_message += f"\nFile: {risk.file_path}"
        if risk.command:
            alert_message += f"\nCommand: {risk.command}"
        
        #Send through connection if available
        if self.connection:
            try:
                self.connection.send({
                    'type': 'security_alert',
                    'data': {
                        'risk_id': risk.id,
                        'level': risk.level,
                        'message': alert_message,
                        'blocked': blocked
                    }
                })
            except Exception as e:
                self.logger.error(f"Failed to send security alert: {e}")
        
        #Log the alert
        self.logger.warning(alert_message)
    
    def _check_running_processes(self):
        """Check for suspicious running processes."""
        try:
            import psutil
            
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if process.info['pid'] not in self.monitored_processes:
                        self.monitored_processes.add(process.info['pid'])
                        
                        #Check for suspicious process names
                        process_name = process.info['name'].lower()
                        suspicious_names = [
                            'keylogger', 'stealer', 'miner', 'backdoor',
                            'trojan', 'virus', 'malware'
                        ]
                        
                        if any(susp in process_name for susp in suspicious_names):
                            risk = SecurityRisk(
                                'process',
                                'Critical',
                                f"Suspicious process detected: {process_name}",
                                command=str(process.info['cmdline'])
                            )
                            self.log_security_violation(risk)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except ImportError:
            #psutil not available, skip process monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error checking processes: {e}")
    
    def _check_recent_file_access(self):
        """Check for recent file access patterns."""
        #This would integrate with file system monitoring
        #For now, it's a placeholder for future implementation
        pass
    
    def _check_network_connections(self):
        """Check for suspicious network connections."""
        try:
            import psutil
            
            #Try to get network connections with error handling for permission issues
            try:
                connections = psutil.net_connections()
            except psutil.AccessDenied:
                #Skip network monitoring if we don't have permission
                return
            except Exception:
                #Skip for other permission/access issues
                return
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    #Check for connections to suspicious IPs/ports
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    #Check for commonly abused ports
                    suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337]
                    if remote_port in suspicious_ports:
                        risk = SecurityRisk(
                            'network',
                            'High',
                            f"Connection to suspicious port {remote_port}",
                            command=f"Connection to {remote_ip}:{remote_port}"
                        )
                        self.log_security_violation(risk)
                        
        except ImportError:
            #psutil not available, skip network monitoring
            pass
        except Exception as e:
            #Log error only once per session to avoid spam
            if not hasattr(self, '_network_error_logged'):
                self.logger.warning(f"Network monitoring disabled due to error: {e}")
                self._network_error_logged = True
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status and statistics."""
        recent_violations = [
            v for v in self.security_violations
            if v.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        status = {
            'monitoring_active': self.is_monitoring,
            'total_violations': len(self.security_violations),
            'recent_violations': len(recent_violations),
            'critical_violations': len([v for v in recent_violations if v.level == 'Critical']),
            'high_violations': len([v for v in recent_violations if v.level == 'High']),
            'settings': self.settings.copy(),
            'last_check': datetime.now().isoformat()
        }
        
        return status
    
    def add_whitelist_pattern(self, pattern: str):
        """Add a pattern to the security whitelist."""
        if pattern not in self.whitelist_patterns:
            self.whitelist_patterns.append(pattern)
            self.logger.info(f"Added whitelist pattern: {pattern}")
    
    def remove_whitelist_pattern(self, pattern: str):
        """Remove a pattern from the security whitelist."""
        if pattern in self.whitelist_patterns:
            self.whitelist_patterns.remove(pattern)
            self.logger.info(f"Removed whitelist pattern: {pattern}")
    
    def is_whitelisted(self, operation: str) -> bool:
        """Check if an operation matches any whitelist pattern."""
        for pattern in self.whitelist_patterns:
            if re.search(pattern, operation, re.IGNORECASE):
                return True
        return False
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other components."""
        msg_type = message.get('type')
        data = message.get('data', {})
        
        if msg_type == 'check_file_access':
            file_path = data.get('file_path')
            operation = data.get('operation', 'read')
            risk = self.assess_file_access_risk(file_path, operation)
            approved = self.check_operation_approval(risk)
            
            return {
                'type': 'security_response',
                'data': {
                    'approved': approved,
                    'risk_level': risk.level,
                    'risk_description': risk.description
                }
            }
            
        elif msg_type == 'check_command':
            command = data.get('command')
            risk = self.assess_command_risk(command)
            approved = self.check_operation_approval(risk)
            
            return {
                'type': 'security_response',
                'data': {
                    'approved': approved,
                    'risk_level': risk.level,
                    'risk_description': risk.description
                }
            }
            
        elif msg_type == 'check_network':
            url = data.get('url')
            operation = data.get('operation', 'request')
            risk = self.assess_network_risk(url, operation)
            approved = self.check_operation_approval(risk)
            
            return {
                'type': 'security_response',
                'data': {
                    'approved': approved,
                    'risk_level': risk.level,
                    'risk_description': risk.description
                }
            }
            
        elif msg_type == 'get_status':
            return {
                'type': 'security_status',
                'data': self.get_security_status()
            }
            
        elif msg_type == 'update_settings':
            self.settings.update(data.get('settings', {}))
            return {
                'type': 'settings_updated',
                'data': {'success': True}
            }
        
        return {'type': 'unknown_message', 'data': {}}
    
    def start(self):
        """Start the security agent."""
        super().start()
        self.start_monitoring()
    
    def stop(self):
        """Stop the security agent."""
        self.stop_monitoring()
        super().stop()
    
    def execute_task(self, task: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a security-related task."""
        if parameters is None:
            parameters = {}
            
        if task == "assess_file_access":
            file_path = parameters.get("file_path", "")
            operation = parameters.get("operation", "read")
            risk = self.assess_file_access_risk(file_path, operation)
            return {
                "risk_level": risk.level,
                "risk_type": risk.risk_type,
                "description": risk.description,
                "approved": self.check_operation_approval(risk)
            }
            
        elif task == "assess_command":
            command = parameters.get("command", "")
            risk = self.assess_command_risk(command)
            return {
                "risk_level": risk.level,
                "risk_type": risk.risk_type,
                "description": risk.description,
                "approved": self.check_operation_approval(risk)
            }
            
        elif task == "assess_network":
            url = parameters.get("url", "")
            operation = parameters.get("operation", "request")
            risk = self.assess_network_risk(url, operation)
            return {
                "risk_level": risk.level,
                "risk_type": risk.risk_type,
                "description": risk.description,
                "approved": self.check_operation_approval(risk)
            }
            
        elif task == "get_status":
            return self.get_security_status()
            
        else:
            return {"error": f"Unknown security task: {task}"}
