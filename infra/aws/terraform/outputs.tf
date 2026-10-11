output "aws_iot_endpoint" {
  description = "Data-plane endpoint for MQTT/TLS clients."
  value       = data.aws_iot_endpoint.current.endpoint_address
}

output "telemetry_bucket_name" {
  description = "S3 bucket receiving raw telemetry through the IoT rule."
  value       = aws_s3_bucket.telemetry.bucket
}

output "iot_thing_name" {
  description = "Thing name to associate with a certificate securely."
  value       = aws_iot_thing.device.name
}

output "iot_policy_name" {
  description = "Restricted device policy name."
  value       = aws_iot_policy.device.name
}
