"""
Workflow Monitoring and Analytics Module

This module provides functionality for real-time monitoring, performance metrics,
and optimization suggestions for workflows.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkflowAnalytics:
    """Handles monitoring and analytics for workflow execution."""

    def __init__(self, db_path: str = "workflow_analytics.db"):
        """Initialize the Workflow Analytics system.

        Args:
            db_path (str): Path to the SQLite database for storing analytics data.
        """
        self.db_path = db_path
        self.conn = None
        self.initialize_db()

    def initialize_db(self) -> None:
        """Initialize the SQLite database for analytics data."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    status TEXT,
                    actions_count INTEGER,
                    failed_actions_count INTEGER,
                    details TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    status TEXT,
                    error_message TEXT
                )
            """)
            self.conn.commit()
            logger.info("Database initialized for workflow analytics.")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize analytics database: {e}")
            raise

    def start_execution(self, execution_id: str, workflow_id: str) -> None:
        """Record the start of a workflow execution.

        Args:
            execution_id (str): Unique identifier for this execution.
            workflow_id (str): Identifier of the workflow being executed.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflow_executions (
                    execution_id, workflow_id, start_time, status,
                    actions_count, failed_actions_count
                )
                VALUES (?, ?, ?, 'running', 0, 0)
            """,
                (execution_id, workflow_id, datetime.now()),
            )
            self.conn.commit()
            logger.info(
                f"Started monitoring execution {execution_id} for workflow {workflow_id}"
            )
        except sqlite3.Error as e:
            logger.error(f"Failed to start monitoring execution {execution_id}: {e}")
            raise

    def end_execution(
        self, execution_id: str, status: str, details: Optional[str] = None
    ) -> None:
        """Record the end of a workflow execution.

        Args:
            execution_id (str): Unique identifier for this execution.
            status (str): Final status of the execution ('completed', 'failed', 'aborted').
            details (Optional[str]): Additional details or error messages if applicable.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE workflow_executions
                SET end_time = ?,
                    duration_seconds = (strftime('%s', 'now') - strftime('%s', start_time)),
                    status = ?,
                    details = ?
                WHERE execution_id = ?
            """,
                (datetime.now(), status, details or "", execution_id),
            )
            self.conn.commit()
            logger.info(
                f"Ended monitoring execution {execution_id} with status {status}"
            )
        except sqlite3.Error as e:
            logger.error(f"Failed to end monitoring execution {execution_id}: {e}")
            raise

    def record_action(
        self,
        execution_id: str,
        action_name: str,
        start_time: datetime,
        end_time: datetime,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Record the execution details of a single action within a workflow.

        Args:
            execution_id (str): Unique identifier for the workflow execution.
            action_name (str): Name or identifier of the action.
            start_time (datetime): When the action started.
            end_time (datetime): When the action ended.
            status (str): Status of the action ('success', 'failed').
            error_message (Optional[str]): Error message if the action failed.
        """
        try:
            cursor = self.conn.cursor()
            duration = (end_time - start_time).total_seconds()
            cursor.execute(
                """
                INSERT INTO action_executions (
                    execution_id, action_name, start_time, end_time,
                    duration_seconds, status, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    execution_id,
                    action_name,
                    start_time,
                    end_time,
                    duration,
                    status,
                    error_message or "",
                ),
            )

            # Update counts in workflow_executions
            if status == "failed":
                cursor.execute(
                    """
                    UPDATE workflow_executions
                    SET actions_count = actions_count + 1,
                        failed_actions_count = failed_actions_count + 1
                    WHERE execution_id = ?
                """,
                    (execution_id,),
                )
            else:
                cursor.execute(
                    """
                    UPDATE workflow_executions
                    SET actions_count = actions_count + 1
                    WHERE execution_id = ?
                """,
                    (execution_id,),
                )

            self.conn.commit()
            logger.info(
                f"Recorded action {action_name} for execution {execution_id} with status {status}"
            )
        except sqlite3.Error as e:
            logger.error(
                f"Failed to record action {action_name} for execution {execution_id}: {e}"
            )
            raise

    def get_workflow_performance(
        self, workflow_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve performance data for a specific workflow.

        Args:
            workflow_id (str): Identifier of the workflow to analyze.
            limit (int): Maximum number of recent executions to return.

        Returns:
            List[Dict[str, Any]]: List of execution performance data.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT execution_id, start_time, end_time, duration_seconds,
                       status, actions_count, failed_actions_count, details
                FROM workflow_executions
                WHERE workflow_id = ?
                ORDER BY start_time DESC
                LIMIT ?
            """,
                (workflow_id, limit),
            )

            columns = [
                "execution_id",
                "start_time",
                "end_time",
                "duration_seconds",
                "status",
                "actions_count",
                "failed_actions_count",
                "details",
            ]
            results = [
                dict(zip(columns, row, strict=False)) for row in cursor.fetchall()
            ]
            logger.info(
                f"Retrieved performance data for workflow {workflow_id} with {len(results)} executions"
            )
            return results
        except sqlite3.Error as e:
            logger.error(
                f"Failed to retrieve performance data for workflow {workflow_id}: {e}"
            )
            raise

    def get_action_performance(self, execution_id: str) -> List[Dict[str, Any]]:
        """Retrieve performance data for actions within a specific execution.

        Args:
            execution_id (str): Unique identifier for the workflow execution.

        Returns:
            List[Dict[str, Any]]: List of action performance data.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, action_name, start_time, end_time, duration_seconds, status, error_message
                FROM action_executions
                WHERE execution_id = ?
                ORDER BY start_time
            """,
                (execution_id,),
            )

            columns = [
                "id",
                "action_name",
                "start_time",
                "end_time",
                "duration_seconds",
                "status",
                "error_message",
            ]
            results = [
                dict(zip(columns, row, strict=False)) for row in cursor.fetchall()
            ]
            logger.info(
                f"Retrieved action performance data for execution {execution_id} with {len(results)} actions"
            )
            return results
        except sqlite3.Error as e:
            logger.error(
                f"Failed to retrieve action performance data for execution {execution_id}: {e}"
            )
            raise

    def analyze_failures(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze failure patterns for a specific workflow.

        Args:
            workflow_id (str): Identifier of the workflow to analyze.

        Returns:
            Dict[str, Any]: Analysis of failures including common failing actions and error messages.
        """
        try:
            cursor = self.conn.cursor()
            # Get failed executions
            cursor.execute(
                """
                SELECT execution_id, details
                FROM workflow_executions
                WHERE workflow_id = ? AND status = 'failed'
            """,
                (workflow_id,),
            )
            failed_executions = cursor.fetchall()

            # Get failed actions
            cursor.execute(
                """
                SELECT ae.action_name, ae.error_message, COUNT(*) as failure_count
                FROM action_executions ae
                JOIN workflow_executions we ON ae.execution_id = we.execution_id
                WHERE we.workflow_id = ? AND ae.status = 'failed'
                GROUP BY ae.action_name, ae.error_message
                ORDER BY failure_count DESC
            """,
                (workflow_id,),
            )
            failed_actions = cursor.fetchall()

            analysis = {
                "total_failed_executions": len(failed_executions),
                "failed_actions": [
                    {"action_name": row[0], "error_message": row[1], "count": row[2]}
                    for row in failed_actions
                ],
                "recommendations": self._generate_recommendations(failed_actions),
            }
            logger.info(f"Analyzed failures for workflow {workflow_id}")
            return analysis
        except sqlite3.Error as e:
            logger.error(f"Failed to analyze failures for workflow {workflow_id}: {e}")
            raise

    def _generate_recommendations(self, failed_actions: List[tuple]) -> List[str]:
        """Generate recommendations based on failure analysis.

        Args:
            failed_actions (List[tuple]): List of failed actions with their error messages and counts.

        Returns:
            List[str]: List of recommendations to address failures.
        """
        recommendations = []
        for action_name, error_message, count in failed_actions:
            if count > 1:  # Only generate recommendations for recurring failures
                recommendations.append(
                    f"Review action '{action_name}' for recurring error: {error_message} (failed {count} times)"
                )
                if "timeout" in error_message.lower():
                    recommendations.append(
                        f"Consider increasing timeout for action '{action_name}'"
                    )
                elif (
                    "permission" in error_message.lower()
                    or "access denied" in error_message.lower()
                ):
                    recommendations.append(
                        f"Check permissions for action '{action_name}'"
                    )
                elif "not found" in error_message.lower():
                    recommendations.append(
                        f"Verify resource availability for action '{action_name}'"
                    )
        return recommendations

    def optimize_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Suggest optimizations for a workflow based on performance data.

        Args:
            workflow_id (str): Identifier of the workflow to optimize.

        Returns:
            Dict[str, Any]: Optimization suggestions including bottlenecks and parallelization opportunities.
        """
        try:
            cursor = self.conn.cursor()
            # Get average duration of actions to identify bottlenecks
            cursor.execute(
                """
                SELECT ae.action_name, AVG(ae.duration_seconds) as avg_duration, COUNT(*) as execution_count
                FROM action_executions ae
                JOIN workflow_executions we ON ae.execution_id = we.execution_id
                WHERE we.workflow_id = ? AND ae.status = 'success'
                GROUP BY ae.action_name
                ORDER BY avg_duration DESC
            """,
                (workflow_id,),
            )
            action_durations = cursor.fetchall()

            # Check if workflow has a high total duration
            cursor.execute(
                """
                SELECT AVG(duration_seconds) as avg_total_duration, COUNT(*) as execution_count
                FROM workflow_executions
                WHERE workflow_id = ? AND status = 'completed'
            """,
                (workflow_id,),
            )
            total_duration_data = cursor.fetchone()

            suggestions = {
                "bottlenecks": [],
                "parallelization_opportunities": [],
                "other_suggestions": [],
            }

            if total_duration_data and total_duration_data[0] is not None:
                avg_total_duration = total_duration_data[0]
                if (
                    avg_total_duration > 10.0
                ):  # Arbitrary threshold for long-running workflows
                    suggestions["other_suggestions"].append(
                        f"Workflow takes on average {avg_total_duration:.2f} seconds "
                        f"to complete. Consider breaking it into smaller workflows."
                    )

                # Identify bottlenecks (actions taking more than 20% of total duration)
                for action_name, avg_duration, count in action_durations:
                    if count > 1 and avg_duration > avg_total_duration * 0.2:
                        suggestions["bottlenecks"].append(
                            f"Action '{action_name}' takes on average "
                            f"{avg_duration:.2f} seconds "
                            f"({(avg_duration / avg_total_duration) * 100:.1f}% of total)"
                        )
                        suggestions["parallelization_opportunities"].append(
                            f"Consider parallelizing or optimizing action '{action_name}'"
                        )

            logger.info(
                f"Generated optimization suggestions for workflow {workflow_id}"
            )
            return suggestions
        except sqlite3.Error as e:
            logger.error(f"Failed to optimize workflow {workflow_id}: {e}")
            raise

    def __del__(self):
        """Cleanup database connection on object destruction."""
        if self.conn:
            self.conn.close()
            logger.info("Closed database connection for WorkflowAnalytics.")
