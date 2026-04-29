# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## TL;DR

- **Pattern**: EventBridge → Step Functions → Lambda (multi-region GuardDuty calls) → DynamoDB + S3
- **Build**: `sam build --use-container` (requires Docker; outputs to `.aws-sam/build`)
- **Test**: `cd blackboxduty/functions/<function-name> && python -m pytest test_app.py -v`
- **Deploy**: `sam deploy --guided` (prompts for table/bucket names; see `samconfig.toml` for cached values)
- **Cleanup**: `sam delete --stack-name "BlackBoxDuty"`

## Architecture at a Glance

**EventBridge trigger**: Fires on `aws.securityhub` "Security Hub Findings - Imported" events (GuardDuty product only).

**State Machine flow** (`statemachine/blackboxduty.asl.json`):
1. Choice: Branch on Workflow.Status == "NEW" vs. existing notes
2. Extract: Parse SecurityHub event into normalized fields (ARN, region, finding ID, hash, etc.)
3. Hash: Generate SHA-256 hash of finding for dedup (stored in `Metadata.FindingHash`)
4. ListDetectors: Call `guardduty-list-detectors` Lambda to get detector ID for the region
5. GetFindings: Call `guardduty-get-findings` Lambda with detector ID + finding IDs
6. Store: Write metadata to DynamoDB; findings JSON to S3

**Key design**: Multi-region awareness—finding region is extracted from SecurityHub event and passed to both Lambda functions to scope AWS API calls correctly.

## File Structure

- `blackboxduty/template.yaml` – SAM resource definitions (DynamoDB table, S3 bucket, state machine, Lambda functions)
- `blackboxduty/statemachine/blackboxduty.asl.json` – State machine definition (uses variable substitution for ARNs)
- `blackboxduty/functions/guardduty-{get-findings,list-detectors}/` – Each function has `app.py` (handler) + `test_app.py` (pytest unit tests)
- `samconfig.toml` – Deployment config (cached parameters from `sam deploy --guided`)

## Adding a New Lambda Function

1. Create `blackboxduty/functions/<function-name>/` with `app.py` and `test_app.py`
2. Add `AWS::Serverless::Function` resource to `template.yaml` (set `CodeUri`, `Handler: app.lambda_handler`, `Runtime: python3.13`, `Policies`)
3. If the state machine needs to invoke it, add a Task step in `blackboxduty.asl.json` with `Resource` = `${NewFunctionArn}` and add `DefinitionSubstitutions` entry + `LambdaInvokePolicy` to the state machine resource

## Modifying the State Machine

- Edit `blackboxduty.asl.json` directly (JSON ASL syntax)
- All ARN references use `${TokenName}` placeholders; define them in `template.yaml` under `DefinitionSubstitutions`
- Validate syntax before deploy: SAM will error on invalid ASL
- State names are immutable for resumption; changing a state name breaks in-flight executions

## Testing Strategy

- Unit tests live adjacent to handlers (e.g., `functions/guardduty-get-findings/test_app.py`)
- Mock boto3 clients; don't call real AWS APIs in unit tests
- Each function's Lambda environment passes region via `FindingRegion` parameter
- Run tests: `cd blackboxduty/functions/<function-name> && python -m pytest test_app.py -v`

## Deployment Gotchas

- **First deploy**: `sam deploy --guided` prompts for table name, bucket name, region, profile. Answers cached in `samconfig.toml`
- **S3 bucket names must be globally unique** (AWS constraint); default name may fail if taken
- **DynamoDB billing**: On-demand mode (default). Check `template.yaml` if you need provisioned capacity
- **State machine timeout**: Default is 24 hours; increase `TimeoutSeconds` in state machine resource if needed

## Key Non-Obvious Details

- **Finding region extraction**: State machine extracts `FindingRegion` from SecurityHub event. Both Lambda functions receive this and scope their `boto3.client()` call to it. If a new function is added, it must also respect this region parameter
- **Variable substitution is SAM-time, not runtime**: The `${...}` tokens in `blackboxduty.asl.json` are replaced when `sam build` runs. You cannot use runtime Step Functions syntax like `$.` substitution for these placeholders
- **Datetime serialization**: GuardDuty API returns datetime objects; Lambda serializes them to ISO 8601 strings in the JSON response (see `serialize_datetime` in `guardduty-get-findings/app.py`)
- **Event filtering**: EventBridge filter only triggers on GuardDuty findings; non-GuardDuty SecurityHub events are silently ignored

## Recommended Tools

- **[AWS Serverless plugin](https://claude.com/plugins/aws-serverless)** — provides SAM/CloudFormation-aware context for Claude. Install it once from the link; it is enabled project-wide via `.claude/settings.json`.
- **[Code Review plugin](https://claude.com/plugins/code-review)** — use this to review all changes before opening a PR (see below). Install it once from the link; enabled project-wide via `.claude/settings.json`.
- **CloudWatch MCP Server** — configured in `.mcp.json` (project root); auto-starts when Claude Code loads this project. Requires a `blackboxduty` AWS profile. See `blackboxduty/README.md` for setup.
- **AWS Documentation MCP Server** — configured in `.mcp.json`; auto-starts alongside CloudWatch. No credentials required — fetches public AWS docs over HTTPS. Use this to look up current SAM resource schemas, Step Functions ASL intrinsic functions, and GuardDuty API reference inline.

## Local Development

No dedicated local execution framework beyond unit tests. To test the state machine end-to-end:
1. Deploy to dev environment (`sam deploy`)
2. Trigger via AWS Console or `aws stepfunctions start-execution`
3. Monitor execution in Step Functions console

## Before Opening a PR

**Always run a code review using the [Code Review plugin](https://claude.com/plugins/code-review) before merging.**

1. Ensure all changes are committed on your branch
2. Push the branch and create a PR: `gh pr create --title "..." --body "..."`
3. Run the code review skill: `/code-review:code-review`
4. Address any issues surfaced, then mark the PR ready for review: `gh pr ready <number>`

## Deployment Checklist

- [ ] Ran `sam build --use-container` (Docker running)
- [ ] Ran all unit tests: `python -m pytest blackboxduty/functions/*/test_app.py -v`
- [ ] Updated `template.yaml` if adding/modifying resources
- [ ] Updated `blackboxduty.asl.json` if adding/modifying state machine steps
- [ ] Code review completed via Code Review plugin
- [ ] Ran `sam deploy --guided` or `sam deploy` (uses `samconfig.toml`)
