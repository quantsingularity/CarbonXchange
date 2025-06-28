# Enhanced Monitoring Module Variables for Financial Standards Compliance

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# KMS Configuration
variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}

# Log Retention Configuration
variable "log_retention_days" {
  description = "Number of days to retain application logs"
  type        = number
  default     = 2555  # 7 years for financial compliance
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 2555, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch Logs retention period."
  }
}

variable "security_log_retention_days" {
  description = "Number of days to retain security logs"
  type        = number
  default     = 2555  # 7 years for financial compliance
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 2555, 3653], var.security_log_retention_days)
    error_message = "Security log retention days must be a valid CloudWatch Logs retention period."
  }
}

variable "audit_log_retention_days" {
  description = "Number of days to retain audit logs"
  type        = number
  default     = 2555  # 7 years for financial compliance
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 2555, 3653], var.audit_log_retention_days)
    error_message = "Audit log retention days must be a valid CloudWatch Logs retention period."
  }
}

# Infrastructure Resource Identifiers
variable "instance_id" {
  description = "EC2 instance ID for monitoring"
  type        = string
  default     = ""
}

variable "db_instance_identifier" {
  description = "RDS instance identifier for monitoring"
  type        = string
  default     = ""
}

variable "load_balancer_arn_suffix" {
  description = "ALB ARN suffix for monitoring"
  type        = string
  default     = ""
}

variable "waf_web_acl_name" {
  description = "WAF Web ACL name for monitoring"
  type        = string
  default     = ""
}

# Alarm Thresholds
variable "cpu_alarm_threshold" {
  description = "CPU utilization threshold for alarms (percentage)"
  type        = number
  default     = 80
  validation {
    condition     = var.cpu_alarm_threshold > 0 && var.cpu_alarm_threshold <= 100
    error_message = "CPU alarm threshold must be between 1 and 100."
  }
}

variable "memory_alarm_threshold" {
  description = "Memory utilization threshold for alarms (percentage)"
  type        = number
  default     = 85
  validation {
    condition     = var.memory_alarm_threshold > 0 && var.memory_alarm_threshold <= 100
    error_message = "Memory alarm threshold must be between 1 and 100."
  }
}

variable "db_cpu_alarm_threshold" {
  description = "Database CPU utilization threshold for alarms (percentage)"
  type        = number
  default     = 75
  validation {
    condition     = var.db_cpu_alarm_threshold > 0 && var.db_cpu_alarm_threshold <= 100
    error_message = "Database CPU alarm threshold must be between 1 and 100."
  }
}

variable "db_connection_alarm_threshold" {
  description = "Database connection count threshold for alarms"
  type        = number
  default     = 80
}

variable "error_rate_threshold" {
  description = "Error rate threshold for alarms (count per period)"
  type        = number
  default     = 10
}

variable "response_time_threshold" {
  description = "Response time threshold for alarms (seconds)"
  type        = number
  default     = 2.0
}

variable "failed_login_threshold" {
  description = "Failed login attempts threshold for security alarms"
  type        = number
  default     = 5
}

variable "suspicious_activity_threshold" {
  description = "Suspicious activity threshold for security alarms"
  type        = number
  default     = 3
}

# Alert Configuration
variable "alert_email_addresses" {
  description = "List of email addresses for general alerts"
  type        = list(string)
  default     = []
}

variable "critical_alert_email_addresses" {
  description = "List of email addresses for critical alerts"
  type        = list(string)
  default     = []
}

variable "security_alert_email_addresses" {
  description = "List of email addresses for security alerts"
  type        = list(string)
  default     = []
}

# Automated Response Configuration
variable "enable_automated_response" {
  description = "Enable automated incident response"
  type        = bool
  default     = false
}

variable "security_response_lambda_arn" {
  description = "ARN of Lambda function for automated security response"
  type        = string
  default     = ""
}

# Synthetics Configuration
variable "enable_synthetics" {
  description = "Enable CloudWatch Synthetics for application monitoring"
  type        = bool
  default     = true
}

variable "synthetics_schedule" {
  description = "Schedule expression for Synthetics canary (rate or cron)"
  type        = string
  default     = "rate(5 minutes)"
}

variable "api_endpoint_url" {
  description = "API endpoint URL for Synthetics monitoring"
  type        = string
  default     = ""
}

# X-Ray Tracing Configuration
variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray distributed tracing"
  type        = bool
  default     = true
}

# Business Metrics Configuration
variable "business_metrics_enabled" {
  description = "Enable business-specific metrics collection"
  type        = bool
  default     = true
}

variable "transaction_volume_threshold" {
  description = "Transaction volume threshold for business alerts"
  type        = number
  default     = 1000
}

variable "revenue_threshold" {
  description = "Revenue threshold for business alerts"
  type        = number
  default     = 10000
}

