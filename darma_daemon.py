#!/usr/bin/python3.4
import pika
from daemon import runner



def ADAM_ProcessQueueData(ch, method, properties, body):
    print ("Received %r" % (body,))



class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/tmp/mylog.log'
        self.stderr_path = '/tmp/mylog.error'
        self.pidfile_path =  '/tmp/foo.pid'
        self.pidfile_timeout = 5
    def run(self):
        while True:
            print("*** ADAM Daemon Started!")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            
            channel.queue_declare(queue='ADAMProcessingQueue')
            
            print ('*** ADAM Processing Queue Initialized and Waiting for IPs to discover')
            
            
            channel.basic_consume(ADAM_ProcessQueueData,queue='ADAMProcessingQueue', no_ack=True)
            
            channel.start_consuming()            

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

