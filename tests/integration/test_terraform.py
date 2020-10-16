import os
import unittest
from localstack.utils.aws import aws_stack
from localstack.utils.common import run

BUCKET_NAME = 'tf-bucket'
QUEUE_NAME = 'tf-queue'


class TestTerraform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        base_dir = os.path.join(os.path.dirname(__file__), 'terraform')
        if not os.path.exists(os.path.join(base_dir, '.terraform')):
            run('cd %s; terraform init -input=false' % base_dir)
        run('cd %s; terraform plan -out=tfplan -input=false' % (base_dir))
        run('cd %s; terraform apply -input=false tfplan' % (base_dir))

    @classmethod
    def tearDownClass(cls):
        base_dir = os.path.join(os.path.dirname(__file__), 'terraform')
        run('cd %s; terraform destroy -auto-approve' % (base_dir))

    def test_bucket_exists(self):
        s3_client = aws_stack.connect_to_service('s3')
        response = s3_client.head_bucket(Bucket=BUCKET_NAME)
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_sqs(self):
        sqs_client = aws_stack.connect_to_service('sqs')
        queue_url = sqs_client.get_queue_url(QueueName=QUEUE_NAME)['QueueUrl']
        response = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])

        self.assertEqual(response['Attributes']['DelaySeconds'], '90')
        self.assertEqual(response['Attributes']['MaximumMessageSize'], '2048')
        self.assertEqual(response['Attributes']['MessageRetentionPeriod'], '86400')
        self.assertEqual(response['Attributes']['ReceiveMessageWaitTimeSeconds'], '10')