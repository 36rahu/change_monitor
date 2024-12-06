"""
This module sets up and runs a file monitoring system that listens for changes in a specified 
directory and processes messages via a message broker. 
"""
import os
import time

from watchdog.observers import Observer

from message_broker.broker import MessageBroker, Consumer
from file_monitor.monitor import FileChangeMonitor


def setup_message_broker(topic, consumer_name="AuditConsumer"):
    """
    Initialize the message broker and consumer, and subscribe the consumer to a specific topic.

    Args:
        topic (str): The topic to which the consumer subscribes.
        consumer_name (str): Name of the consumer (default: "AuditConsumer").

    Returns:
        tuple: The initialized message broker and consumer.
    """
    broker = MessageBroker()
    consumer = Consumer(consumer_name)
    consumer.subscribe(broker, topic)
    return broker, consumer


def setup_file_monitoring(broker, consumer, root_path, directory_to_watch):
    """
    Set up file monitoring for a specified directory and return the observer.

    Args:
        broker (MessageBroker): The message broker instance.
        consumer (Consumer): The consumer instance.
        root_path (str): The root path of the file server.
        directory_to_watch (str): The directory to monitor for file changes.

    Returns:
        Observer: The observer monitoring the specified directory.
    """
    event_handler = FileChangeMonitor(broker, consumer)
    observer = Observer()
    monitoring_path = os.path.join(root_path, directory_to_watch)
    observer.schedule(event_handler, path=monitoring_path, recursive=True)
    return observer


def start_consumer_listener():
    """
    Start the consumer listener to process messages indefinitely.
    """
    print("Listening for messages...")
    while True:
        time.sleep(1)


def main():
    """
    Main function to set up and run the file monitoring and message broker application.
    """
    root_path = os.getenv("FILE_SERVER_ROOT_PATH")
    if not root_path:
        raise EnvironmentError("FILE_SERVER_ROOT_PATH environment variable is not set.")

    directory_to_watch = "important_stuff"
    broker, consumer = setup_message_broker(topic=f"{directory_to_watch}~",
                                            consumer_name="AuditConsumer")
    observer = setup_file_monitoring(broker, consumer, root_path, directory_to_watch)

    print("Observer created and monitoring started.")
    try:
        observer.start()
        start_consumer_listener()
    except KeyboardInterrupt:
        print("Shutting down...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
