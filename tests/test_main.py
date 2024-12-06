import unittest
from unittest.mock import MagicMock, patch

from app import setup_message_broker, setup_file_monitoring, start_consumer_listener, main


class TestFileMonitorApp(unittest.TestCase):

    @patch('app.MessageBroker')
    @patch('app.Consumer')
    def test_setup_message_broker(self, mock_consumer, mock_broker):
        """Test the setup of the message broker and consumer."""
        topic = "important_stuff~"
        consumer_name = "AuditConsumer"

        broker, consumer = setup_message_broker(topic, consumer_name)

        mock_consumer.assert_called_once_with(consumer_name)
        consumer.subscribe.assert_called_once_with(mock_broker.return_value, topic)

        self.assertIs(broker, mock_broker.return_value)
        self.assertIs(consumer, mock_consumer.return_value)

    @patch('app.Observer')
    @patch('app.FileChangeMonitor')
    @patch('os.path.join', return_value="/root/path/important_stuff")
    def test_setup_file_monitoring(self, mock_join, mock_file_change_monitor, mock_observer):
        """Test the setup of file monitoring."""
        broker = MagicMock()
        consumer = MagicMock()
        root_path = "/root/path"
        directory_to_watch = "important_stuff"

        observer = setup_file_monitoring(broker, consumer, root_path, directory_to_watch)

        mock_file_change_monitor.assert_called_once_with(broker, consumer)
        mock_observer.return_value.schedule.assert_called_once_with(
            mock_file_change_monitor.return_value,
            path="/root/path/important_stuff",
            recursive=True
        )
        self.assertIs(observer, mock_observer.return_value)

    @patch('time.sleep', side_effect=KeyboardInterrupt)
    def test_start_consumer_listener(self, mock_sleep):
        """Test the consumer listener loop."""
        with self.assertRaises(KeyboardInterrupt):
            start_consumer_listener()

        mock_sleep.assert_called()

    @patch('app.setup_message_broker')
    @patch('app.setup_file_monitoring')
    @patch('app.start_consumer_listener')
    @patch('app.os.getenv', return_value="/root/path")
    def test_main(self, mock_getenv, mock_start_listener, mock_setup_monitoring, mock_setup_broker):
        """Test the main application setup and execution."""
        mock_broker = MagicMock()
        mock_consumer = MagicMock()
        mock_observer = MagicMock()

        # Mock the return values
        mock_setup_monitoring.return_value = mock_observer
        mock_setup_broker.return_value = (mock_broker, mock_consumer)

        # Call the main function
        main()

        # Assertions
        mock_getenv.assert_called_once_with("FILE_SERVER_ROOT_PATH")
        mock_setup_broker.assert_called_once_with(topic="important_stuff~", consumer_name="AuditConsumer")
        mock_setup_monitoring.assert_called_once_with(
            mock_broker,
            mock_consumer,
            "/root/path",
            "important_stuff"
        )
        mock_observer.start.assert_called_once()
        mock_start_listener.assert_called_once()
        mock_observer.join.assert_called_once()


    @patch('app.os.getenv', return_value=None)
    def test_main_missing_root_path(self, mock_getenv):
        """Test the main function with missing FILE_SERVER_ROOT_PATH."""
        with self.assertRaises(EnvironmentError) as context:
            main()
        self.assertEqual(str(context.exception), "FILE_SERVER_ROOT_PATH environment variable is not set.")
