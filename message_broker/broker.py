"""
This module implements a simple message broker system with support for wildcard topic matching.

It includes:

1. `MessageBroker`: Manages subscriptions, message publishing, and topic matching.
2. `Producer`: Publishes messages to topics via the `MessageBroker`.
3. `Consumer`: Subscribes to topics and receives messages.

The system allows producers to publish messages and consumers to subscribe to topics, 
with wildcard support for flexible topic matching.
"""

class MessageBroker:
    """
    A simple message broker that allows producers to publish messages to topics 
    and consumers to subscribe to those topics, including support for wildcard topic matching.
    """

    def __init__(self):
        """
        This constructor sets up an empty dictionary to store the subscriptions, 
        where each key is a topic and each value is a list of consumers subscribed to that topic.
        """
        self.subscriptions = {}

    def subscribe(self, consumer, topic):
        """
        Subscribes a consumer to a given topic.

        Args:
            consumer (Consumer): The consumer object to subscribe.
            topic (str): The topic to which the consumer is subscribing.

        Raises:
            ValueError: If the topic is invalid.
        """
        if not self._is_valid_topic(topic):
            raise ValueError(f"Invalid topic: {topic}")
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(consumer)

    def unsubscribe(self, consumer, topic):
        """
        Unsubscribes a consumer from a given topic.

        Args:
            consumer (Consumer): The consumer object to unsubscribe.
            topic (str): The topic from which the consumer is unsubscribing.

        Raises:
            KeyError: If the topic does not exist in the subscriptions.
            ValueError: If the consumer is not subscribed to the topic.
        """
        if topic in self.subscriptions:
            self.subscriptions[topic].remove(consumer)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]

    def publish(self, topic, message):
        """
        Publishes a message to a given topic, notifying all matching subscribers.

        Args:
            topic (str): The topic to which the message is published.
            message (str): The message to be delivered to the subscribers.

        Raises:
            ValueError: If the topic is invalid.
        """
        if not self._is_valid_topic(topic):
            raise ValueError(f"Invalid topic: {topic}")
        for subscription, consumers in self.subscriptions.items():
            if self._matches(subscription, topic):
                for consumer in consumers:
                    consumer.receive_message(topic, message)

    def list_subscriptions(self):
        """
        Lists all current subscriptions and their subscribers.

        Returns:
            dict: A dictionary where keys are topics and values are lists of subscriber names.
        """
        return {topic: [consumer.name for consumer in consumers]
                for topic, consumers in self.subscriptions.items()}

    def _matches(self, subscription, topic):
        """
        Checks if a topic matches a subscription with wildcard support.

        Args:
            subscription (str): The subscription string, which may include a wildcard (~).
            topic (str): The topic string to be matched.

        Returns:
            bool: True if the topic matches the subscription, otherwise False.
        """
        parts = subscription.split("~", 1)
        if len(parts) == 1:
            return subscription == topic
        prefix = parts[0]
        return topic.startswith(prefix)

    def _is_valid_topic(self, topic):
        """
        Validates the topic name to ensure it is a non-empty string.

        Args:
            topic (str): The topic name to validate.

        Returns:
            bool: True if the topic is valid, otherwise False.
        """
        return isinstance(topic, str) and len(topic.strip()) > 0


class Producer:
    """
    A producer that can publish messages to topics via the given message broker.
    """

    def __init__(self, broker):
        """
        Args:
            broker (MessageBroker): The message broker through which the producer
            will publish messages.
        """
        self.broker = broker

    def publish(self, topic, message):
        """
        Publishes a message to a given topic via the message broker.

        Args:
            topic (str): The topic to publish the message to.
            message (str): The message to be published.
        """
        self.broker.publish(topic, message)


class Consumer:
    """
    A consumer that subscribes to topics and receives messages from a message broker.
    """

    def __init__(self, name):
        """
        Args:
            name (str): The name of the consumer.
        """
        self.name = name
        self.messages = []

    def receive_message(self, topic, message):
        """
        Receives a message from a topic and stores it.

        Args:
            topic (str): The topic from which the message was received.
            message (str): The message content.
        """
        self.messages.append((topic, message))
        print("Message recived")
        print(f"Topic: {topic}, Message: {message}")

    def subscribe(self, broker, topic):
        """
        Subscribes the consumer to a topic via the message broker.

        Args:
            broker (MessageBroker): The message broker to handle the subscription.
            topic (str): The topic to subscribe to.
        """
        broker.subscribe(self, topic)
