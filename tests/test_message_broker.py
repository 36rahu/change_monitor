import unittest
from message_broker.broker import MessageBroker, Producer, Consumer

class TestMessageBroker(unittest.TestCase):
    """Test Cases for Message Broker"""

    def setUp(self):
        """Sets up the MessageBroker, Producer, and Consumers for testing."""
        self.broker = MessageBroker()
        self.producer = Producer(self.broker)
        self.consumer = Consumer("TestConsumer")
        self.consumer2 = Consumer("NewConsumer")

    def test_simple_subscription(self):
        """Tests subscribing to a topic and receiving a message."""
        self.consumer.subscribe(self.broker, "topicA")
        self.producer.publish("topicA", "Message1")
        self.assertEqual(self.consumer.messages, [("topicA", "Message1")])

    def test_wildcard_subscription(self):
        """Tests subscribing to a topic with a wildcard and receiving messages."""
        self.consumer.subscribe(self.broker, "topic~")
        self.producer.publish("topicA", "Message1")
        self.producer.publish("topicB", "Message2")
        self.assertEqual(self.consumer.messages, [("topicA", "Message1"), ("topicB", "Message2")])

    def test_only_wildcard_subscription(self):
        """Tests subscribing to all topics with a wildcard subscription."""
        self.consumer.subscribe(self.broker, "~")
        topic_and_message_list = [('topic1', 'Message 1'),
                                 ('topic2', 'Message 2'),
                                 ('topic3', 'Message 3'),
                                 ('topic4', 'Message 4')]
        for topic, message in topic_and_message_list:
            self.producer.publish(topic, message)
        self.assertEqual(self.consumer.messages, topic_and_message_list)

    def test_no_matching_subscription(self):
        """Tests subscription with no matching topics."""
        self.consumer.subscribe(self.broker, "topic~")
        self.producer.publish("anotherTopic", "Message1")
        self.assertEqual(self.consumer.messages, [])

    def test_multiple_consumer(self):
        """Tests multiple consumers subscribing to different topics."""
        self.consumer.subscribe(self.broker, "ab~")
        self.consumer2.subscribe(self.broker, "b~")
        self.producer.publish("abc", "Message1")
        self.assertEqual(self.consumer.messages, [("abc", "Message1")])
        self.assertEqual(self.consumer2.messages, [])

    def test_unsubscribe(self):
        """Tests unsubscribing from a topic."""
        self.consumer.subscribe(self.broker, "topicA")
        self.producer.publish("topicA", "Message1")
        self.assertEqual(self.consumer.messages, [("topicA", "Message1")])

        # Unsubscribe and publish again
        self.broker.unsubscribe(self.consumer, "topicA")
        self.producer.publish("topicA", "Message2")
        self.assertEqual(self.consumer.messages, [("topicA", "Message1")])

    def test_invalid_subscription_topic(self):
        """Tests invalid subscription topics."""
        with self.assertRaises(ValueError):
            self.consumer.subscribe(self.broker, "")
        with self.assertRaises(ValueError):
            self.consumer.subscribe(self.broker, "   ")
        with self.assertRaises(ValueError):
            self.consumer.subscribe(self.broker, None)
        with self.assertRaises(ValueError):
            self.consumer.subscribe(self.broker, 1234)

    def test_invalid_publish_topic(self):
        """Tests invalid publish topics."""
        with self.assertRaises(ValueError):
            self.producer.publish("", "Message1")
        with self.assertRaises(ValueError):
            self.producer.publish("   ", "Message2")
        with self.assertRaises(ValueError):
            self.producer.publish(None, "Message3")
        with self.assertRaises(ValueError):
            self.producer.publish(1234, "Message4")

    def test_list_subscriptions(self):
        """Tests listing all current subscriptions."""
        self.consumer.subscribe(self.broker, "topicA")
        self.consumer.subscribe(self.broker, "topicB")
        self.consumer2.subscribe(self.broker, "topicA")
        subscriptions = self.broker.list_subscriptions()
        expected = {
            "topicA": ["TestConsumer", "NewConsumer"],
            "topicB": ["TestConsumer"]
        }
        self.assertEqual(subscriptions, expected)
