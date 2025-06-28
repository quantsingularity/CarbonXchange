# Enhanced Monitoring Module for Financial Standards Compliance
# This module implements comprehensive monitoring, logging, and alerting for CarbonXchange

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# CloudWatch Log Groups for centralized logging
resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/application/${var.app_name}/${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-app-logs"
    Type = "logging"
  })
}

resource "aws_cloudwatch_log_group" "database" {
  name              = "/aws/rds/${var.app_name}/${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-db-logs"
    Type = "logging"
  })
}

resource "aws_cloudwatch_log_group" "security" {
  name              = "/aws/security/${var.app_name}/${var.environment}"
  retention_in_days = var.security_log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-security-logs"
    Type = "security-logging"
  })
}

resource "aws_cloudwatch_log_group" "audit" {
  name              = "/aws/audit/${var.app_name}/${var.environment}"
  retention_in_days = var.audit_log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-audit-logs"
    Type = "audit-logging"
  })
}

resource "aws_cloudwatch_log_group" "performance" {
  name              = "/aws/performance/${var.app_name}/${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-performance-logs"
    Type = "performance-logging"
  })
}

# CloudWatch Dashboards
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.app_name}-${var.environment}-overview"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.load_balancer_arn_suffix],
            [".", "TargetResponseTime", ".", "."],
            [".", "HTTPCode_Target_2XX_Count", ".", "."],
            [".", "HTTPCode_Target_4XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Application Load Balancer Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.db_instance_identifier],
            [".", "DatabaseConnections", ".", "."],
            [".", "ReadLatency", ".", "."],
            [".", "WriteLatency", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Database Performance Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.security.name}' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 100"
          region  = data.aws_region.current.name
          title   = "Recent Security Errors"
          view    = "table"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_dashboard" "security" {
  dashboard_name = "${var.app_name}-${var.environment}-security"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/WAFV2", "AllowedRequests", "WebACL", var.waf_web_acl_name, "Rule", "ALL", "Region", data.aws_region.current.name],
            [".", "BlockedRequests", ".", ".", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "WAF Request Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.security.name}' | fields @timestamp, sourceIP, action | filter action = \"BLOCK\" | stats count() by sourceIP | sort count desc | limit 10"
          region  = data.aws_region.current.name
          title   = "Top Blocked IPs"
          view    = "table"
        }
      }
    ]
  })
}

# CloudWatch Alarms for Application Monitoring
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.app_name}-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = var.cpu_alarm_threshold
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = var.instance_id
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-high-cpu-alarm"
    Type = "monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${var.app_name}-${var.environment}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "CWAgent"
  period              = "300"
  statistic           = "Average"
  threshold           = var.memory_alarm_threshold
  alarm_description   = "This metric monitors memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = var.instance_id
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-high-memory-alarm"
    Type = "monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.app_name}-${var.environment}-db-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.db_cpu_alarm_threshold
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.db_instance_identifier
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-db-high-cpu-alarm"
    Type = "monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "${var.app_name}-${var.environment}-db-high-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.db_connection_alarm_threshold
  alarm_description   = "This metric monitors RDS connection count"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.db_instance_identifier
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-db-high-connections-alarm"
    Type = "monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "application_errors" {
  alarm_name          = "${var.app_name}-${var.environment}-app-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.error_rate_threshold
  alarm_description   = "This metric monitors application 5XX errors"
  alarm_actions       = [aws_sns_topic.critical_alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = var.load_balancer_arn_suffix
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-app-errors-alarm"
    Type = "monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "response_time" {
  alarm_name          = "${var.app_name}-${var.environment}-high-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = var.response_time_threshold
  alarm_description   = "This metric monitors application response time"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = var.load_balancer_arn_suffix
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-high-response-time-alarm"
    Type = "monitoring"
  })
}

