import aws_cdk as core
import aws_cdk.assertions as assertions

from transaction_processing.transaction_processing_stack import TransactionProcessingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in transaction_processing/transaction_processing_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TransactionProcessingStack(app, "transaction-processing")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
