#producer
import pika
#declaring the credentials needed for connection like host, port, username, password, exchange etc
credentials = pika.PlainCredentials("test","123")
connection= pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials= credentials))
channel= connection.channel()
channel.exchange_declare('test', durable=True, exchange_type='topic')
channel.queue_declare(queue= 'A')
channel.queue_bind(exchange='test', queue='A', routing_key='A')
channel.queue_declare(queue= 'B')
channel.queue_bind(exchange='test', queue='B', routing_key='B')
channel.queue_declare(queue= 'C')
channel.queue_bind(exchange='test', queue='C', routing_key='C')
#messaging to queue named C
message= 'hello consumer!!!!!'
channel.basic_publish(exchange='test', routing_key='C', body= message)
channel.close()
