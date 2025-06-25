#!/usr/bin/env python3
"""
Enhanced Deputy Agent for Atlas

Provides background assistance and handles delegated tasks.
"""

import json
import logging
import os
import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from modules.agents.base_agent import BaseAgent


class Task:
    """Represents a task that can be executed by the Deputy Agent."""

    def __init__(self, task_id: str, task_type: str, parameters: Dict[str, Any],
                 priority: int = 5, created_by: str = "system"):
        self.id = task_id
        self.type = task_type
        self.parameters = parameters
        self.priority = priority  #1-10, where 1 is highest priority
        self.created_by = created_by
        self.created_at = datetime.now()
        self.status = "pending"  #pending, running, completed, failed
        self.result = None
        self.error_message = None
        self.attempts = 0
        self.max_attempts = 3
        self.estimated_duration = None
        self.actual_duration = None
        self.started_at = None
        self.completed_at = None

    def __lt__(self, other):
        """For priority queue ordering."""
        return self.priority < other.priority


class EnhancedDeputyAgent(BaseAgent):
    """Enhanced Deputy Agent that handles background tasks and provides assistance."""

    def __init__(self, connection=None, llm_manager=None, agent_manager=None):
        super().__init__("DeputyAgent", connection)
        self.llm_manager = llm_manager
        self.agent_manager = agent_manager
        self.logger = logging.getLogger(__name__)

        #Task management
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []

        #Worker threads
        self.max_workers = 3
        self.workers: List[threading.Thread] = []
        self.is_running = False

        #Capabilities
        self.capabilities = {
            "file_monitoring": True,
            "system_monitoring": True,
            "background_research": True,
            "data_processing": True,
            "notification_management": True,
            "cleanup_tasks": True,
            "health_checks": True,
            "log_analysis": True,
        }

        #Monitoring settings
        self.monitoring_intervals = {
            "system_health": 60,  #seconds
            "file_changes": 30,
            "log_analysis": 300,
            "cleanup": 3600,
        }

        #Background monitoring threads
        self.monitoring_threads: Dict[str, threading.Thread] = {}

        #Data storage
        self.data_dir = "data/deputy"
        os.makedirs(self.data_dir, exist_ok=True)

        #Load persistent data
        self.load_persistent_data()

    def load_persistent_data(self):
        """Load persistent data from disk."""
        try:
            #Load completed tasks history
            history_file = os.path.join(self.data_dir, "task_history.json")
            if os.path.exists(history_file):
                with open(history_file) as f:
                    history_data = json.load(f)
                    #Convert to Task objects (simplified - just keep as dict for now)
                    self.completed_tasks = history_data.get("completed", [])
                    self.failed_tasks = history_data.get("failed", [])
        except Exception as e:
            self.logger.error(f"Failed to load persistent data: {e}")

    def save_persistent_data(self):
        """Save persistent data to disk."""
        try:
            history_file = os.path.join(self.data_dir, "task_history.json")

            #Convert tasks to serializable format
            completed_data = []
            for task in self.completed_tasks[-100:]:  #Keep last 100 tasks
                if isinstance(task, Task):
                    completed_data.append({
                        "id": task.id,
                        "type": task.type,
                        "parameters": task.parameters,
                        "status": task.status,
                        "created_at": task.created_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "duration": task.actual_duration,
                        "created_by": task.created_by,
                    })
                else:
                    completed_data.append(task)

            failed_data = []
            for task in self.failed_tasks[-50:]:  #Keep last 50 failed tasks
                if isinstance(task, Task):
                    failed_data.append({
                        "id": task.id,
                        "type": task.type,
                        "parameters": task.parameters,
                        "status": task.status,
                        "error_message": task.error_message,
                        "created_at": task.created_at.isoformat(),
                        "attempts": task.attempts,
                        "created_by": task.created_by,
                    })
                else:
                    failed_data.append(task)

            with open(history_file, "w") as f:
                json.dump({
                    "completed": completed_data,
                    "failed": failed_data,
                    "last_updated": datetime.now().isoformat(),
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save persistent data: {e}")

    def start(self):
        """Start the Deputy Agent and its workers."""
        if self.is_running:
            return

        self.is_running = True
        super().start()

        #Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"DeputyWorker-{i}", daemon=True)
            worker.start()
            self.workers.append(worker)

        #Start monitoring threads
        self.start_monitoring_tasks()

        self.logger.info(f"Deputy Agent started with {self.max_workers} workers")

    def stop(self):
        """Stop the Deputy Agent and its workers."""
        self.is_running = False

        #Stop monitoring
        self.stop_monitoring_tasks()

        #Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)

        #Save persistent data
        self.save_persistent_data()

        super().stop()
        self.logger.info("Deputy Agent stopped")

    def _worker_loop(self):
        """Main worker loop for processing tasks."""
        while self.is_running:
            try:
                #Get next task from queue (blocks for up to 1 second)
                try:
                    priority, task = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue

                #Execute the task
                self._execute_task(task)
                self.task_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error in worker loop: {e}")
                time.sleep(1)

    def _execute_task(self, task: Task):
        """Execute a specific task."""
        task.status = "running"
        task.started_at = datetime.now()
        task.attempts += 1

        self.running_tasks[task.id] = task

        try:
            self.logger.info(f"Executing task {task.id}: {task.type}")

            #Route to appropriate handler
            if task.type == "file_monitoring":
                result = self._handle_file_monitoring(task)
            elif task.type == "system_health_check":
                result = self._handle_system_health_check(task)
            elif task.type == "background_research":
                result = self._handle_background_research(task)
            elif task.type == "data_processing":
                result = self._handle_data_processing(task)
            elif task.type == "cleanup":
                result = self._handle_cleanup(task)
            elif task.type == "log_analysis":
                result = self._handle_log_analysis(task)
            elif task.type == "notification":
                result = self._handle_notification(task)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

            #Task completed successfully
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()
            task.actual_duration = (task.completed_at - task.started_at).total_seconds()

            self.completed_tasks.append(task)
            self.logger.info(f"Task {task.id} completed successfully in {task.actual_duration:.2f}s")

        except Exception as e:
            #Task failed
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()

            self.logger.error(f"Task {task.id} failed: {e}")

            #Retry if attempts remaining
            if task.attempts < task.max_attempts:
                task.status = "pending"
                self.add_task(task.type, task.parameters, task.priority, task.created_by, task)
                self.logger.info(f"Retrying task {task.id} (attempt {task.attempts + 1}/{task.max_attempts})")
            else:
                self.failed_tasks.append(task)

        finally:
            #Remove from running tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

    def add_task(self, task_type: str, parameters: Dict[str, Any],
                priority: int = 5, created_by: str = "system", existing_task: Optional[Task] = None) -> str:
        """Add a new task to the queue."""
        if existing_task:
            task = existing_task
        else:
            task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(parameters)}"
            task = Task(task_id, task_type, parameters, priority, created_by)

        self.task_queue.put((priority, task))
        self.logger.info(f"Added task {task.id}: {task_type} (priority {priority})")

        return task.id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        #Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return self._task_to_dict(task)

        #Check completed tasks
        for task in self.completed_tasks:
            if (isinstance(task, Task) and task.id == task_id) or \
               (isinstance(task, dict) and task.get("id") == task_id):
                return self._task_to_dict(task)

        #Check failed tasks
        for task in self.failed_tasks:
            if (isinstance(task, Task) and task.id == task_id) or \
               (isinstance(task, dict) and task.get("id") == task_id):
                return self._task_to_dict(task)

        return None

    def _task_to_dict(self, task) -> Dict[str, Any]:
        """Convert a task to dictionary format."""
        if isinstance(task, Task):
            return {
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "priority": task.priority,
                "created_by": task.created_by,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "duration": task.actual_duration,
                "attempts": task.attempts,
                "result": task.result,
                "error_message": task.error_message,
            }
        return task  #Already a dict

    def start_monitoring_tasks(self):
        """Start background monitoring tasks."""
        #System health monitoring
        if self.capabilities["system_monitoring"]:
            self.monitoring_threads["system_health"] = threading.Thread(
                target=self._periodic_system_health_check,
                daemon=True,
            )
            self.monitoring_threads["system_health"].start()

        #Log analysis
        if self.capabilities["log_analysis"]:
            self.monitoring_threads["log_analysis"] = threading.Thread(
                target=self._periodic_log_analysis,
                daemon=True,
            )
            self.monitoring_threads["log_analysis"].start()

        #Cleanup tasks
        if self.capabilities["cleanup_tasks"]:
            self.monitoring_threads["cleanup"] = threading.Thread(
                target=self._periodic_cleanup,
                daemon=True,
            )
            self.monitoring_threads["cleanup"].start()

    def stop_monitoring_tasks(self):
        """Stop background monitoring tasks."""
        #Monitoring threads will stop when self.is_running becomes False
        for name, thread in self.monitoring_threads.items():
            if thread.is_alive():
                thread.join(timeout=2)

    def _periodic_system_health_check(self):
        """Periodically check system health."""
        while self.is_running:
            try:
                self.add_task("system_health_check", {}, priority=7, created_by="monitor")
                time.sleep(self.monitoring_intervals["system_health"])
            except Exception as e:
                self.logger.error(f"Error in system health monitoring: {e}")
                time.sleep(60)  #Wait a minute on error

    def _periodic_log_analysis(self):
        """Periodically analyze logs for issues."""
        while self.is_running:
            try:
                self.add_task("log_analysis", {}, priority=8, created_by="monitor")
                time.sleep(self.monitoring_intervals["log_analysis"])
            except Exception as e:
                self.logger.error(f"Error in log analysis monitoring: {e}")
                time.sleep(300)  #Wait 5 minutes on error

    def _periodic_cleanup(self):
        """Periodically perform cleanup tasks."""
        while self.is_running:
            try:
                self.add_task("cleanup", {"type": "general"}, priority=9, created_by="monitor")
                time.sleep(self.monitoring_intervals["cleanup"])
            except Exception as e:
                self.logger.error(f"Error in cleanup monitoring: {e}")
                time.sleep(3600)  #Wait an hour on error

    #Task handlers

    def _handle_file_monitoring(self, task: Task) -> Dict[str, Any]:
        """Handle file monitoring tasks."""
        parameters = task.parameters
        watch_path = parameters.get("path", ".")

        #Simple file monitoring implementation
        file_info = {}
        if os.path.exists(watch_path):
            if os.path.isfile(watch_path):
                stat = os.stat(watch_path)
                file_info[watch_path] = {
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "created": stat.st_ctime,
                }
            elif os.path.isdir(watch_path):
                for root, dirs, files in os.walk(watch_path):
                    for file in files[:10]:  #Limit to first 10 files
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            file_info[file_path] = {
                                "size": stat.st_size,
                                "modified": stat.st_mtime,
                            }
                        except OSError:
                            continue

        return {
            "monitored_files": len(file_info),
            "file_info": file_info,
            "timestamp": datetime.now().isoformat(),
        }

    def _handle_system_health_check(self, task: Task) -> Dict[str, Any]:
        """Handle system health check tasks."""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        #Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            health_data["checks"]["disk_space"] = {
                "total_gb": total // (1024**3),
                "used_gb": used // (1024**3),
                "free_gb": free // (1024**3),
                "usage_percent": (used / total) * 100,
            }
        except Exception as e:
            health_data["checks"]["disk_space"] = {"error": str(e)}

        #Check memory usage (if psutil available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            health_data["checks"]["memory"] = {
                "total_gb": memory.total // (1024**3),
                "available_gb": memory.available // (1024**3),
                "usage_percent": memory.percent,
            }
        except ImportError:
            health_data["checks"]["memory"] = {"error": "psutil not available"}
        except Exception as e:
            health_data["checks"]["memory"] = {"error": str(e)}

        #Check running processes count
        try:
            import psutil
            health_data["checks"]["processes"] = {
                "count": len(psutil.pids()),
            }
        except ImportError:
            health_data["checks"]["processes"] = {"error": "psutil not available"}
        except Exception as e:
            health_data["checks"]["processes"] = {"error": str(e)}

        return health_data

    def _handle_background_research(self, task: Task) -> Dict[str, Any]:
        """Handle background research tasks."""
        parameters = task.parameters
        query = parameters.get("query", "")

        if not self.llm_manager or not query:
            return {"error": "No LLM manager available or no query provided"}

        try:
            #Perform research using LLM
            research_prompt = f"Research and provide detailed information about: {query}"
            response = self.llm_manager.get_completion(research_prompt)

            return {
                "query": query,
                "research_result": response,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _handle_data_processing(self, task: Task) -> Dict[str, Any]:
        """Handle data processing tasks."""
        parameters = task.parameters
        data_type = parameters.get("type", "unknown")
        data = parameters.get("data", {})

        if data_type == "log_aggregation":
            #Aggregate log data
            return self._aggregate_log_data(data)
        if data_type == "metrics_calculation":
            #Calculate metrics
            return self._calculate_metrics(data)
        return {"error": f"Unknown data processing type: {data_type}"}

    def _handle_cleanup(self, task: Task) -> Dict[str, Any]:
        """Handle cleanup tasks."""
        parameters = task.parameters
        cleanup_type = parameters.get("type", "general")

        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "actions": [],
        }

        if cleanup_type in ["general", "logs"]:
            #Clean old log files
            log_dir = "logs"
            if os.path.exists(log_dir):
                cutoff_date = datetime.now() - timedelta(days=30)
                cleaned_files = []

                for file in os.listdir(log_dir):
                    file_path = os.path.join(log_dir, file)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            try:
                                os.remove(file_path)
                                cleaned_files.append(file)
                            except OSError:
                                pass

                cleanup_results["actions"].append({
                    "type": "log_cleanup",
                    "files_removed": len(cleaned_files),
                    "files": cleaned_files,
                })

        if cleanup_type in ["general", "temp"]:
            #Clean temporary files
            temp_dirs = ["temp", "tmp", "__pycache__"]
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        import shutil
                        shutil.rmtree(temp_dir)
                        cleanup_results["actions"].append({
                            "type": "temp_cleanup",
                            "directory": temp_dir,
                            "status": "removed",
                        })
                    except Exception as e:
                        cleanup_results["actions"].append({
                            "type": "temp_cleanup",
                            "directory": temp_dir,
                            "status": "failed",
                            "error": str(e),
                        })

        return cleanup_results

    def _handle_log_analysis(self, task: Task) -> Dict[str, Any]:
        """Handle log analysis tasks."""
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "log_files_analyzed": 0,
            "issues_found": [],
            "summary": {},
        }

        log_dir = "logs"
        if not os.path.exists(log_dir):
            return analysis_results

        error_patterns = [
            r"ERROR", r"CRITICAL", r"FATAL", r"Exception", r"Traceback",
        ]

        for log_file in os.listdir(log_dir):
            if log_file.endswith(".log"):
                log_path = os.path.join(log_dir, log_file)
                try:
                    with open(log_path) as f:
                        lines = f.readlines()
                        analysis_results["log_files_analyzed"] += 1

                        for i, line in enumerate(lines[-1000:]):  #Check last 1000 lines
                            for pattern in error_patterns:
                                if pattern in line:
                                    analysis_results["issues_found"].append({
                                        "file": log_file,
                                        "line_number": len(lines) - 1000 + i,
                                        "pattern": pattern,
                                        "line": line.strip()[:200],  #Truncate long lines
                                    })
                                    break
                except Exception as e:
                    analysis_results["issues_found"].append({
                        "file": log_file,
                        "error": f"Failed to read file: {e}",
                    })

        analysis_results["summary"] = {
            "total_issues": len(analysis_results["issues_found"]),
            "files_with_issues": len(set(issue.get("file") for issue in analysis_results["issues_found"] if "file" in issue)),
        }

        return analysis_results

    def _handle_notification(self, task: Task) -> Dict[str, Any]:
        """Handle notification tasks."""
        parameters = task.parameters
        message = parameters.get("message", "")
        notification_type = parameters.get("type", "info")

        #For now, just log the notification
        #In a full implementation, this would send actual notifications
        self.logger.info(f"Notification ({notification_type}): {message}")

        return {
            "message": message,
            "type": notification_type,
            "sent_at": datetime.now().isoformat(),
            "status": "logged",
        }

    def _aggregate_log_data(self, data: Dict) -> Dict[str, Any]:
        """Aggregate log data for analysis."""
        #Placeholder implementation
        return {
            "aggregated_entries": len(data.get("entries", [])),
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_metrics(self, data: Dict) -> Dict[str, Any]:
        """Calculate metrics from data."""
        #Placeholder implementation
        return {
            "metrics_calculated": True,
            "data_points": len(data.get("points", [])),
            "timestamp": datetime.now().isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Deputy Agent."""
        return {
            "is_running": self.is_running,
            "workers": len(self.workers),
            "queue_size": self.task_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "capabilities": self.capabilities,
            "monitoring_active": len(self.monitoring_threads),
            "last_health_check": datetime.now().isoformat(),
        }

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other components."""
        msg_type = message.get("type")
        data = message.get("data", {})

        if msg_type == "add_task":
            task_id = self.add_task(
                data.get("task_type"),
                data.get("parameters", {}),
                data.get("priority", 5),
                data.get("created_by", "external"),
            )
            return {
                "type": "task_added",
                "data": {"task_id": task_id},
            }

        if msg_type == "get_task_status":
            task_id = data.get("task_id")
            status = self.get_task_status(task_id)
            return {
                "type": "task_status",
                "data": {"task_id": task_id, "status": status},
            }

        if msg_type == "get_status":
            return {
                "type": "deputy_status",
                "data": self.get_status(),
            }

        if msg_type == "delegate_task":
            #Handle task delegation from MasterAgent
            task_type = data.get("task_type")
            parameters = data.get("parameters", {})
            priority = data.get("priority", 5)

            task_id = self.add_task(task_type, parameters, priority, "MasterAgent")
            return {
                "type": "task_delegated",
                "data": {"task_id": task_id},
            }

        return {"type": "unknown_message", "data": {}}

    def execute_task(self, task: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task directly (synchronous execution)."""
        if parameters is None:
            parameters = {}

        try:
            #Create a task object
            from datetime import datetime
            task_id = f"{task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            task_obj = Task(task_id, task, parameters, priority=1, created_by="direct")

            #Execute immediately
            self._execute_task(task_obj)

            return {
                "task_id": task_id,
                "status": task_obj.status,
                "result": task_obj.result,
                "error": task_obj.error_message,
            }

        except Exception as e:
            return {
                "task_id": None,
                "status": "failed",
                "result": None,
                "error": str(e),
            }
