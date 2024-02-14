import sys
import pika

def callback(ch, method, properties, body):
    body = eval(body)
    youtube_name = body['youtuber_name']
    video_name = body['video_name']
    print(f"New video from {youtube_name}: {video_name}")

def recieveNotifications(name:str)->None:
    """Recieves notifications from the server
        Args:
            name: str: The name of the user"""
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='egress', exchange_type='direct', durable=True)
    channel.queue_declare(queue=name)
    channel.queue_bind(exchange='egress', queue=name, routing_key=name)
    channel.basic_consume(queue=name, on_message_callback=callback, auto_ack=True)
    print("Recieving notifications from server, press CTRL+C to stop")
    channel.start_consuming()
    
def updateSubscription(name:str, action:str, youtuber_name:str)->None:
    """Updates the subscription of the user
        Args:
            name: str: The name of the user
            action: str: The action to be performed (s/u)
            youtuber_name: str: The name of the youtuber"""
    
    print(f"Updating subscription for {name} to {youtuber_name}")
    
    action:bool = True if action == "s" else False

    msg_body:dict[str,str] = {
        "name": name,
        "youtuber_name": youtuber_name,
        "subscribe": action,
    }
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='ingress', exchange_type='direct', durable=True)
    channel.queue_declare(queue='user')
    channel.queue_bind(exchange='ingress', queue='user', routing_key=name)
    channel.basic_publish(exchange='ingress', routing_key=name, body=str(msg_body))
    
    print("Request sent to server.")
    
    connection.close()
    

if __name__ == '__main__':
    if (len(sys.argv) != 2) and (len(sys.argv) != 4):
        print("Usage: User.py <user_name> [s/u] [youtuber_name]")
        sys.exit(1)
    name = sys.argv[1]
    if len(sys.argv) == 4:
        updateSubscription(name, sys.argv[2], sys.argv[3])
    recieveNotifications(name)