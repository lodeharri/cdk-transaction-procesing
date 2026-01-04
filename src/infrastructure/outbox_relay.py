import json
import os
import boto3

class OutboxRelayHandler:
    def __init__(self):
        self.client = boto3.client('events')
        self.bus_name = os.environ.get("EVENT_BUS_NAME")

    def handle(self, event):
        entries = []
        for record in event['Records']:
            # Solo procesamos nuevas inserciones
            if record['eventName'] == 'INSERT':
                new_image = record['dynamodb']['NewImage']
                
                # VALIDACIÓN CRÍTICA: Solo notificamos si fue aprobado
                status = new_image['status']['S']
                if status == "APPROVED":
                    payload = {
                        "transaction_id": new_image['id']['S'],
                        "correlation_id": new_image['correlation_id']['S'],
                        "amount": new_image['amount']['N'],
                        "merchant_id": new_image['merchant_id']['S']
                    }

                    print(f'bus name: {self.bus_name}')
                    print(f'payload: {payload}')
                    entries.append({
                        'EventBusName': self.bus_name,
                        'Source': 'some.payments',
                        'DetailType': 'PaymentConfirmed',
                        'Detail': json.dumps(payload)
                    })
        
        if entries:
            self.client.put_events(Entries=entries)
            print(f"Relay: Enviados {len(entries)} eventos al bus.")

# Punto de entrada para AWS
relay_handler = OutboxRelayHandler()
def handler(event, context):
    return relay_handler.handle(event)