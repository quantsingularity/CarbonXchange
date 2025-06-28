# Enhanced Security Module Outputs for Financial Standards Compliance

# Security Groups
output "alb_security_group_id" {
  description = "ID of the Application Load Balancer security group"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "ID of the application security group"
  value       = aws_security_group.app.id
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.db.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis.id
}

output "monitoring_security_group_id" {
  description = "ID of the monitoring security group"
  value       = aws_security_group.monitoring.id
}

# KMS
output "kms_key_id" {
  description = "ID of the KMS key for encryption"
  value       = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  value       = aws_kms_key.main.arn
}

output "kms_alias_name" {
  description = "Name of the KMS key alias"
  value       = aws_kms_alias.main.name
}

# WAF
output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.id
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

# CloudTrail
output "cloudtrail_arn" {
  description = "ARN of the CloudTrail"
  value       = var.enable_cloudtrail ? aws_cloudtrail.main[0].arn : null
}

output "cloudtrail_bucket_name" {
  description = "Name of the CloudTrail S3 bucket"
  value       = var.enable_cloudtrail ? aws_s3_bucket.cloudtrail[0].bucket : null
}

output "cloudtrail_bucket_arn" {
  description = "ARN of the CloudTrail S3 bucket"
  value       = var.enable_cloudtrail ? aws_s3_bucket.cloudtrail[0].arn : null
}

# GuardDuty
output "guardduty_detector_id" {
  description = "ID of the GuardDuty detector"
  value       = var.enable_guardduty ? aws_guardduty_detector.main[0].id : null
}

# Config
output "config_recorder_name" {
  description = "Name of the Config configuration recorder"
  value       = var.enable_config ? aws_config_configuration_recorder.main[0].name : null
}

output "config_delivery_channel_name" {
  description = "Name of the Config delivery channel"
  value       = var.enable_config ? aws_config_delivery_channel.main[0].name : null
}

output "config_bucket_name" {
  description = "Name of the Config S3 bucket"
  value       = var.enable_config ? aws_s3_bucket.config[0].bucket : null
}

output "config_bucket_arn" {
  description = "ARN of the Config S3 bucket"
  value       = var.enable_config ? aws_s3_bucket.config[0].arn : null
}

# Security Hub
output "security_hub_account_id" {
  description = "Security Hub account ID"
  value       = var.enable_security_hub ? aws_securityhub_account.main[0].id : null
}

# Network ACLs
output "private_network_acl_id" {
  description = "ID of the private network ACL"
  value       = aws_network_acl.private.id
}

# VPC Flow Logs
output "vpc_flow_log_id" {
  description = "ID of the VPC Flow Log"
  value       = var.enable_vpc_flow_logs ? aws_flow_log.vpc[0].id : null
}

output "vpc_flow_log_group_name" {
  description = "Name of the VPC Flow Log CloudWatch Log Group"
  value       = var.enable_vpc_flow_logs ? aws_cloudwatch_log_group.vpc_flow_log[0].name : null
}

output "vpc_flow_log_group_arn" {
  description = "ARN of the VPC Flow Log CloudWatch Log Group"
  value       = var.enable_vpc_flow_logs ? aws_cloudwatch_log_group.vpc_flow_log[0].arn : null
}

# Secrets Manager
output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "db_credentials_secret_name" {
  description = "Name of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.name
}

# Parameter Store
output "app_parameter_names" {
  description = "Names of the application parameters in SSM Parameter Store"
  value       = [for k, v in aws_ssm_parameter.app_config : v.name]
}

output "app_parameter_arns" {
  description = "ARNs of the application parameters in SSM Parameter Store"
  value       = [for k, v in aws_ssm_parameter.app_config : v.arn]
}

# IAM Roles
output "config_role_arn" {
  description = "ARN of the Config IAM role"
  value       = var.enable_config ? aws_iam_role.config[0].arn : null
}

output "flow_log_role_arn" {
  description = "ARN of the VPC Flow Log IAM role"
  value       = var.enable_vpc_flow_logs ? aws_iam_role.flow_log[0].arn : null
}

# Security Configuration Summary
output "security_configuration" {
  description = "Summary of security configuration"
  value = {
    encryption_at_rest_enabled    = var.encryption_at_rest_required
    encryption_in_transit_enabled = var.encryption_in_transit_required
    minimum_tls_version          = var.minimum_tls_version
    mfa_required                 = var.require_mfa
    cloudtrail_enabled           = var.enable_cloudtrail
    guardduty_enabled            = var.enable_guardduty
    config_enabled               = var.enable_config
    security_hub_enabled         = var.enable_security_hub
    vpc_flow_logs_enabled        = var.enable_vpc_flow_logs
    waf_enabled                  = true
    geo_blocking_enabled         = var.enable_geo_blocking
    ddos_protection_enabled      = var.enable_ddos_protection
    data_classification          = var.data_classification
    compliance_standards         = var.compliance_standards
    log_retention_days           = var.log_retention_days
    backup_retention_days        = var.backup_retention_days
    rto_minutes                  = var.rto_minutes
    rpo_minutes                  = var.rpo_minutes
  }
}

# Compliance Outputs
output "compliance_report" {
  description = "Compliance configuration report"
  value = {
    standards_covered = var.compliance_standards
    audit_logging = {
      cloudtrail_enabled = var.enable_cloudtrail
      vpc_flow_logs     = var.enable_vpc_flow_logs
      config_enabled    = var.enable_config
      log_retention     = var.log_retention_days
    }
    data_protection = {
      encryption_at_rest    = var.encryption_at_rest_required
      encryption_in_transit = var.encryption_in_transit_required
      kms_key_rotation     = true
      secrets_management   = true
      data_classification  = var.data_classification
    }
    access_control = {
      mfa_required           = var.require_mfa
      least_privilege        = true
      network_segmentation   = true
      security_groups        = true
      network_acls          = true
    }
    monitoring_detection = {
      guardduty_enabled     = var.enable_guardduty
      security_hub_enabled  = var.enable_security_hub
      waf_protection       = true
      vulnerability_scanning = true
    }
    incident_response = {
      automated_alerting    = true
      centralized_logging   = true
      forensic_capabilities = true
    }
    business_continuity = {
      backup_strategy      = true
      disaster_recovery    = true
      rto_minutes         = var.rto_minutes
      rpo_minutes         = var.rpo_minutes
      multi_az_deployment = true
    }
  }
}

# Cost and Resource Tracking
output "resource_tags" {
  description = "Common resource tags applied"
  value       = var.common_tags
}

output "cost_allocation_tags" {
  description = "Tags for cost allocation and tracking"
  value = {
    Application   = var.app_name
    Environment   = var.environment
    CostCenter    = var.cost_center
    DataClass     = var.data_classification
    Compliance    = join(",", var.compliance_standards)
  }
}

# Security Metrics and KPIs
output "security_metrics" {
  description = "Security metrics and KPIs for monitoring"
  value = {
    security_groups_count    = 5  # alb, app, db, redis, monitoring
    network_acls_count      = 1
    kms_keys_count          = 1
    secrets_count           = 1
    waf_rules_count         = 4
    cloudwatch_log_groups   = var.enable_vpc_flow_logs ? 1 : 0
    compliance_services = {
      cloudtrail    = var.enable_cloudtrail
      guardduty     = var.enable_guardduty
      config        = var.enable_config
      security_hub  = var.enable_security_hub
    }
  }
}

