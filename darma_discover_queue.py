#!/usr/bin/python3
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
        
channel.queue_declare(queue='ADAMProcessingQueue')
        
channel.basic_publish(exchange='',routing_key='ADAMProcessingQueue',body='New IP to Discover!')
                              
print (" [x] Sent 'New IP to discover!'")
connection.close()




