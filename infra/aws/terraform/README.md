# VisorSense AWS Terraform foundation

This directory declares a low-cost proof-of-concept foundation:

- AWS IoT Core Thing and a restricted publish policy.
- An S3 bucket with public access blocked, SSE-S3 encryption, and configurable
  raw-data expiration.
- An AWS IoT rule that writes matching MQTT messages to S3.
- A CloudWatch log group with explicit retention.

It does **not** create device certificates or private keys. Provision a
certificate securely, attach it to the Thing and policy, and deliver the
private key to the ESP32 out of band. Never commit those artifacts.

## Validation without deployment

From this directory:

```text
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
```

`terraform init` may download the AWS provider but does not create AWS
resources. The configuration uses the AWS provider's data sources, so
`terraform validate` checks configuration structure only; it is not proof that
an account has permissions, quotas, or eligible pricing.

Do not run `terraform apply` or `terraform destroy` as part of CI.

## Future controlled deployment

1. Copy `terraform.tfvars.example` to a local, ignored `terraform.tfvars`.
2. Choose a globally unique bucket name and retention values.
3. Review the generated policy and expected costs.
4. Configure AWS credentials manually in the operator environment.
5. Run `terraform plan` manually and review it.
6. Apply only after the plan, region, account, retention and certificate
   procedure have been approved.
