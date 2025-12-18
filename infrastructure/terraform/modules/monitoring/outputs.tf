# Enhanced Monitoring Module Outputs for Financial Standards Compliance

# CloudWatch Log Groups
output "application_log_group_name" {
  description = "Name of the application log group"
  value       = aws_cloudwatch_log_group.application.name
}

output "application_log_group_arn" {
  description = "ARN of the application log group"
  value       = aws_cloudwatch_log_group.application.arn
}

output "database_log_group_name" {
  description = "Name of the database log group"
  value       = aws_cloudwatch_log_group.database.name
}

output "database_log_group_arn" {
  description = "ARN of the database log group"
  value       = aws_cloudwatch_log_group.database.arn
}

output "security_log_group_name" {
  description = "Name of the security log group"
  value       = aws_cloudwatch_log_group.security.name
}

output "security_log_group_arn" {
  description = "ARN of the security log group"
  value       = aws_cloudwatch_log_group.security.arn
}

output "audit_log_group_name" {
  description = "Name of the audit log group"
  value       = aws_cloudwatch_log_group.audit.name
}

output "audit_log_group_arn" {
  description = "ARN of the audit log group"
  value       = aws_cloudwatch_log_group.audit.arn
}

output "performance_log_group_name" {
  description = "Name of the performance log group"
  value       = aws_cloudwatch_log_group.performance.name
}

output "performance_log_group_arn" {
  description = "ARN of the performance log group"
  value       = aws_cloudwatch_log_group.performance.arn
}

# CloudWatch Dashboards
output "main_dashboard_url" {
  description = "URL of the main monitoring dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "security_dashboard_url" {
  description = "URL of the security monitoring dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.security.dashboard_name}"
}

output "main_dashboard_name" {
  description = "Name of the main monitoring dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "security_dashboard_name" {
  description = "Name of the security monitoring dashboard"
  value       = aws_cloudwatch_dashboard.security.dashboard_name
}

# CloudWatch Alarms
output "alarm_arns" {
  description = "ARNs of all CloudWatch alarms"
  value = {
    high_cpu             = aws_cloudwatch_metric_alarm.high_cpu.arn
    high_memory          = aws_cloudwatch_metric_alarm.high_memory.arn
    database_cpu         = aws_cloudwatch_metric_alarm.database_cpu.arn
    database_connections = aws_cloudwatch_metric_alarm.database_connections.arn
    application_errors   = aws_cloudwatch_metric_alarm.application_errors.arn
    response_time        = aws_cloudwatch_metric_alarm.response_time.arn
    failed_logins        = aws_cloudwatch_metric_alarm.failed_logins.arn
    suspicious_activity  = aws_cloudwatch_metric_alarm.suspicious_activity.arn
  }
}

output "alarm_names" {
  description = "Names of all CloudWatch alarms"
  value = {
    high_cpu             = aws_cloudwatch_metric_alarm.high_cpu.alarm_name
    high_memory          = aws_cloudwatch_metric_alarm.high_memory.alarm_name
    database_cpu         = aws_cloudwatch_metric_alarm.database_cpu.alarm_name
    database_connections = aws_cloudwatch_metric_alarm.database_connections.alarm_name
    application_errors   = aws_cloudwatch_metric_alarm.application_errors.alarm_name
    response_time        = aws_cloudwatch_metric_alarm.response_time.alarm_name
    failed_logins        = aws_cloudwatch_metric_alarm.failed_logins.alarm_name
    suspicious_activity  = aws_cloudwatch_metric_alarm.suspicious_activity.alarm_name
  }
}

# SNS Topics
output "alerts_topic_arn" {
  description = "ARN of the general alerts SNS topic"
  value       = aws_sns_topic.alerts.arn
}

output "critical_alerts_topic_arn" {
  description = "ARN of the critical alerts SNS topic"
  value       = aws_sns_topic.critical_alerts.arn
}

output "security_alerts_topic_arn" {
  description = "ARN of the security alerts SNS topic"
  value       = aws_sns_topic.security_alerts.arn
}

output "alerts_topic_name" {
  description = "Name of the general alerts SNS topic"
  value       = aws_sns_topic.alerts.name
}

output "critical_alerts_topic_name" {
  description = "Name of the critical alerts SNS topic"
  value       = aws_sns_topic.critical_alerts.name
}

output "security_alerts_topic_name" {
  description = "Name of the security alerts SNS topic"
  value       = aws_sns_topic.security_alerts.name
}

# CloudWatch Insights Queries
output "insights_query_ids" {
  description = "IDs of CloudWatch Insights queries"
  value = {
    transaction_audit    = aws_cloudwatch_query_definition.transaction_audit.query_definition_id
    security_events      = aws_cloudwatch_query_definition.security_events.query_definition_id
    performance_analysis = aws_cloudwatch_query_definition.performance_analysis.query_definition_id
    error_analysis       = aws_cloudwatch_query_definition.error_analysis.query_definition_id
  }
}

output "insights_query_names" {
  description = "Names of CloudWatch Insights queries"
  value = {
    transaction_audit    = aws_cloudwatch_query_definition.transaction_audit.name
    security_events      = aws_cloudwatch_query_definition.security_events.name
    performance_analysis = aws_cloudwatch_query_definition.performance_analysis.name
    error_analysis       = aws_cloudwatch_query_definition.error_analysis.name
  }
}

# Metric Filters
output "metric_filter_names" {
  description = "Names of CloudWatch log metric filters"
  value = {
    transaction_volume  = aws_cloudwatch_log_metric_filter.transaction_volume.name
    failed_transactions = aws_cloudwatch_log_metric_filter.failed_transactions.name
    user_registrations  = aws_cloudwatch_log_metric_filter.user_registrations.name
  }
}

