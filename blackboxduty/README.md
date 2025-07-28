# BlackBoxDuty

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders:

- statemachine - Definition for the state machine that orchestrates the workflow.
- template.yaml - A template that defines the application's AWS resources.
- samconfig.toml - This file stores configuration settings for AWS SAM CLI deployments, such as parameter values, stack names, and deployment options, allowing for repeatable and automated deployments without manual prompts.

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda.

To use the SAM CLI, you need the following tools:

- SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the BlackBoxDuty application. The second command will package and deploy the application to AWS, with a series of prompts.

## Use the SAM CLI to build locally

Build the state machine application with the `sam build --use-container` command.

```bash
blackboxduty$ sam build --use-container
```

The SAM CLI creates a deployment package, and saves it in the `.aws-sam/build` folder.

## Deployment Parameters

When deploying BlackBoxDuty, you can customize the following parameters in `template.yaml`:

- **BlackBoxDutyTableName**  
  _Type:_ String  
  _Default:_ `BlackBoxDutyTable`  
  _Description:_ Name of the DynamoDB table to store metadata about processed SecurityHub and GuardDuty findings.  
  _Constraints:_ 3-255 characters; alphanumeric, underscores, hyphens, and periods.

- **BlackBoxDutyS3BucketName**  
  _Type:_ String  
  _Description:_ Name of the S3 bucket to store artifacts, including SecurityHub and GuardDuty findings.  
  _Constraints:_ 3-63 characters; lowercase letters, numbers, and hyphens.

You will be prompted to provide these values during `sam deploy --guided`, or create override for them in the `samconfig.toml` deployment configuration.

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
sam delete --stack-name "BlackBoxDuty"
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.
