# Run 'brew install graphviz' on terminal to install on MacOS
from diagrams import Diagram
from diagrams.aws.compute import EC2ContainerRegistry, Lambda
from diagrams.aws.integration import Eventbridge
from diagrams.aws.integration import SimpleNotificationServiceSns as Sns
from diagrams.programming.language import Python

with Diagram("", filename="birthday_reminder", show=False):
    event_rule = Eventbridge("EventBridge Daily Trigger")
    code = Python("/app code")
    ecr = EC2ContainerRegistry("Docker Image in ECR")
    lam = Lambda("Lambda")
    message = Sns("Reminder using SNS")
    event_rule >> lam
    code >> ecr >> lam >> message
