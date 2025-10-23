import pika
import time
import uuid

def test_publish_and_consume_rabbitmq(config):
    url = config['rabbitmq'].get('url') or "amqp://guest:guest@localhost:5672/"
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    queue = config['rabbitmq'].get('queue', 'test_queue')
    ch.queue_declare(queue=queue, durable=False, auto_delete=True)
    corr_id = str(uuid.uuid4())
    message = {"hello": "world", "id": corr_id}
    ch.basic_publish(exchange="", routing_key=queue, body=str(message))

    # consume (poll for message) with a short timeout
    method_frame, header_frame, body = ch.basic_get(queue=queue, auto_ack=True)
    assert body is not None
    assert corr_id in body.decode()
    conn.close()

