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

## Supercharge Your Security Investigations with AWS MCP Servers

Transform your BlackBoxDuty security investigations from manual SQL queries to intelligent, conversational analysis using [Amazon DynamoDB MCP Server](https://awslabs.github.io/mcp/servers/dynamodb-mcp-server). This powerful integration brings AI-assisted security analysis directly to your BlackBoxDuty findings, enabling faster incident response, deeper threat insights, and streamlined compliance reporting.

### Why AWS MCP Servers Are a Game-Changer for Security Teams

**🚀 Zero Learning Curve**
- No PartiQL or SQL expertise required
- Natural language queries that security analysts can use immediately
- AI understands security context and terminology

**🔍 Advanced Analysis Capabilities**
- Automatic pattern detection across historical findings
- Cross-reference multiple data points for comprehensive investigations
- Generate executive summaries and technical deep-dives from the same data

**⚡ Faster Incident Response**
- Interactive follow-up questions during active investigations
- Real-time correlation of related security events
- Immediate context switching between different investigation angles

**📊 Intelligent Compliance Reporting**
- Generate audit-ready reports with natural language requests
- Automatically format findings for different stakeholder audiences
- Create trending analysis and risk assessments on-demand

### Setup

1. Install and configure the DynamoDB MCP Server following the [official documentation](https://awslabs.github.io/mcp/servers/dynamodb-mcp-server)
2. Configure your GenAI Client - such as Claude Desktop - Developer settings for **Local MCP servers**
3. Ensure your AWS credentials have read access to the DynamoDB table

#### Claude Desktop Configuration Example

Add this configuration to your Claude Desktop MCP settings file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "awslabs.dynamodb-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--interactive",
        "--env",
        "AWS_PROFILE=security-auditor-read",
        "--env",
        "AWS_REGION=ca-central-1",
        "--volume",
        "/Users/<username>/.aws:/app/.aws",
        "public.ecr.aws/awslabs-mcp/awslabs/dynamodb-mcp-server:latest"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Note:** Update the `AWS_PROFILE`, `AWS_REGION`, and volume path to match your local AWS configuration.

### Real-World Investigation Scenarios

Transform complex security investigations with these example prompts:

#### **🔥 Emergency Response: Active Threat Investigation**
```
"We just detected suspicious activity on EC2 instance i-1234567890abcdef0. Show me all GuardDuty findings for this instance in the last 48 hours, correlate with any related network or IAM findings, and provide an incident severity assessment."
```

**Impact:** Reduces incident triage time from hours to minutes with comprehensive context.

#### **📈 Executive Briefing: Security Posture Summary**
```
"Create an executive summary of our security findings for the last quarter. Include trend analysis, top threats, mean time to detection improvements, and recommendations for board presentation."
```

**Impact:** Transforms raw security data into business-relevant insights for leadership.

#### **🕵️ Forensic Deep-Dive: Attack Pattern Analysis**
```
"Analyze all cryptocurrency mining-related GuardDuty findings from the past 6 months. Show me attack vectors, affected resources, geographic patterns, and suggest preventive controls."
```

**Impact:** Enables proactive security hardening based on historical attack patterns.

#### **✅ Compliance Audit: Evidence Collection**
```
"Generate SOC 2 Type II evidence for our security monitoring controls. Show detection coverage, response times, and remediation tracking for all high-severity findings in 2024."
```

**Impact:** Streamlines audit preparation with automatically formatted compliance evidence.

### The MCP Advantage: Beyond Traditional Querying

| Traditional PartiQL Approach | AWS MCP Server Approach |
|----------------------------|------------------------|
| Static queries requiring SQL knowledge | Conversational, adaptive investigation |
| Manual data interpretation | AI-powered pattern recognition |
| One-dimensional analysis | Multi-faceted correlation and context |
| Technical reports only | Stakeholder-appropriate formatting |
| Reactive querying | Proactive threat intelligence |

## Why This Matters for SOC 2 and Other Compliance Frameworks

SOC 2 and similar standards require organizations to retain security evidence and demonstrate effective monitoring and response to threats. BlackBoxDuty makes it easy to:

- Prove that you are capturing and retaining all GuardDuty findings
- Provide auditors with direct evidence of findings and responses
- Support incident investigations with historical data

By using BlackBoxDuty and DynamoDB PartiQL queries, you can streamline your compliance and audit processes, reduce manual effort, and ensure you always have the evidence you need.
