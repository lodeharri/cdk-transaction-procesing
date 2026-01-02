import boto3
import json
import os

class EventBridgeBus:
    def __init__(self):
        self.client = boto3.client('events')

    def publish(self, detail_type, data):
        bus_name = os.environ.get("EVENT_BUS_NAME")
        
        self.client.put_events(
            Entries=[{
                'EventBusName': bus_name,
                'Source': 'some.payments',
                'DetailType': detail_type,
                'Detail': json.dumps(str(data))
            }]
        )