# Security-specific alarms
resource "aws_cloudwatch_metric_alarm" "failed_logins" {
  alarm_name          = "${var.app_name}-${var.environment}-failed-logins"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FailedLoginAttempts"
  namespace           = "CarbonXchange/Security"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.failed_login_threshold
  alarm_description   = "This metric monitors failed login attempts"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-failed-logins-alarm"
    Type = "security-monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "suspicious_activity" {
  alarm_name          = "${var.app_name}-${var.environment}-suspicious-activity"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "SuspiciousActivity"
  namespace           = "CarbonXchange/Security"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.suspicious_activity_threshold
  alarm_description   = "This metric monitors suspicious activity patterns"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-suspicious-activity-alarm"
    Type = "security-monitoring"
  })
}

# SNS Topics for Alerting
resource "aws_sns_topic" "alerts" {
  name              = "${var.app_name}-${var.environment}-alerts"
  kms_master_key_id = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-alerts"
    Type = "alerting"
  })
}

resource "aws_sns_topic" "critical_alerts" {
  name              = "${var.app_name}-${var.environment}-critical-alerts"
  kms_master_key_id = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-critical-alerts"
    Type = "alerting"
  })
}

resource "aws_sns_topic" "security_alerts" {
  name              = "${var.app_name}-${var.environment}-security-alerts"
  kms_master_key_id = var.kms_key_arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-security-alerts"
    Type = "security-alerting"
  })
}

# SNS Topic Subscriptions
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = length(var.alert_email_addresses)
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_addresses[count.index]
}

resource "aws_sns_topic_subscription" "email_critical_alerts" {
  count     = length(var.critical_alert_email_addresses)
  topic_arn = aws_sns_topic.critical_alerts.arn
  protocol  = "email"
  endpoint  = var.critical_alert_email_addresses[count.index]
}

resource "aws_sns_topic_subscription" "email_security_alerts" {
  count     = length(var.security_alert_email_addresses)
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email_addresses[count.index]
}

# CloudWatch Insights Queries for Financial Compliance
resource "aws_cloudwatch_query_definition" "transaction_audit" {
  name = "${var.app_name}-${var.environment}-transaction-audit"

  log_group_names = [
    aws_cloudwatch_log_group.application.name,
    aws_cloudwatch_log_group.audit.name
  ]

  query_string = <<EOF
fields @timestamp, user_id, transaction_id, amount, transaction_type, status
| filter transaction_type like /TRADE|TRANSFER|PAYMENT/
| sort @timestamp desc
| limit 1000
EOF
}

resource "aws_cloudwatch_query_definition" "security_events" {
  name = "${var.app_name}-${var.environment}-security-events"

  log_group_names = [
    aws_cloudwatch_log_group.security.name,
    aws_cloudwatch_log_group.audit.name
  ]

  query_string = <<EOF
fields @timestamp, event_type, source_ip, user_id, action, result
| filter event_type like /LOGIN|LOGOUT|ACCESS_DENIED|PRIVILEGE_ESCALATION/
| sort @timestamp desc
| limit 1000
EOF
}

resource "aws_cloudwatch_query_definition" "performance_analysis" {
  name = "${var.app_name}-${var.environment}-performance-analysis"

  log_group_names = [
    aws_cloudwatch_log_group.application.name,
    aws_cloudwatch_log_group.performance.name
  ]

  query_string = <<EOF
fields @timestamp, request_id, endpoint, response_time, status_code
| filter response_time > 1000
| stats avg(response_time), max(response_time), count() by endpoint
| sort avg desc
EOF
}

resource "aws_cloudwatch_query_definition" "error_analysis" {
  name = "${var.app_name}-${var.environment}-error-analysis"

  log_group_names = [
    aws_cloudwatch_log_group.application.name
  ]

  query_string = <<EOF
fields @timestamp, @message, error_code, stack_trace
| filter @message like /ERROR|EXCEPTION|FATAL/
| stats count() by error_code
| sort count desc
EOF
}

