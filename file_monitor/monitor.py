"""
This module defines a `FileChangeMonitor` class that monitors file changes in a directory using the
`watchdog` library. It handles file modifications, publishes file change events to a 
message broker, and logs file changes for auditing purposes.
"""

import os
from datetime import datetime
import difflib

from watchdog.events import FileSystemEventHandler


class FileChangeMonitor(FileSystemEventHandler):
    """
    Monitors file changes in a directory and handles events such as file modifications.
    Publishes file change events to a broker and logs file changes for auditing.
    """

    def __init__(self, broker, consumer, audit_log_path="file_change_audit.log"):
        """
        Initializes the file change monitor.

        Args:
            broker: The message broker to publish events to.
            consumer: The consumer object for handling messages.
            audit_log_path (str): Path to the audit log file for recording file change events.
        """
        self.file_versions = {}
        self.broker = broker
        self.consumer = consumer
        self.audit_log_path = audit_log_path
        self.root_path = os.getenv("FILE_SERVER_ROOT_PATH")

    def on_modified(self, event):
        """
        Handles the event when a file is modified.

        Args:
            event: The event object containing details about the file change.
        """
        if event.is_directory:
            return
        # Publish the file change event to the broker
        timestamp = self._get_current_timestamp()
        self.publish_file_change(event.src_path, timestamp)
        # Log the file change for auditing
        self.audit_change_log(timestamp, event.src_path)

    def publish_file_change(self, file_path, timestamp):
        """
        Publishes a file change event to the broker.

        Args:
            file_path (str): The path of the modified file.
            timestamp (str): The timestamp of the file change.
        """
        file_diff = self.get_file_diff(file_path)
        topic = self._generate_topic_from_file_path(file_path)
        self.broker.publish(topic, f"Timestamp: {timestamp}\nDiff:\n{file_diff}")

    def get_file_diff(self, file_path):
        """
        Generates a diff of the modified file compared to its previous version.

        Args:
            file_path (str): The path of the modified file.

        Returns:
            str: The diff of the file.
        """
        with open(file_path, 'r', encoding='utf-8') as fp:
            current_content = fp.readlines()
        previous_content = self.file_versions.get(file_path)

        if previous_content:
            diff = difflib.unified_diff(previous_content,
                                        current_content,
                                        fromfile='previous',
                                        tofile='current',
                                        lineterm='')
            file_diff = '\n'.join(diff)
        else:
            file_diff = f"+ {current_content}"
        self.file_versions[file_path] = current_content

        return file_diff

    def audit_change_log(self, timestamp, file_path):
        """
        Appends a log entry for a file change to the audit log file.

        Args:
            timestamp (str): The timestamp of the file change.
            file_path (str): The path of the modified file.
        """
        log_entry = f"{timestamp}, {file_path}\n"
        with open(self.audit_log_path, "a", encoding='utf-8') as log_file:
            log_file.write(log_entry)

    def _get_current_timestamp(self):
        """
        Retrieves the current timestamp.

        Returns:
            str: The current timestamp in 'YYYY-MM-DD HH:MM:SS' format.
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _generate_topic_from_file_path(self, file_path):
        """
        Generates a topic string based on the file path relative to the root path.

        Args:
            file_path (str): The full path of the file.

        Returns:
            str: The relative topic string.
        """
        return os.path.relpath(file_path, self.root_path)
