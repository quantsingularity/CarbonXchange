# Enhanced Database Module Outputs for Financial Standards Compliance

# Primary Database Instance
output "db_instance_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.main.identifier
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "db_instance_hosted_zone_id" {
  description = "RDS instance hosted zone ID"
  value       = aws_db_instance.main.hosted_zone_id
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_instance_status" {
  description = "RDS instance status"
  value       = aws_db_instance.main.status
}

output "db_instance_engine" {
  description = "RDS instance engine"
  value       = aws_db_instance.main.engine
}

output "db_instance_engine_version" {
  description = "RDS instance engine version"
  value       = aws_db_instance.main.engine_version
}

output "db_instance_class" {
  description = "RDS instance class"
  value       = aws_db_instance.main.instance_class
}

output "db_instance_allocated_storage" {
  description = "RDS instance allocated storage"
  value       = aws_db_instance.main.allocated_storage
}

output "db_instance_storage_type" {
  description = "RDS instance storage type"
  value       = aws_db_instance.main.storage_type
}

output "db_instance_storage_encrypted" {
  description = "Whether RDS instance storage is encrypted"
  value       = aws_db_instance.main.storage_encrypted
}

output "db_instance_kms_key_id" {
  description = "RDS instance KMS key ID"
  value       = aws_db_instance.main.kms_key_id
}

output "db_instance_multi_az" {
  description = "Whether RDS instance is Multi-AZ"
  value       = aws_db_instance.main.multi_az
}

output "db_instance_availability_zone" {
  description = "RDS instance availability zone"
  value       = aws_db_instance.main.availability_zone
}

output "db_instance_backup_retention_period" {
  description = "RDS instance backup retention period"
  value       = aws_db_instance.main.backup_retention_period
}

output "db_instance_backup_window" {
  description = "RDS instance backup window"
  value       = aws_db_instance.main.backup_window
}

output "db_instance_maintenance_window" {
  description = "RDS instance maintenance window"
  value       = aws_db_instance.main.maintenance_window
}

# Read Replicas
output "read_replica_identifiers" {
  description = "List of read replica identifiers"
  value       = var.create_read_replica ? aws_db_instance.read_replica[*].identifier : []
}

output "read_replica_endpoints" {
  description = "List of read replica endpoints"
  value       = var.create_read_replica ? aws_db_instance.read_replica[*].endpoint : []
  sensitive   = true
}

output "read_replica_arns" {
  description = "List of read replica ARNs"
  value       = var.create_read_replica ? aws_db_instance.read_replica[*].arn : []
}

# Database Proxy
output "db_proxy_id" {
  description = "RDS Proxy identifier"
  value       = var.create_db_proxy ? aws_db_proxy.main[0].id : null
}

output "db_proxy_arn" {
  description = "RDS Proxy ARN"
  value       = var.create_db_proxy ? aws_db_proxy.main[0].arn : null
}

output "db_proxy_endpoint" {
  description = "RDS Proxy endpoint"
  value       = var.create_db_proxy ? aws_db_proxy.main[0].endpoint : null
  sensitive   = true
}

# Subnet Group
output "db_subnet_group_id" {
  description = "DB subnet group identifier"
  value       = aws_db_subnet_group.main.id
}

output "db_subnet_group_arn" {
  description = "DB subnet group ARN"
  value       = aws_db_subnet_group.main.arn
}

# Parameter Group
output "db_parameter_group_id" {
  description = "DB parameter group identifier"
  value       = aws_db_parameter_group.main.id
}

output "db_parameter_group_arn" {
  description = "DB parameter group ARN"
  value       = aws_db_parameter_group.main.arn
}

# Option Group
output "db_option_group_id" {
  description = "DB option group identifier"
  value       = var.create_option_group ? aws_db_option_group.main[0].id : null
}

output "db_option_group_arn" {
  description = "DB option group ARN"
  value       = var.create_option_group ? aws_db_option_group.main[0].arn : null
}

# KMS Key
output "kms_key_id" {
  description = "KMS key ID for database encryption"
  value       = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for database encryption"
  value       = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn
}

