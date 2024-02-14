import pika
import logging

logging.basicConfig(filename="./logs/YoutuberServer.log", level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriberMap:

    def __init__(self):
        self.subscribers:dict[str, set[str]] = dict()

    def addSubscriber(self, user:str, youtuber:str)->None:
        if youtuber not in self.subscribers:
            print(f"{youtuber} does not exist")
            return
        self.subscribers[youtuber].add(user)
        print(f"{user} has subscribed to {youtuber}")

    def removeSubscriber(self, user:str, youtuber:str)->None:
        if youtuber not in self.subscribers:
            print(f"{youtuber} does not exist")
            return
        self.subscribers[youtuber].remove(user)
        print(f"{user} has unsubscribed from {youtuber}")

    def addYoutuber(self, youtuber:str)->None:
        if youtuber in self.subscribers:
            return
        self.subscribers[youtuber] = set()
        logging.info(f"In function addYoutuber: Added {youtuber} to the list of youtubers")

    def getSubscribers(self, youtuber:str)->list[str]:
        if youtuber not in self.subscribers:
            logging.info(f"In function getSubscriber: {youtuber} does not exist")
            return
        return list(self.subscribers[youtuber])
    
subscriberMap:SubscriberMap

def consumeYoutuberRequests(ch, method, properties, body):
    logging.info(f"In function consumeYoutuberRequests: Got a message {body}")
    body = eval(body)
    youtuber_name = body['name']
    video_name = body['video_name']
    print(f"Got a message from {youtuber_name}: {video_name}")
    subscriberMap.addYoutuber(youtuber_name)
    for user in subscriberMap.getSubscribers(youtuber_name):
        notifyUsers(user, youtuber_name, video_name)

def consumeUserRequests(ch, method, properties, body):
    logging.info(f"In function consumeUserRequests: Got a message {body}")
    body = eval(body)
    user_name = body['name']
    youtuber_name = body['youtuber_name']
    subscribe = body['subscribe']
    print(f"Updating subscription for {user_name} to {youtuber_name}")
    if subscribe:
        subscriberMap.addSubscriber(user_name, youtuber_name)
    else:
        subscriberMap.removeSubscriber(user_name, youtuber_name)

def notifyUsers(user:str, youtuber:str, video:str)->None:
    print(f"Sending notification to {user} for {youtuber}'s new video {video}")
    logging.info(f"In function notifyUsers: Sending notification to {user} for {youtuber}'s new video {video}")

def main():

    global subscriberMap
    subscriberMap = SubscriberMap()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost', port = 5672))
    channel = connection.channel()
    logging.info(f"In function main: Created the connection and channel")

    channel.exchange_declare(exchange='ingress', exchange_type='direct', durable=True)
    channel.basic_consume(queue='youtuber', on_message_callback=consumeYoutuberRequests, auto_ack=True)
    channel.basic_consume(queue='user', on_message_callback=consumeUserRequests, auto_ack=True)
    logging.info(f"In function main: Declared the exchange and queues")

    # channel.queue_declare(queue='user')
    # channel.queue_bind(exchange='ingress', queue='user', routing_key='user')
    
    channel.start_consuming()

if __name__ == '__main__':
    main()