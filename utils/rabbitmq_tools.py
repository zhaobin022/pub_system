__author__ = 'zhaobin022'
import pika
def get_rabbitmq_connect():

    credentials = pika.PlainCredentials('guest', 'guest')
    # Á´½Órabbit
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    return connection