# EventBridge Rules
output "event_rule_arns" {
  description = "ARNs of EventBridge rules"
  value = {
    security_incident = aws_cloudwatch_event_rule.security_incident.arn
  }
}

output "event_rule_names" {
  description = "Names of EventBridge rules"
  value = {
    security_incident = aws_cloudwatch_event_rule.security_incident.name
  }
}

# Synthetics
output "synthetics_canary_name" {
  description = "Name of the Synthetics canary"
  value       = var.enable_synthetics ? aws_synthetics_canary.api_health_check[0].name : null
}

output "synthetics_canary_arn" {
  description = "ARN of the Synthetics canary"
  value       = var.enable_synthetics ? aws_synthetics_canary.api_health_check[0].arn : null
}

output "synthetics_artifacts_bucket" {
  description = "Name of the Synthetics artifacts S3 bucket"
  value       = var.enable_synthetics ? aws_s3_bucket.synthetics_artifacts[0].bucket : null
}

# X-Ray
output "xray_sampling_rule_name" {
  description = "Name of the X-Ray sampling rule"
  value       = var.enable_xray_tracing ? aws_xray_sampling_rule.main[0].rule_name : null
}

output "xray_sampling_rule_arn" {
  description = "ARN of the X-Ray sampling rule"
  value       = var.enable_xray_tracing ? aws_xray_sampling_rule.main[0].arn : null
}

# Monitoring Configuration Summary
output "monitoring_configuration" {
  description = "Summary of monitoring configuration"
  value = {
    log_retention_days             = var.log_retention_days
    security_log_retention_days    = var.security_log_retention_days
    audit_log_retention_days       = var.audit_log_retention_days
    synthetics_enabled             = var.enable_synthetics
    xray_tracing_enabled           = var.enable_xray_tracing
    automated_response_enabled     = var.enable_automated_response
    business_metrics_enabled       = var.business_metrics_enabled
    compliance_monitoring_enabled  = var.compliance_monitoring_enabled
    performance_monitoring_enabled = var.performance_monitoring_enabled
    cost_monitoring_enabled        = var.cost_monitoring_enabled
    log_analysis_enabled           = var.log_analysis_enabled
  }
}

# Alert Configuration Summary
output "alert_configuration" {
  description = "Summary of alert configuration"
  value = {
    cpu_threshold                 = var.cpu_alarm_threshold
    memory_threshold              = var.memory_alarm_threshold
    db_cpu_threshold              = var.db_cpu_alarm_threshold
    db_connection_threshold       = var.db_connection_alarm_threshold
    error_rate_threshold          = var.error_rate_threshold
    response_time_threshold       = var.response_time_threshold
    failed_login_threshold        = var.failed_login_threshold
    suspicious_activity_threshold = var.suspicious_activity_threshold
    alert_email_count             = length(var.alert_email_addresses)
    critical_alert_email_count    = length(var.critical_alert_email_addresses)
    security_alert_email_count    = length(var.security_alert_email_addresses)
  }
}

# Compliance Reporting
output "compliance_monitoring_status" {
  description = "Status of compliance monitoring features"
  value = {
    audit_trail_enabled            = var.audit_trail_enabled
    data_retention_compliant       = var.log_retention_days >= 2555
    security_monitoring_enabled    = true
    transaction_monitoring_enabled = true
    access_logging_enabled         = true
    encryption_monitoring_enabled  = true
    incident_response_enabled      = var.enable_automated_response
    regulatory_requirements        = var.regulatory_requirements
  }
}

# Cost Monitoring
output "cost_monitoring_configuration" {
  description = "Cost monitoring configuration details"
  value = {
    enabled                    = var.cost_monitoring_enabled
    monthly_budget_limit       = var.monthly_budget_limit
    alert_threshold_percentage = var.cost_alert_threshold_percentage
  }
}

# Integration Points
output "integration_endpoints" {
  description = "Integration endpoints for external monitoring tools"
  value = {
    cloudwatch_logs_endpoint    = "https://logs.${data.aws_region.current.name}.amazonaws.com"
    cloudwatch_metrics_endpoint = "https://monitoring.${data.aws_region.current.name}.amazonaws.com"
    xray_endpoint               = var.enable_xray_tracing ? "https://xray.${data.aws_region.current.name}.amazonaws.com" : null
    synthetics_endpoint         = var.enable_synthetics ? "https://synthetics.${data.aws_region.current.name}.amazonaws.com" : null
  }
}

# Monitoring URLs for Quick Access
output "monitoring_urls" {
  description = "Quick access URLs for monitoring resources"
  value = {
    cloudwatch_console = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}"
    logs_console       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#logsV2:log-groups"
    alarms_console     = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#alarmsV2:"
    insights_console   = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#logsV2:logs-insights"
    xray_console       = var.enable_xray_tracing ? "https://console.aws.amazon.com/xray/home?region=${data.aws_region.current.name}" : null
    synthetics_console = var.enable_synthetics ? "https://console.aws.amazon.com/synthetics/home?region=${data.aws_region.current.name}" : null
  }
}

# Resource Counts for Inventory
output "resource_inventory" {
  description = "Inventory of monitoring resources created"
  value = {
    log_groups_count          = 5 # application, database, security, audit, performance
    dashboards_count          = 2 # main, security
    alarms_count              = 8 # all alarm types
    sns_topics_count          = 3 # alerts, critical, security
    metric_filters_count      = 3 # transaction volume, failed transactions, user registrations
    event_rules_count         = 1 # security incident
    insights_queries_count    = 4 # transaction audit, security events, performance, error analysis
    synthetics_canaries_count = var.enable_synthetics ? 1 : 0
    xray_sampling_rules_count = var.enable_xray_tracing ? 1 : 0
  }
}
