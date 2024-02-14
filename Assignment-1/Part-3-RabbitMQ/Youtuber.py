import sys
import pika

def publish_video(name:str, video_name:str)->None:
    """Publishes the video name to the youtuber's channel
        Args: 
            name: str: The name of the youtuber
            video_name: str: The name of the video"""
    
    print(f"Publishing {video_name} to {name}'s channel")

    msg_body:dict[str, str] = {
        "name": name,
        "video_name": video_name
    }

    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='ingress', exchange_type='direct', durable=True)
    channel.queue_declare(queue='youtuber')
    channel.queue_bind(exchange='ingress', queue='youtuber', routing_key=name)
    channel.basic_publish(exchange='ingress', routing_key=name, body=str(msg_body))

    print("Request sent to server.")

    connection.close()

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("Usage: Youtuber.py <youtuber_name> <video_name> ")
        sys.exit(1)
    name:str = sys.argv[1]
    video_name:str = " ".join(sys.argv[2:])
    publish_video(name, video_name)
    

    