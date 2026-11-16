locals {
  name_prefix     = "${var.project_name}-${var.environment}"
  bucket_name     = coalesce(var.telemetry_bucket_name, "${local.name_prefix}-${data.aws_caller_identity.current.account_id}")
  telemetry_topic = "${trim(var.telemetry_topic_prefix, "/")}/#"
}

data "aws_caller_identity" "current" {}

data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}
