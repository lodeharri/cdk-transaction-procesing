import boto3
from decimal import Decimal
import os
from botocore.exceptions import ClientError

class DynamoRepository:
    def __init__(self):
        self.table_name = os.environ.get("TRANSACTION_TABLE")
        self.table = boto3.resource('dynamodb').Table(self.table_name)

    def get_account(self, merchant_id):
        from domain.aggregates.account import Account
        return Account(merchant_id=merchant_id, is_active=True, balance=1000.0)

    def save_transaction(self, tx):
        try:
            self.table.put_item(
                Item={
                    'id': tx.id,
                    'idempotency_key': tx.idempotency_key,
                    'amount': Decimal(str(tx.amount.amount)),
                    'status': tx.status.value,
                    'merchant_id': tx.merchant_id,
                    'correlation_id': tx.correlation_id
                },
                ConditionExpression='attribute_not_exists(idempotency_key)'
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"IDEMPOTENCY_ERROR: {tx.idempotency_key}")
            raise e