# BlackBoxDuty

BlackBoxDuty is a serverless application for orchestrating and managing AWS SecurityHub and GuardDuty findings. The project is designed for deployment with the AWS SAM CLI.

Project structure:

- `statemachine/` – State machine definition for workflow orchestration
- `functions/` – Lambda function handlers for GuardDuty operations
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

## Lambda Functions

BlackBoxDuty includes two AWS::Serverless::Function resources that handle GuardDuty operations:

### GuardDuty Get Findings Function
- **Purpose**: Retrieves detailed GuardDuty findings with multi-region support
- **Handler**: `functions/guardduty-get-findings/app.lambda_handler`
- **Runtime**: Python 3.13
- **Permissions**: AmazonGuardDutyReadOnlyAccess
- **Parameters**:
  - `DetectorId`: GuardDuty detector ID
  - `FindingRegion`: AWS region where the finding is located
  - `FindingIds`: List of finding IDs to retrieve

### GuardDuty List Detectors Function
- **Purpose**: Lists GuardDuty detectors with multi-region support
- **Handler**: `functions/guardduty-list-detectors/app.lambda_handler`
- **Runtime**: Python 3.13
- **Permissions**: AmazonGuardDutyReadOnlyAccess
- **Parameters**:
  - `FindingRegion`: AWS region where the finding is located

## Cleanup

To remove the deployed application, run:

```bash
sam delete --stack-name "BlackBoxDuty"
```

## Tests

The `AWS::Serverless::Function` resources have unit test coverage (pytest), executable adjacent to the Lambda function handler definition.

To run tests for the GuardDuty Get Findings function:
```bash
cd functions/guardduty-get-findings
python -m pytest test_app.py -v
```

To run tests for the GuardDuty List Detectors function:
```bash
cd functions/guardduty-list-detectors
python -m pytest test_app.py -v
```

## CloudWatch MCP Server (Claude Code Integration)

The project root includes an `.mcp.json` that configures the [Amazon CloudWatch MCP Server](https://awslabs.github.io/mcp/servers/cloudwatch-mcp-server) for use with Claude Code. This lets Claude query CloudWatch Logs directly from the project — useful for debugging Lambda function executions and Step Functions state machine runs.

### Prerequisites

- Docker installed and running
- A `blackboxduty` AWS profile in `~/.aws/config` with read-only CloudWatch Logs permissions

### AWS Profile Setup

Create a dedicated `blackboxduty` profile with minimal permissions. The recommended approach is to attach the AWS managed policy:

```
arn:aws:iam::aws:policy/CloudWatchLogsReadOnlyAccess
```

Add the profile to `~/.aws/config`:

```ini
[profile blackboxduty]
region = ca-central-1
# ... credential source (IAM role, SSO, access key, etc.)
```

### Usage

When Claude Code loads this project, the MCP server starts automatically via Docker. Claude can then query CloudWatch Logs for Lambda function logs and Step Functions execution logs without requiring manual AWS Console access.

The `.mcp.json` mounts `~/.aws` as read-only and passes `AWS_PROFILE=blackboxduty` and `AWS_REGION=ca-central-1` to the container.

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for more on the SAM specification, CLI, and serverless concepts.