# Compliance and Audit Configuration
variable "compliance_monitoring_enabled" {
  description = "Enable compliance-specific monitoring"
  type        = bool
  default     = true
}

variable "audit_trail_enabled" {
  description = "Enable comprehensive audit trail logging"
  type        = bool
  default     = true
}

variable "data_retention_policy" {
  description = "Data retention policy configuration"
  type = object({
    application_logs = number
    security_logs   = number
    audit_logs      = number
    metrics_data    = number
  })
  default = {
    application_logs = 2555  # 7 years
    security_logs   = 2555  # 7 years
    audit_logs      = 2555  # 7 years
    metrics_data    = 2555  # 7 years
  }
}

# Performance Monitoring Configuration
variable "performance_monitoring_enabled" {
  description = "Enable detailed performance monitoring"
  type        = bool
  default     = true
}

variable "apm_tool" {
  description = "Application Performance Monitoring tool (datadog, newrelic, dynatrace, none)"
  type        = string
  default     = "none"
  validation {
    condition     = contains(["datadog", "newrelic", "dynatrace", "none"], var.apm_tool)
    error_message = "APM tool must be one of: datadog, newrelic, dynatrace, none."
  }
}

# Cost Monitoring Configuration
variable "cost_monitoring_enabled" {
  description = "Enable cost monitoring and alerting"
  type        = bool
  default     = true
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit for cost alerts (USD)"
  type        = number
  default     = 1000
}

variable "cost_alert_threshold_percentage" {
  description = "Cost alert threshold as percentage of budget"
  type        = number
  default     = 80
  validation {
    condition     = var.cost_alert_threshold_percentage > 0 && var.cost_alert_threshold_percentage <= 100
    error_message = "Cost alert threshold must be between 1 and 100."
  }
}

# Log Analysis Configuration
variable "log_analysis_enabled" {
  description = "Enable advanced log analysis and insights"
  type        = bool
  default     = true
}

variable "log_analysis_queries" {
  description = "Custom log analysis queries for business insights"
  type = map(object({
    description = string
    query       = string
    schedule    = string
  }))
  default = {}
}

# Notification Configuration
variable "notification_channels" {
  description = "Notification channels configuration"
  type = object({
    email_enabled    = bool
    sms_enabled     = bool
    slack_enabled   = bool
    teams_enabled   = bool
    pagerduty_enabled = bool
  })
  default = {
    email_enabled    = true
    sms_enabled     = false
    slack_enabled   = false
    teams_enabled   = false
    pagerduty_enabled = false
  }
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "teams_webhook_url" {
  description = "Microsoft Teams webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "pagerduty_integration_key" {
  description = "PagerDuty integration key for critical alerts"
  type        = string
  default     = ""
  sensitive   = true
}

# Dashboard Configuration
variable "dashboard_configuration" {
  description = "Dashboard configuration settings"
  type = object({
    auto_refresh_interval = number
    time_range_hours     = number
    include_cost_metrics = bool
    include_security_metrics = bool
    include_business_metrics = bool
  })
  default = {
    auto_refresh_interval = 300  # 5 minutes
    time_range_hours     = 24   # 24 hours
    include_cost_metrics = true
    include_security_metrics = true
    include_business_metrics = true
  }
}

# Environment-specific Configuration
variable "environment_config" {
  description = "Environment-specific monitoring configuration"
  type = map(object({
    detailed_monitoring = bool
    enhanced_logging   = bool
    real_time_alerts   = bool
    cost_optimization  = bool
  }))
  default = {
    dev = {
      detailed_monitoring = false
      enhanced_logging   = false
      real_time_alerts   = false
      cost_optimization  = true
    }
    staging = {
      detailed_monitoring = true
      enhanced_logging   = true
      real_time_alerts   = true
      cost_optimization  = true
    }
    prod = {
      detailed_monitoring = true
      enhanced_logging   = true
      real_time_alerts   = true
      cost_optimization  = false
    }
  }
}

# Regulatory Compliance Configuration
variable "regulatory_requirements" {
  description = "Regulatory compliance requirements"
  type = object({
    sox_compliance     = bool
    pci_dss_compliance = bool
    gdpr_compliance    = bool
    hipaa_compliance   = bool
    iso27001_compliance = bool
  })
  default = {
    sox_compliance     = true
    pci_dss_compliance = true
    gdpr_compliance    = true
    hipaa_compliance   = false
    iso27001_compliance = true
  }
}

# Monitoring Integration Configuration
variable "monitoring_integrations" {
  description = "Third-party monitoring tool integrations"
  type = object({
    prometheus_enabled = bool
    grafana_enabled   = bool
    elk_stack_enabled = bool
    splunk_enabled    = bool
  })
  default = {
    prometheus_enabled = true
    grafana_enabled   = true
    elk_stack_enabled = false
    splunk_enabled    = false
  }
}

