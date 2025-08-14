# BlackBoxDuty

BlackBoxDuty is a serverless application for orchestrating and managing AWS SecurityHub and GuardDuty findings. The project is designed for deployment with the AWS SAM CLI.

Project structure:

- `statemachine/` – State machine definition for workflow orchestration
- `template.yaml` – AWS resource definitions
- `samconfig.toml` – Deployment configuration for repeatable, automated deployments

## Deploying BlackBoxDuty

The AWS SAM CLI extends the AWS CLI to build and test Lambda applications locally using Docker. Before you begin, ensure you have:

- [AWS SAM CLI installed](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Docker installed](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy for the first time, run:

```bash
sam build --use-container
sam deploy --guided
```

`sam build` compiles the application. `sam deploy --guided` packages and deploys it to AWS, prompting for required parameters.

## Local Build

To build the state machine application locally:

```bash
sam build --use-container
```

The deployment package will be created in the `.aws-sam/build` directory.

## Deployment Parameters

You can customize these parameters in `template.yaml`:

- **BlackBoxDutyTableName**

  - Type: String
  - Default: `BlackBoxDutyTable`
  - Description: DynamoDB table for storing SecurityHub and GuardDuty findings metadata
  - Constraints: 3–255 characters; alphanumeric, underscores, hyphens, periods

- **BlackBoxDutyS3BucketName**
  - Type: String
  - Description: S3 bucket for storing artifacts (including findings)
  - Constraints: 3–63 characters; lowercase letters, numbers, hyphens

You will be prompted for these values during `sam deploy --guided`, or you can override them in `samconfig.toml`.

## Cleanup

To remove the deployed application, run:

```bash
sam delete --stack-name "BlackBoxDuty"
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for more on the SAM specification, CLI, and serverless concepts.
