<div align="center">

# AWS QR Code Python Application Infra Pipeline
Infrastructure-as-code repository for the **QR Code Generator** project. Contains the bootstrap CloudFormation template, all infrastructure stacks, and the teardown script.

<img width="1280" height="720" alt="AWS_CICD_Series (9)" src="https://github.com/user-attachments/assets/21e58cdf-56bd-4175-9de6-5d6fcea3f446" />


![Infra Pipeline](https://img.shields.io/badge/pipeline-infra-blue?style=flat-square&logo=amazonaws)
![IaC](https://img.shields.io/badge/IaC-CloudFormation-orange?style=flat-square&logo=amazonaws)
![Lint](https://img.shields.io/badge/lint-cfn--lint-green?style=flat-square)
![Deploy Target](https://img.shields.io/badge/deploy-EC2-yellow?style=flat-square&logo=amazonaws)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)


<a href="https://www.buymeacoffee.com/Dheeraj3" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" height="50">
</a>

## [Subscribe](https://www.youtube.com/@dheeraj-choudhary?sub_confirmation=1) to learn more About Artificial-Intellegence, Machine-Learning, Cloud & DevOps.

<p align="center">
<a href="https://www.linkedin.com/in/dheeraj-choudhary/" target="_blank">
  <img height="100" alt="Dheeraj Choudhary | LinkedIN"  src="https://user-images.githubusercontent.com/60597290/152035581-a7c6c0c3-65c3-4160-89c0-e90ddc1e8d4e.png"/>
</a> 

<a href="https://www.youtube.com/@dheeraj-choudhary?sub_confirmation=1">
    <img height="100" src="https://user-images.githubusercontent.com/60597290/152035929-b7f75d38-e1c2-4325-a97e-7b934b8534e2.png" />
</a>    
</p>

</div>

---

## Repository Structure

```
aws-cicd-qrcode-python-infra/
├── bootstrap/
│   └── pipeline.yml          # Deploy once from console — creates both repos + both pipelines
├── infra/
│   ├── buildspec-validate.yml # CodeBuild: cfn-lint + cloudformation validate-template
│   └── cfn/
│       ├── 01-iam.yml         # EC2 instance role, instance profile, CodeDeploy service role
│       ├── 02-networking.yml  # VPC, public subnet, IGW, route table, security group
│       ├── 03-compute.yml     # EC2 instance, Elastic IP, CodeDeploy app + deployment group
│       ├── 04-ecr-s3.yml      # ECR repo, deployment S3 bucket, SSM parameters
│       └── 05-monitoring.yml  # CloudWatch log groups, alarms, dashboard
├── teardown.sh                # Full environment teardown in reverse order
├── .gitignore
└── README.md
```

---

## Stacks

| Order | Stack Name | Template | Description |
|-------|------------|----------|-------------|
| 1 | `qrcode-iam` | `01-iam.yml` | EC2 instance role, instance profile, CodeDeploy service role |
| 2 | `qrcode-networking` | `02-networking.yml` | VPC `10.0.0.0/16`, public subnet, IGW, SG (ports 80 + 5000) |
| 3 | `qrcode-ecr-s3` | `04-ecr-s3.yml` | ECR repo, deployment S3 bucket, 5 SSM parameters |
| 4 | `qrcode-compute` | `03-compute.yml` | EC2 (AL2023, t3.micro), EIP, CodeDeploy app + deployment group |
| 5 | `qrcode-monitoring` | `05-monitoring.yml` | CW log groups, CPU + status check alarms, dashboard |

> `03-compute` deploys after `04-ecr-s3` because EC2 user data reads the ECR repo URI from the SSM parameter written by stack 04.

---

## Prerequisites

- AWS CLI v2 configured with sufficient permissions
- Git with AWS CodeCommit HTTPS credentials configured
- `jq` installed (required by `teardown.sh`)

---

## First-Time Setup

### 1. Deploy the Bootstrap Stack

Go to **AWS Console → CloudFormation → Create Stack** and upload `bootstrap/pipeline.yml`.

Use the following stack name:

```
qrcode-bootstrap
```

Accept all default parameter values or override as needed:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `AwsRegion` | `us-east-1` | AWS region for all resources |
| `InfraRepoBranch` | `main` | Branch that triggers the infra pipeline |
| `AppRepoBranch` | `main` | Branch that triggers the app pipeline |
| `CodeBuildComputeType` | `BUILD_GENERAL1_SMALL` | CodeBuild instance size |

### 2. Clone Both Repositories

After the bootstrap stack is created, get the clone URLs from the stack Outputs tab and clone:

```bash
git clone https://git-codecommit.<region>.amazonaws.com/v1/repos/aws-cicd-qrcode-python-infra
git clone https://git-codecommit.<region>.amazonaws.com/v1/repos/aws-cicd-qrcode-python-app
```

### 3. Push Infra Repo

```bash
cd aws-cicd-qrcode-python-infra
git add .
git commit -m "feat: initial infra"
git push origin main
```

This push triggers the infra pipeline automatically via EventBridge. The pipeline will validate all CFN templates then deploy all 5 stacks in order.

### 4. Push App Repo

Once the infra pipeline completes successfully (EC2 + CodeDeploy are provisioned), push the app repo to trigger the app pipeline:

```bash
cd aws-cicd-qrcode-python-app
git add .
git commit -m "feat: initial app"
git push origin main
```

---

## SSM Parameters Written by Stack 04

| Parameter | Value |
|-----------|-------|
| `/qrcode/ecr/repo-uri` | `<account>.dkr.ecr.<region>.amazonaws.com/qrcode-app` |
| `/qrcode/ecr/repo-name` | `qrcode-app` |
| `/qrcode/s3/deployment-bucket` | `qrcode-deployments-<account>-<region>` |
| `/qrcode/aws/region` | `<region>` |
| `/qrcode/aws/account-id` | `<account>` |

---

## Stack Exports

Key values exported by stacks for cross-stack reference:

| Export Name | Source Stack | Description |
|-------------|-------------|-------------|
| `qrcode-ec2-instance-profile-name` | `qrcode-iam` | Used by `03-compute` |
| `qrcode-codedeploy-service-role-arn` | `qrcode-iam` | Used by `03-compute` |
| `qrcode-public-subnet-id` | `qrcode-networking` | Used by `03-compute` |
| `qrcode-app-sg-id` | `qrcode-networking` | Used by `03-compute` |
| `qrcode-ec2-instance-id` | `qrcode-compute` | Used by `05-monitoring` |
| `qrcode-app-url` | `qrcode-compute` | Public URL of the app |

---

## Teardown

To destroy the entire environment:

```bash
chmod +x teardown.sh
./teardown.sh --region us-east-1 --profile default
```

The script will:
1. Empty all S3 buckets (versioned objects + delete markers)
2. Delete all ECR images from `qrcode-app`
3. Delete CFN stacks in reverse order: monitoring → compute → ecr-s3 → networking → iam
4. Delete the bootstrap stack
5. Delete the now-empty S3 buckets

> All actions are logged to `teardown.log`.

---

## Making Infrastructure Changes

Any push to `main` triggers the infra pipeline. The pipeline re-validates and re-deploys all stacks using `CREATE_UPDATE` — existing resources are updated in place where possible.

```bash
# Edit a template, then:
git add infra/cfn/
git commit -m "fix: update security group rules"
git push origin main
```

---

## Related Repository

| Repo | Description |
|------|-------------|
| [`aws-cicd-qrcode-python-app`](https://github.com/dheeraj3choudhary/aws-cicd-qrcode-python-app) | Python QR Code app, Docker, CodeDeploy scripts, app pipeline |
