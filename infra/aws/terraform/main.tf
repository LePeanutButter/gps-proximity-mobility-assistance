resource "aws_s3_bucket" "telemetry" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_public_access_block" "telemetry" {
  bucket = aws_s3_bucket.telemetry.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "telemetry" {
  bucket = aws_s3_bucket.telemetry.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "telemetry" {
  bucket = aws_s3_bucket.telemetry.id

  rule {
    id     = "expire-raw-telemetry"
    status = "Enabled"

    expiration {
      days = var.telemetry_retention_days
    }

    filter {}
  }
}

resource "aws_iot_thing" "device" {
  name = var.iot_thing_name
}

resource "aws_iot_policy" "device" {
  name = "${local.name_prefix}-device-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["iot:Connect"]
        Resource = "arn:aws:iot:${var.aws_region}:*:client/${var.iot_thing_name}"
      },
      {
        Effect   = "Allow"
        Action   = ["iot:Publish"]
        Resource = "arn:aws:iot:${var.aws_region}:*:topic/${trim(var.telemetry_topic_prefix, "/")}/*"
      },
    ]
  })
}

resource "aws_iam_role" "iot_rule" {
  name = "${local.name_prefix}-iot-rule"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "iot.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "iot_rule_s3" {
  name = "${local.name_prefix}-s3-write"
  role = aws_iam_role.iot_rule.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.telemetry.arn}/raw/*"
      }, {
      Effect = "Allow"
      Action = [
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]
      Resource = "${aws_cloudwatch_log_group.iot_rule.arn}:*"
    }]
  })
}

resource "aws_iot_topic_rule" "telemetry_to_s3" {
  name        = replace("${local.name_prefix}_telemetry_to_s3", "-", "_")
  enabled     = true
  sql         = "SELECT * FROM '${trim(var.telemetry_topic_prefix, "/")}/#'"
  sql_version = "2016-03-23"

  s3 {
    bucket_name = aws_s3_bucket.telemetry.bucket
    key         = "raw/${timestamp()}.json"
    role_arn    = aws_iam_role.iot_rule.arn
  }

  cloudwatch_logs {
    log_group_name = aws_cloudwatch_log_group.iot_rule.name
    role_arn       = aws_iam_role.iot_rule.arn
  }
}

resource "aws_cloudwatch_log_group" "iot_rule" {
  name              = "/aws/iot/${local.name_prefix}"
  retention_in_days = var.cloudwatch_log_retention_days
}
