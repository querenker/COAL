import os
import pika
import rdflib


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

        channel.queue_declare(queue=queue_name)

        channel.basic_publish(exchange='',
                              routing_key=queue_name
                              body=body)

        print(' [x] Sent %r' % body)

        connection.close()

    def open_model(self, model_filename):
        model = rdflib.Graph()
        if os.path.isfile(model_filename):
            model_format = rdflib.util.guess_format(model_filename)
            model.parse(model_filename, format=model_format)
        return model

    def write_model(self, model, model_filename):
        model.serialize(destination=model_filename, format='turtle')

    def process_data(url):
        pass
