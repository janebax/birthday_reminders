# Use environment variables specified in .env
include .env

# Local dev commands
pytest:
	@poetry run pytest --cov=app tests/  
	
lint:
	@poetry run black .
	@poetry run isort .
	@poetry run pylint app

local_run: 
	@poetry run python ./app/send_message.py

# Docker commands
up:
	@docker build -t app .

down:
	@docker image rm app

get_image_id:
	'IMAGE_ID=$(docker images -q app)' >> app/.env

# AWS service commands
ecr_login:
	@aws ecr get-login-password --region ${AWS_REGION} | docker login \
    --username AWS --password-stdin ${ACCOUNT_NUMBER}.dkr.ecr.${AWS_REGION}.amazonaws.com

create_ecr:
	@aws ecr create-repository --repository-name birthday_reminders --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

push_to_ecr:
	@docker tag ${IMAGE_ID} ${ACCOUNT_NUMBER}.dkr.ecr.${AWS_REGION}.amazonaws.com/birthday_reminders:v2
	@docker push ${ACCOUNT_NUMBER}.dkr.ecr.${AWS_REGION}.amazonaws.com/birthday_reminders:v2

create_lambda_function:
	@aws lambda create-function --region ${AWS_REGION} --function-name birthday_reminders_v1  \
    --package-type Image  \
    --code ImageUri=${ACCOUNT_NUMBER}.dkr.ecr.${AWS_REGION}.amazonaws.com/birthday_reminders:v1   \
    --role ${IAM_ROLE_ARN} \
	--architectures arm64

create_daily_rule:
	@aws events put-rule --schedule-expression "cron(0 12 * * ? *)" --name daily_noon