output "kms_alias_name" {
  description = "KMS key alias name"
  value       = var.kms_key_id != "" ? null : aws_kms_alias.database[0].name
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

output "db_credentials_secret_version_id" {
  description = "Version ID of the database credentials secret"
  value       = aws_secretsmanager_secret_version.db_credentials.version_id
}

# CloudWatch Log Groups
output "cloudwatch_log_group_names" {
  description = "Names of CloudWatch log groups"
  value       = [for log_group in aws_cloudwatch_log_group.database_logs : log_group.name]
}

output "cloudwatch_log_group_arns" {
  description = "ARNs of CloudWatch log groups"
  value       = [for log_group in aws_cloudwatch_log_group.database_logs : log_group.arn]
}

# Enhanced Monitoring
output "enhanced_monitoring_role_arn" {
  description = "ARN of the enhanced monitoring IAM role"
  value       = var.enhanced_monitoring_interval > 0 || (var.create_read_replica && var.read_replica_monitoring_interval > 0) ? aws_iam_role.enhanced_monitoring[0].arn : null
}

# Backup S3 Bucket
output "backup_bucket_id" {
  description = "ID of the backup S3 bucket"
  value       = var.create_backup_bucket ? aws_s3_bucket.database_backups[0].id : null
}

output "backup_bucket_arn" {
  description = "ARN of the backup S3 bucket"
  value       = var.create_backup_bucket ? aws_s3_bucket.database_backups[0].arn : null
}

output "backup_bucket_domain_name" {
  description = "Domain name of the backup S3 bucket"
  value       = var.create_backup_bucket ? aws_s3_bucket.database_backups[0].bucket_domain_name : null
}

# Connection Information
output "connection_info" {
  description = "Database connection information"
  value = {
    primary_endpoint = aws_db_instance.main.endpoint
    proxy_endpoint   = var.create_db_proxy ? aws_db_proxy.main[0].endpoint : null
    port             = aws_db_instance.main.port
    database_name    = aws_db_instance.main.db_name
    username         = aws_db_instance.main.username
    engine           = aws_db_instance.main.engine
    engine_version   = aws_db_instance.main.engine_version
  }
  sensitive = true
}

# Security Configuration
output "security_configuration" {
  description = "Database security configuration summary"
  value = {
    storage_encrypted               = aws_db_instance.main.storage_encrypted
    kms_key_id                      = aws_db_instance.main.kms_key_id
    deletion_protection             = aws_db_instance.main.deletion_protection
    backup_retention_period         = aws_db_instance.main.backup_retention_period
    multi_az                        = aws_db_instance.main.multi_az
    publicly_accessible             = aws_db_instance.main.publicly_accessible
    ca_cert_identifier              = aws_db_instance.main.ca_cert_identifier
    performance_insights_enabled    = aws_db_instance.main.performance_insights_enabled
    enhanced_monitoring_interval    = aws_db_instance.main.monitoring_interval
    enabled_cloudwatch_logs_exports = aws_db_instance.main.enabled_cloudwatch_logs_exports
  }
}

# Compliance Information
output "compliance_status" {
  description = "Compliance status and configuration"
  value = {
    standards_covered              = var.compliance_standards
    data_classification            = var.data_classification
    encryption_at_rest             = aws_db_instance.main.storage_encrypted
    encryption_in_transit          = true # Enforced via parameter group
    audit_logging_enabled          = contains(var.enabled_cloudwatch_logs_exports, "audit")
    backup_retention_compliant     = aws_db_instance.main.backup_retention_period >= 2555
    multi_az_enabled               = aws_db_instance.main.multi_az
    deletion_protection_enabled    = aws_db_instance.main.deletion_protection
    performance_monitoring_enabled = aws_db_instance.main.performance_insights_enabled
    enhanced_monitoring_enabled    = aws_db_instance.main.monitoring_interval > 0
    secrets_management_enabled     = true
    network_isolation_enabled      = !aws_db_instance.main.publicly_accessible
  }
}

# Performance Metrics
output "performance_configuration" {
  description = "Performance configuration details"
  value = {
    instance_class                        = aws_db_instance.main.instance_class
    allocated_storage                     = aws_db_instance.main.allocated_storage
    max_allocated_storage                 = aws_db_instance.main.max_allocated_storage
    storage_type                          = aws_db_instance.main.storage_type
    iops                                  = aws_db_instance.main.iops
    performance_insights_enabled          = aws_db_instance.main.performance_insights_enabled
    performance_insights_retention_period = aws_db_instance.main.performance_insights_retention_period
    enhanced_monitoring_interval          = aws_db_instance.main.monitoring_interval
    read_replica_count                    = var.create_read_replica ? var.read_replica_count : 0
    proxy_enabled                         = var.create_db_proxy
  }
}

# Cost Information
output "cost_optimization_features" {
  description = "Cost optimization features enabled"
  value = {
    storage_autoscaling_enabled = aws_db_instance.main.max_allocated_storage > aws_db_instance.main.allocated_storage
    reserved_instance_eligible  = true
    backup_lifecycle_management = var.create_backup_bucket
    read_replica_optimization   = var.create_read_replica
    proxy_connection_pooling    = var.create_db_proxy
  }
}

# Disaster Recovery Information
output "disaster_recovery_configuration" {
  description = "Disaster recovery configuration"
  value = {
    multi_az_enabled               = aws_db_instance.main.multi_az
    automated_backups_enabled      = aws_db_instance.main.backup_retention_period > 0
    backup_retention_period        = aws_db_instance.main.backup_retention_period
    backup_window                  = aws_db_instance.main.backup_window
    maintenance_window             = aws_db_instance.main.maintenance_window
    read_replicas_count            = var.create_read_replica ? var.read_replica_count : 0
    cross_region_backup_enabled    = var.cross_region_backup_enabled
    point_in_time_recovery_enabled = aws_db_instance.main.backup_retention_period > 0
    deletion_protection_enabled    = aws_db_instance.main.deletion_protection
    final_snapshot_enabled         = !var.skip_final_snapshot
  }
}

# Monitoring Endpoints
output "monitoring_endpoints" {
  description = "Monitoring and observability endpoints"
  value = {
    cloudwatch_logs              = [for log_group in aws_cloudwatch_log_group.database_logs : log_group.name]
    performance_insights_enabled = aws_db_instance.main.performance_insights_enabled
    enhanced_monitoring_enabled  = aws_db_instance.main.monitoring_interval > 0
    metrics_namespace            = "AWS/RDS"
    primary_instance_id          = aws_db_instance.main.identifier
    read_replica_ids             = var.create_read_replica ? aws_db_instance.read_replica[*].identifier : []
  }
}

# Network Configuration
output "network_configuration" {
  description = "Network configuration details"
  value = {
    subnet_group_name      = aws_db_subnet_group.main.name
    vpc_security_group_ids = var.security_group_ids
    availability_zone      = aws_db_instance.main.availability_zone
    publicly_accessible    = aws_db_instance.main.publicly_accessible
    port                   = aws_db_instance.main.port
    proxy_vpc_id           = var.create_db_proxy ? aws_db_proxy.main[0].vpc_id : null
  }
}

# Resource Tags
output "resource_tags" {
  description = "Tags applied to database resources"
  value = merge(var.common_tags, {
    DatabaseEngine     = aws_db_instance.main.engine
    Environment        = var.environment
    Compliance         = join(",", var.compliance_standards)
    DataClassification = var.data_classification
    BackupRetention    = aws_db_instance.main.backup_retention_period
    MultiAZ            = aws_db_instance.main.multi_az
    Encrypted          = aws_db_instance.main.storage_encrypted
  })
}

# Resource Inventory
output "resource_inventory" {
  description = "Inventory of created database resources"
  value = {
    primary_instance_count      = 1
    read_replica_count          = var.create_read_replica ? var.read_replica_count : 0
    subnet_group_count          = 1
    parameter_group_count       = 1
    option_group_count          = var.create_option_group ? 1 : 0
    kms_key_count               = var.kms_key_id == "" ? 1 : 0
    secrets_count               = 1
    cloudwatch_log_groups_count = length(var.enabled_cloudwatch_logs_exports)
    iam_roles_count             = var.enhanced_monitoring_interval > 0 || (var.create_read_replica && var.read_replica_monitoring_interval > 0) ? 1 : 0
    s3_buckets_count            = var.create_backup_bucket ? 1 : 0
    proxy_count                 = var.create_db_proxy ? 1 : 0
  }
}
