# Enhanced Security Module Variables for Financial Standards Compliance

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for network ACLs"
  type        = list(string)
  default     = []
}

variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = []
}

variable "monitoring_access_cidrs" {
  description = "List of CIDR blocks allowed for monitoring access"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "app_port" {
  description = "Port on which the application runs"
  type        = number
  default     = 8000
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# KMS Configuration
variable "kms_deletion_window" {
  description = "Number of days before KMS key deletion"
  type        = number
  default     = 30
  validation {
    condition     = var.kms_deletion_window >= 7 && var.kms_deletion_window <= 30
    error_message = "KMS deletion window must be between 7 and 30 days."
  }
}

# WAF Configuration
variable "rate_limit_per_5min" {
  description = "Rate limit per 5 minutes for WAF"
  type        = number
  default     = 2000
}

variable "enable_geo_blocking" {
  description = "Enable geographic blocking in WAF"
  type        = bool
  default     = false
}

variable "blocked_countries" {
  description = "List of country codes to block (ISO 3166-1 alpha-2)"
  type        = list(string)
  default     = []
}

# CloudTrail Configuration
variable "enable_cloudtrail" {
  description = "Enable CloudTrail for audit logging"
  type        = bool
  default     = true
}

# GuardDuty Configuration
variable "enable_guardduty" {
  description = "Enable GuardDuty for threat detection"
  type        = bool
  default     = true
}

# Config Configuration
variable "enable_config" {
  description = "Enable AWS Config for compliance monitoring"
  type        = bool
  default     = true
}

# Security Hub Configuration
variable "enable_security_hub" {
  description = "Enable Security Hub for centralized security findings"
  type        = bool
  default     = true
}

# VPC Flow Logs Configuration
variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 2555  # 7 years for financial compliance
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 2555, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch Logs retention period."
  }
}

# Database Credentials
variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Secrets Manager Configuration
variable "secret_recovery_window" {
  description = "Number of days for secret recovery window"
  type        = number
  default     = 30
  validation {
    condition     = var.secret_recovery_window >= 7 && var.secret_recovery_window <= 30
    error_message = "Secret recovery window must be between 7 and 30 days."
  }
}

# Application Parameters for SSM Parameter Store
variable "app_parameters" {
  description = "Application parameters to store in SSM Parameter Store"
  type = map(object({
    type  = string
    value = string
  }))
  default = {}
  validation {
    condition = alltrue([
      for param in values(var.app_parameters) : contains(["String", "StringList", "SecureString"], param.type)
    ])
    error_message = "Parameter type must be one of: String, StringList, SecureString."
  }
}

# Compliance and Security Standards
variable "compliance_standards" {
  description = "List of compliance standards to enforce"
  type        = list(string)
  default     = ["PCI-DSS", "SOX", "GDPR", "ISO-27001"]
}

variable "security_contact_email" {
  description = "Email address for security notifications"
  type        = string
  default     = ""
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 2555  # 7 years for financial compliance
}

# Network Security
variable "enable_ddos_protection" {
  description = "Enable DDoS protection"
  type        = bool
  default     = true
}

variable "enable_network_firewall" {
  description = "Enable AWS Network Firewall"
  type        = bool
  default     = false
}

# Data Classification
variable "data_classification" {
  description = "Data classification level (public, internal, confidential, restricted)"
  type        = string
  default     = "confidential"
  validation {
    condition     = contains(["public", "internal", "confidential", "restricted"], var.data_classification)
    error_message = "Data classification must be one of: public, internal, confidential, restricted."
  }
}

# Encryption Configuration
variable "encryption_at_rest_required" {
  description = "Require encryption at rest for all data stores"
  type        = bool
  default     = true
}

variable "encryption_in_transit_required" {
  description = "Require encryption in transit for all communications"
  type        = bool
  default     = true
}

variable "minimum_tls_version" {
  description = "Minimum TLS version required"
  type        = string
  default     = "1.2"
  validation {
    condition     = contains(["1.2", "1.3"], var.minimum_tls_version)
    error_message = "Minimum TLS version must be 1.2 or 1.3."
  }
}

# Access Control
variable "require_mfa" {
  description = "Require multi-factor authentication"
  type        = bool
  default     = true
}

variable "password_policy" {
  description = "Password policy configuration"
  type = object({
    minimum_length         = number
    require_uppercase      = bool
    require_lowercase      = bool
    require_numbers        = bool
    require_symbols        = bool
    max_password_age_days  = number
    password_reuse_prevention = number
  })
  default = {
    minimum_length         = 14
    require_uppercase      = true
    require_lowercase      = true
    require_numbers        = true
    require_symbols        = true
    max_password_age_days  = 90
    password_reuse_prevention = 24
  }
}

# Incident Response
variable "incident_response_email" {
  description = "Email address for incident response notifications"
  type        = string
  default     = ""
}

variable "security_incident_sns_topic" {
  description = "SNS topic ARN for security incident notifications"
  type        = string
  default     = ""
}

# Vulnerability Management
variable "vulnerability_scan_schedule" {
  description = "Cron expression for vulnerability scanning schedule"
  type        = string
  default     = "cron(0 2 * * ? *)"  # Daily at 2 AM
}

variable "patch_maintenance_window" {
  description = "Maintenance window for patching (cron expression)"
  type        = string
  default     = "cron(0 3 ? * SUN *)"  # Sundays at 3 AM
}

# Business Continuity
variable "rto_minutes" {
  description = "Recovery Time Objective in minutes"
  type        = number
  default     = 240  # 4 hours
}

variable "rpo_minutes" {
  description = "Recovery Point Objective in minutes"
  type        = number
  default     = 60   # 1 hour
}

# Cost Management
variable "cost_center" {
  description = "Cost center for billing allocation"
  type        = string
  default     = ""
}

variable "budget_alert_threshold" {
  description = "Budget alert threshold percentage"
  type        = number
  default     = 80
}

# Environment-specific overrides
variable "environment_config" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    enable_detailed_monitoring = bool
    backup_frequency          = string
    log_level                = string
    performance_insights     = bool
  }))
  default = {
    dev = {
      enable_detailed_monitoring = false
      backup_frequency          = "daily"
      log_level                = "DEBUG"
      performance_insights     = false
    }
    staging = {
      enable_detailed_monitoring = true
      backup_frequency          = "daily"
      log_level                = "INFO"
      performance_insights     = true
    }
    prod = {
      enable_detailed_monitoring = true
      backup_frequency          = "hourly"
      log_level                = "WARN"
      performance_insights     = true
    }
  }
}