# Custom Metrics for Business KPIs
resource "aws_cloudwatch_log_metric_filter" "transaction_volume" {
  name           = "${var.app_name}-${var.environment}-transaction-volume"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "[timestamp, request_id, transaction_type=\"TRADE\", ...]"

  metric_transformation {
    name      = "TransactionVolume"
    namespace = "CarbonXchange/Business"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "failed_transactions" {
  name           = "${var.app_name}-${var.environment}-failed-transactions"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "[timestamp, request_id, transaction_type, status=\"FAILED\", ...]"

  metric_transformation {
    name      = "FailedTransactions"
    namespace = "CarbonXchange/Business"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "user_registrations" {
  name           = "${var.app_name}-${var.environment}-user-registrations"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "[timestamp, request_id, event_type=\"USER_REGISTRATION\", ...]"

  metric_transformation {
    name      = "UserRegistrations"
    namespace = "CarbonXchange/Business"
    value     = "1"
  }
}

# EventBridge Rules for Automated Response
resource "aws_cloudwatch_event_rule" "security_incident" {
  name        = "${var.app_name}-${var.environment}-security-incident"
  description = "Capture security incidents for automated response"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [7.0, 8.0, 8.5, 9.0]
    }
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-security-incident-rule"
    Type = "security-automation"
  })
}

resource "aws_cloudwatch_event_target" "security_incident_lambda" {
  count     = var.enable_automated_response ? 1 : 0
  rule      = aws_cloudwatch_event_rule.security_incident.name
  target_id = "SecurityIncidentLambdaTarget"
  arn       = var.security_response_lambda_arn
}

# CloudWatch Synthetics for Application Monitoring
resource "aws_synthetics_canary" "api_health_check" {
  count                = var.enable_synthetics ? 1 : 0
  name                 = "${var.app_name}-${var.environment}-api-health"
  artifact_s3_location = "s3://${aws_s3_bucket.synthetics_artifacts[0].bucket}/canary-artifacts/"
  execution_role_arn   = aws_iam_role.synthetics[0].arn
  handler              = "apiCanaryBlueprint.handler"
  zip_file             = "synthetics-api-canary.zip"
  runtime_version      = "syn-nodejs-puppeteer-6.2"

  schedule {
    expression = var.synthetics_schedule
  }

  run_config {
    timeout_in_seconds    = 60
    memory_in_mb         = 960
    active_tracing       = true
    environment_variables = {
      API_ENDPOINT = var.api_endpoint_url
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-api-health-canary"
    Type = "monitoring"
  })
}

resource "aws_s3_bucket" "synthetics_artifacts" {
  count  = var.enable_synthetics ? 1 : 0
  bucket = "${var.app_name}-${var.environment}-synthetics-artifacts-${random_id.synthetics_bucket_suffix[0].hex}"

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-synthetics-artifacts"
    Type = "monitoring"
  })
}

resource "random_id" "synthetics_bucket_suffix" {
  count       = var.enable_synthetics ? 1 : 0
  byte_length = 4
}

resource "aws_iam_role" "synthetics" {
  count = var.enable_synthetics ? 1 : 0
  name  = "${var.app_name}-${var.environment}-synthetics-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-synthetics-role"
    Type = "monitoring"
  })
}

resource "aws_iam_role_policy_attachment" "synthetics" {
  count      = var.enable_synthetics ? 1 : 0
  role       = aws_iam_role.synthetics[0].name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchSyntheticsExecutionRolePolicy"
}

# X-Ray Tracing for Distributed Tracing
resource "aws_xray_sampling_rule" "main" {
  count           = var.enable_xray_tracing ? 1 : 0
  rule_name       = "${var.app_name}-${var.environment}-sampling-rule"
  priority        = 9000
  version         = 1
  reservoir_size  = 1
  fixed_rate      = 0.1
  url_path        = "*"
  host            = "*"
  http_method     = "*"
  service_type    = "*"
  service_name    = "*"
  resource_arn    = "*"

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-xray-sampling-rule"
    Type = "monitoring"
  })
}

