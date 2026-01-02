import json
import boto3
from typing import List, Dict

class OutboxRelayHandler:
    def __init__(self):
        self.event_bus = boto3.client('events')

    def handle(self, event: Dict):
        """
        Lee los registros provenientes de DynamoDB Streams
        """
        entries = []
        
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                # Deserializamos la imagen de DynamoDB
                new_image = record['dynamodb']['NewImage']
                
                # Transformamos el formato de DynamoDB a JSON plano
                payload = {
                    "transaction_id": new_image['id']['S'],
                    "amount": float(new_image['amount']['N']),
                    "merchant_id": new_image['merchant_id']['S'],
                    "status": new_image['status']['S']
                }

                entries.append({
                    'Source': 'payments.outbox',
                    'DetailType': 'TransactionCreated',
                    'Detail': json.dumps(payload),
                    'EventBusName': 'default'
                })

        if entries:
            # Publicamos en batch para mayor eficiencia
            self.event_bus.put_events(Entries=entries)
            print(f"Relayed {len(entries)} events to EventBridge")

# Punto de entrada para la nueva Lambda
relay = OutboxRelayHandler()
def handler(event, context):
    relay.handle(event)