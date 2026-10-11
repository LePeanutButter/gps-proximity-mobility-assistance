variable "aws_region" {
  description = "AWS region for the proof of concept."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short project identifier used in resource names."
  type        = string
  default     = "visorsense"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,24}$", var.project_name))
    error_message = "project_name must contain 3-24 lowercase letters, numbers, or hyphens."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "poc"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,12}$", var.environment))
    error_message = "environment must contain 2-12 lowercase letters, numbers, or hyphens."
  }
}

variable "telemetry_bucket_name" {
  description = "Globally unique S3 bucket name. Leave null to derive a name."
  type        = string
  default     = null
  nullable    = true
}

variable "telemetry_topic_prefix" {
  description = "MQTT topic prefix accepted by the IoT policy and rule."
  type        = string
  default     = "visorsense/telemetry"
}

variable "telemetry_retention_days" {
  description = "S3 expiration for raw telemetry objects."
  type        = number
  default     = 30

  validation {
    condition     = var.telemetry_retention_days >= 1 && var.telemetry_retention_days <= 365
    error_message = "telemetry_retention_days must be between 1 and 365."
  }
}

variable "cloudwatch_log_retention_days" {
  description = "Retention for the IoT rule CloudWatch log group."
  type        = number
  default     = 14

  validation {
    condition     = var.cloudwatch_log_retention_days >= 1 && var.cloudwatch_log_retention_days <= 90
    error_message = "cloudwatch_log_retention_days must be between 1 and 90."
  }
}

variable "iot_thing_name" {
  description = "Thing name associated with the physical device."
  type        = string
  default     = "visor-esp32-001"
}
