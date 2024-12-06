import unittest
from unittest.mock import MagicMock, patch, mock_open
from file_monitor.monitor import FileChangeMonitor
from datetime import datetime


class TestFileChangeMonitor(unittest.TestCase):
    """Test cases for File change monitor"""

    def setUp(self):
        """Set up test dependencies and mock objects."""
        self.mock_broker = MagicMock()
        self.mock_consumer = MagicMock()
        self.handler = FileChangeMonitor(self.mock_broker, self.mock_consumer)

    @patch('os.getenv')
    def test_generate_topic_from_file_path(self, mock_getenv):
        """Test topic generation from file path."""
        mock_getenv.return_value = "/root/path"
        self.handler.root_path = "/root/path"

        file_path = "/root/path/subdir/file.txt"
        expected_topic = "subdir/file.txt"
        self.assertEqual(self.handler._generate_topic_from_file_path(file_path), expected_topic)

    @patch('file_monitor.monitor.datetime')
    def test_get_current_timestamp(self, mock_datetime):
        """Test if the current timestamp is formatted correctly."""
        mock_datetime.now.return_value = datetime(2024, 12, 6, 12, 30, 45)
        mock_datetime.now.strftime.return_value = '2024-12-06 12:30:45'

        timestamp = self.handler._get_current_timestamp()
        self.assertEqual(timestamp, '2024-12-06 12:30:45')

    @patch('builtins.open', new_callable=mock_open, read_data="Line1\nLine2\n")
    def test_get_file_diff_with_no_previous_version(self, mock_file):
        """Test diff generation when there's no previous version of the file."""
        file_path = "file.txt"
        self.handler.file_versions = {}
        expected_diff = "+ ['Line1\\n', 'Line2\\n']"

        diff = self.handler.get_file_diff(file_path)
        self.assertEqual(diff, expected_diff)
        mock_file.assert_called_once_with(file_path, 'r')

    @patch('builtins.open', new_callable=mock_open, read_data="Line1\nLine2\n")
    def test_get_file_diff_with_previous_version(self, mock_file):
        """Test diff generation when there's a previous version of the file."""
        file_path = "file.txt"
        self.handler.file_versions[file_path] = ["Line1\n", "LineOld\n"]
        expected_diff = "--- previous\n+++ current\n@@ -1,2 +1,2 @@\n Line1\n\n-LineOld\n\n+Line2\n"

        diff = self.handler.get_file_diff(file_path)
        self.assertEqual(diff, expected_diff)
        mock_file.assert_called_once_with(file_path, 'r')

    @patch('file_monitor.monitor.FileChangeMonitor.get_file_diff')
    @patch('file_monitor.monitor.FileChangeMonitor._get_current_timestamp')
    def test_publish_file_change(self, mock_timestamp, mock_get_file_diff):
        """Test if file change is published to the broker."""
        mock_timestamp.return_value = "2024-12-06 12:30:45"
        mock_get_file_diff.return_value = "--- diff ---"
        self.handler.root_path = "/root/path"

        file_path = "/root/path/subdir/file.txt"
        self.handler.publish_file_change(file_path, "2024-12-06 12:30:45")

        topic = "subdir/file.txt"
        message = "Timestamp: 2024-12-06 12:30:45\nDiff:\n--- diff ---"
        self.mock_broker.publish.assert_called_once_with(topic, message)

    def test_on_modified_ignores_directories(self):
        """Test that on_modified ignores directories."""
        mock_event = MagicMock()
        mock_event.is_directory = True

        self.handler.on_modified(mock_event)
        self.mock_broker.publish.assert_not_called()

    @patch('file_monitor.monitor.FileChangeMonitor.publish_file_change')
    @patch('file_monitor.monitor.FileChangeMonitor.audit_change_log')
    def test_on_modified_calls_publish_and_audit_for_files(self,
                                    mock_audit_change_log,
                                    mock_publish_file_change):
        """Test that on_modified calls publish_file_change and audit_change_log for files."""
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "file.txt"

        with patch('file_monitor.monitor.FileChangeMonitor._get_current_timestamp',
                   return_value="2024-12-06 12:30:45"):
            self.handler.on_modified(mock_event)

        mock_publish_file_change.assert_called_once_with("file.txt", "2024-12-06 12:30:45")
        mock_audit_change_log.assert_called_once_with("2024-12-06 12:30:45", "file.txt")

    @patch('builtins.open', new_callable=mock_open)
    def test_audit_change_log(self, mock_open):
        """Test that audit_change_log writes the correct entry to the log file."""
        timestamp = "2024-12-06 12:30:45"
        file_path = "file.txt"

        self.handler.audit_change_log(timestamp, file_path)

        mock_open.assert_called_once_with(self.handler.audit_log_path, "a")
        mock_open().write.assert_called_once_with(f"{timestamp}, {file_path}\n")
