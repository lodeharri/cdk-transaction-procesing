import aws_cdk as cdk
from aws_cdk import (
    Duration,
    Stack,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    RemovalPolicy,
    aws_apigateway as apigw,
    aws_logs as logs,
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_lambda_event_sources import DynamoEventSource

class TransactionProcessingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        transaction_table = dynamodb.Table(self, "Transactions",
            partition_key=dynamodb.Attribute(name="idempotency_key", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            stream=dynamodb.StreamViewType.NEW_IMAGE
        )

        bus = events.EventBus(self, "TransactionEventBus",
            event_bus_name="TransactionEventBus"
        )

        pydantic_layer = PythonLayerVersion(
            self, "PydanticLayer",
            entry="lambda_layer",  # Carpeta raíz donde está tu requirements.txt
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Capa con Pydantic compilada para Linux",
            bundling={
                "platform": "linux/amd64", # Forzamos arquitectura de AWS Lambda
            }
        )

        self.payment_lambda = _lambda.Function(
            self, "TransactionProcessorFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="infrastructure.handler.handler",
            code=_lambda.Code.from_asset("src"), # Lógica (domain, app, infra)
            layers=[pydantic_layer], # Inyecta la capa con Pydantic
            timeout=Duration.seconds(30),
            environment={
                "TRANSACTION_TABLE": transaction_table.table_name,
                "EVENT_BUS_NAME": bus.event_bus_name,
            }
        )

        relay_lambda = _lambda.Function(self, "OutboxRelayFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="infrastructure.outbox_relay.handler",
            code=_lambda.Code.from_asset("src"), 
            timeout=Duration.seconds(30),
            environment={
                "EVENT_BUS_NAME": bus.event_bus_name,
            }
        )

        transaction_table.grant_read_write_data(self.payment_lambda)
        # bus.grant_put_events_to(self.payment_lambda)
        bus.grant_put_events_to(relay_lambda)

        relay_lambda.add_event_source(DynamoEventSource(
            transaction_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=5,
            retry_attempts=2
        ))

        log_group = logs.LogGroup(
            self, "EventLogGroup",
            log_group_name="/aws/events/transaction-events",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        events.Rule(self, "CatchAllRule",
            event_bus=bus,
            event_pattern=events.EventPattern(
                source=["some.payments"],
                detail_type=["PaymentConfirmed"]
            ),
            targets=[targets.CloudWatchLogGroup(log_group)]
        )

        apigw.LambdaRestApi(self, "TransactionAPI",
            handler=self.payment_lambda,
            proxy=False,
            rest_api_name="Transaction Service"
        ).root.add_method("POST")