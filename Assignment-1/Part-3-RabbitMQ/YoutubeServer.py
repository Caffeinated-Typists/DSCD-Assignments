import pika

def callbackFunctionForYoutuber(ch, method, properties, body):
    body = eval(body)
    youtuber_name = body['name']
    video_name = body['video_name']
    print(f"Got a message from {youtuber_name}: {video_name}")

def callbackFunctionForUser(ch, method, properties, body):
    body = eval(body)
    user_name = body['name']
    youtuber_name = body['youtuber_name']
    subscribe = body['subscribe']
    print(f"Updating subscription for {user_name} to {youtuber_name}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost', port = 5672))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='ingress', exchange_type='direct', durable=True)
    channel.basic_consume(queue='youtuber', on_message_callback=callbackFunctionForYoutuber, auto_ack=True)
    channel.basic_consume(queue='user', on_message_callback=callbackFunctionForUser, auto_ack=True)

    # channel.queue_declare(queue='user')
    # channel.queue_bind(exchange='ingress', queue='user', routing_key='user')
    
    channel.start_consuming()

if __name__ == '__main__':
    main()