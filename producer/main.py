import random
from time import sleep, time
import time

import pika
url = 'amqps://ynwbwptb:jv1dmvdqmuEFSABp9fSoZYOAsM5ha69j@goose.rmq2.cloudamqp.com:5671/ynwbwptb'

connection = pika.BlockingConnection(pika.connection.URLParameters(url))
channel = connection.channel()

channel.queue_declare(queue='coada_vietii')

msg_body = {
    'timestamp': "2012-03-16 00:00:00+0000", 'energy': 20.0, 'device_id': 2
}

no = 0
while True:
    msg_body['energy'] = random.uniform(10, 100)
    msg_body['timestamp'] = time.time()
    channel.basic_publish(exchange='', routing_key='coada_vietii', body=str(msg_body))
    print('Sent message ' + str(no))
    no += 1
    sleep(10)

