⚠️ **This project is currently under development.** ⚠️

# BlackBoxDuty: "Cloud flight recorder for GuardDuty"

## Overview

BlackBoxDuty is an open-source solution designed to provide long-term retention and easy retrieval of AWS GuardDuty findings. By default, GuardDuty findings are only retained for 90 days, which can be a challenge for organizations that need to meet compliance, audit, or forensic investigation requirements. BlackBoxDuty captures findings in real time and stores them durably in DynamoDB, ensuring that your security evidence is always available when you need it.

### Key Features

- **Long-term retention**: Never lose critical GuardDuty findings due to AWS retention limits.
- **Compliance-ready**: Easily gather evidence for audits such as SOC 2, ISO 27001, and more.
- **Real-time ingestion**: Findings are captured as soon as they are generated.
- **Simple integration**: Built with [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) for easy deployment and extension.

To deploy the State Machine, follow the instructions in [README.md](/blackboxduty/README.md).

## Using DynamoDB PartiQL Queries for Compliance & Audit

BlackBoxDuty archives Security Hub findings associted with GuardDuty in an S3 bucket, and stores the assocaited metadata in a DynamoDB table (`BlackBoxDutyTable`). You can use PartiQL queries to:

- Retrieve historical findings for specific time periods
- Search for findings by unique identifiers (ARNs)
- Gather evidence for compliance frameworks (e.g., SOC 2, ISO 27001)
- Support incident response and forensic investigations

### Example: Retrieve All Findings Since a Specific Date

This query returns all findings created after January 1, 2025:

```
SELECT * FROM "BlackBoxDutyTable" WHERE "FindingCreatedAt" >= '2025-01-01T00:00:00Z'
```

**Use case:** During a SOC 2 audit, you may be asked to provide evidence of all security findings within a given period. This query allows you to quickly export all relevant findings for the requested timeframe.

### Example: Retrieve a Specific Finding by ID

Replace REGION, ACCOUNT_ID, DETECTOR_ID, and FINDING_ID with the appropriate values for your use case.

```
SELECT * FROM "BlackBoxDutyTable" WHERE "Id" = 'arn:aws:securityhub:REGION::product/aws/guardduty/arn:aws:guardduty:REGION:ACCOUNT_ID:detector/DETECTOR_ID/finding/FINDING_ID'
```

**Use case:** If an auditor or investigator requests details about a specific incident, you can use this query to retrieve the exact finding and provide full evidence, including timestamps and context.

## Why This Matters for SOC 2 and Other Compliance Frameworks

SOC 2 and similar standards require organizations to retain security evidence and demonstrate effective monitoring and response to threats. BlackBoxDuty makes it easy to:

- Prove that you are capturing and retaining all GuardDuty findings
- Provide auditors with direct evidence of findings and responses
- Support incident investigations with historical data

By using BlackBoxDuty and DynamoDB PartiQL queries, you can streamline your compliance and audit processes, reduce manual effort, and ensure you always have the evidence you need.
