import os
import pika
import rdflib
from worker_util import get_cache_filename


class AbstractWorker():

    queue_name = None

    def start_worker(self):
        connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue=self.__class__.queue_name, durable=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        # channel.basicQos(1)

        def callback(ch, method, properties, body):
            print(' [x] Received %r' % body)
            self.process_data(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(callback, queue=self.__class__.queue_name)
        channel.start_consuming()

    def send_to_queue(self, queue_name, body):
        connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=body)

        print(' [x] Sent %r' % body)

        connection.close()

    def get_new_model(self):
        return rdflib.Graph()

    def open_model(self, model_filename):
        model = rdflib.Graph()
        if os.path.isfile(model_filename):
            model_format = rdflib.util.guess_format(model_filename)
            model.parse(model_filename, format=model_format)
        return model

    def notify_update(self, filename):
        self.send_to_queue('update', filename)

    def write_model(self, model, model_filename):
        model.serialize(destination=model_filename, format='turtle')

    def get_model_filename(self, url):
        # url = url.decode('utf-8')
        queue_name_shortened = self.__class__.queue_name.split('/')[-1]
        return get_cache_filename(url) + '.' + queue_name_shortened

    def write_and_merge_model(self, model, filename):
        self.write_model(model, filename)
        self.notify_update(filename)

    def process_data(self, url):
        pass
