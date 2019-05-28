'''
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from Framework.Utils.print_Utils import print_info, print_error, print_exception
try:
    from kafka import KafkaConsumer
    from kafka import KafkaProducer
    from kafka import TopicPartition
    from kafka.admin import KafkaAdminClient, NewTopic, NewPartitions
    from kafka.errors import KafkaError
except ImportError as err:
    print_error("Module kafka is not installed, Refer exception below")
    print_exception(err)

class WarriorKafkaConsumer():
    """
    This class contains all kafka consumer methods
    """
    def __init__(self, *topics, **configs):
        """
        Create Kafka Consumer object
        """
        print_info("creating kafka consumer")
        try:
            self.kafka_consumer = KafkaConsumer(*topics, **configs)
        except KafkaError as exc:
            print_error("Kafka consumer - Exception during connecting to broker - {}".format(exc))

    def subscribe_to_topics(self, topics, **kwargs):
        """
        Subscribe to list of specified topics.
        Arguments:
          topics(list): list of topic names to subscribe
          pattern(list): list of topic name patterns to subscribe
          listener(func): callback function
        Returns:
          result(bool) : False if exception occures, True otherwise
        """
        pattern = kwargs.get("pattern", None)
        listener = kwargs.get("listener", None)
        print_info("subscribe to topics {}".format(topics))
        try:
            self.kafka_consumer.subscribe(topics=topics,
                                          pattern=pattern,
                                          listener=listener)
            result = True
        except KafkaError as exc:
            print_error("Exception during subscribing to topics - {}".format(exc))
            result = False
        return result

    def unsubscribe_to_topics(self):
        """
        Unsubscribe to all topics.
        Arguments: None.
        Returns:
          result(bool) : False if exception occures, True otherwise
        """
        print_info("unsubscribe to all topics")
        try:
            self.kafka_consumer.unsubscribe()
            result = True
        except KafkaError as exc:
            print_error("Exception during unsubscibing to topics - {}".format(exc))
            result = False
        return result

    def assign_partitions(self, partitions):
        """
        Assign partitions to consumer.
        Arguments:
          partitions(list) : list of [topic, partition] lists
            example : [[topic1,1], [topic2,1]]
        Returns:
            None.
        """
        print_info("assigning partitions to consumer {}".format(partitions))
        topic_partitions = [TopicPartition(topic=tup[0], partition=tup[1]) for tup in partitions]
        try:
            self.kafka_consumer.assign(topic_partitions)
            result = True
        except KafkaError as exc:
            print_error("Exception during assiging partitions - {}".format(exc))
            result = False
        return result

    def seek_to_position(self, topic, partition, offset):
        """
        Seek to the given offset.
        Arguments:
          topic(str): topic name
          partition(int): partition number
          offset(int): offset number
        Returns:
          result(bool) : False if exception occures, True otherwise
        """
        print_info("seeking to position {}:{}:{}".format(topic, partition, offset))
        topic_partition = TopicPartition(topic=topic, partition=partition)
        try:
            self.kafka_consumer.seek(partition=topic_partition, offset=offset)
            result = True
        except KafkaError as exc:
            print_error("Exception during seek - {}".format(exc))
            result = False
        return result

    def get_messages(self, get_all_messages=False, **kwargs):
        """
        Get messages from consumer.
        Arguments:
          get_all_messages(bool): set this to True to get all the messages, seeks to the beginning.
                                   Defaults to False.
          timeout(int): timeout in milliseconds
          max_records(int): maximum messages to fetch
        Returns:
          messages(list): messages from the consumer
        """
        timeout_ms = kwargs.get("timeout", 0)
        max_records = kwargs.get("max_records", None)
        messages = []
        msg_pack = {}
        print_info("get messages published to subscribed topics")
        try:
            if get_all_messages:
                self.kafka_consumer.seek_to_beginning()
            msg_pack = self.kafka_consumer.poll(timeout_ms, max_records)
        except KafkaError as exc:
            print_error("Exception occured in get_messages - {}".format(exc))

        for topic, message_list in msg_pack.items():
            for message in message_list:
                messages.append(message.value)
        return messages

    def get_topics(self):
        """
        Get subscribed topics of the consumer.
        Arguments:
          None.
        Returns:
          topic_list(list of lists): list of [topic, partition] lists
            example : [[topic1,1], [topic2,2]]
        """
        print_info("get all the topics consumer is subscribed to")
        try:
            topic_partitions = self.kafka_consumer.assignment()
            topic_list = [[topic_partition.topic, topic_partition.partition] \
                       for topic_partition in topic_partitions]
        except KafkaError as exc:
            print_error("Exception during getting assigned partitions - {}".format(exc))
            topic_list = None
        return topic_list

class WarriorKafkaProducer():
    """
    This class contains all kafka producer methods
    """
    def __init__(self, **configs):
        """
        Create kafka producer object
        """
        print_info("Creating kafka producer")
        try:
            self.kafka_producer = KafkaProducer(**configs)
        except KafkaError as exc:
            print_error("kafka producer - Exception during connecting to broker - {}".format(exc))

    def send_messages(self, topic, value=None, **kwargs):
        """
        Publish messages to the desired topic
        Arguments:
          topic(str): topic name to publish messages
          partition(int): partition nubmer
          key(str): key name
          value(str): message to publish
        Returns:
          result(bool) : False if exception occures, True otherwise
        """
        partition = kwargs.get("partition", None)
        headers = kwargs.get("headers", None)
        timestamp = kwargs.get("timestamp", None)
        key = kwargs.get("key", None)
        print_info("publishing messages to the topic")
        try:
            self.kafka_producer.send(topic=topic,
                                     value=value,
                                     partition=partition,
                                     key=key,
                                     headers=headers,
                                     timestamp_ms=timestamp)
            self.kafka_producer.flush()
            result = True
        except KafkaError as exc:
            print_error("Exception during publishing messages - {}".format(exc))
            result = False
        return result

class WarriorKafkaClient():
    """
    This class contains all kafka admin client related
    methods
    """
    def __init__(self, **configs):
        """
        create a kafka client
        """
        print_info("Creating kafka client")
        try:
            self.kafka_client = KafkaAdminClient(**configs)
        except KafkaError as exc:
            print_error("kafka client - Exception during connecting to broker- {}".format(exc))

    def create_topics(self, topic_sets, **kwargs):
        """
        create topics for the producer or consumer to use
        Arguments:
         topic_sets(list) : list of
         ['topic_name', 'num_partitions', 'replication_factor'] lists
         example : ['topic1',1,1]
         timeout(int): time in milliseconds
        Returns:
          result(bool) : False if exception occures, True otherwise
         None.
        """
        timeout = kwargs.get("timeout", None)
        validate = kwargs.get("validate", False)
        new_topics = [NewTopic(name=tup[0], num_partitions=tup[1],\
                      replication_factor=tup[2]) for tup in topic_sets]
        print_info("creating topics")
        try:
            self.kafka_client.create_topics(new_topics=new_topics,
                                            timeout_ms=timeout,
                                            validate_only=validate)
            result = True
        except KafkaError as exc:
            print_error("Exception during creating topics - {}".format(exc))
            result = False
        return result

    def delete_topics(self, topics, timeout=None):
        """
        Delete topics
        Arguments:
          topics(list): list of topic names
          timeout(int): timeout in milliseconds
        Returns:
          result(bool) : False if exception occures, True otherwise
        """
        print_info("deleting topics {}".format(topics))
        try:
            self.kafka_client.delete_topics(topics=topics,
                                            timeout_ms=timeout)
            result = True
        except KafkaError as exc:
            print_error("Exception during deleting topics - {}".format(exc))
            result = False
        return result

    def create_partitions_in_topic(self, partitions, **kwargs):
        """
        create partitions in topic
        Arguments:
          partitions(list) : list of ['topic_name','num_partitions'] lists
          example : [['topic1',4], ['topic2',5]]
          timeout(int): timeout in milliseconds
        Returns:
          result(bool) : False if exception occures, True otherwise
        """
        timeout = kwargs.get("timeout", None)
        validate = kwargs.get("validate", False)
        topic_partitions = {tup[0]:NewPartitions(total_count=tup[1]) for tup in partitions}
        print_info("creating partitions in topic")
        try:
            self.kafka_client.create_partitions(topic_partitions=topic_partitions,
                                                timeout_ms=timeout,
                                                validate_only=validate)
            result = True
        except KafkaError as exc:
            print_error("Exception during creating partitions - {}".format(exc))
            result = False
        return result
