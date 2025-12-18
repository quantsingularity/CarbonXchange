# Enhanced Database Module for Financial Standards Compliance
# This module implements comprehensive database infrastructure for CarbonXchange

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random password generation for additional security
resource "random_password" "master_password" {
  count   = var.manage_master_user_password ? 0 : 1
  length  = 32
  special = true
}

# KMS key for database encryption (if not provided)
resource "aws_kms_key" "database" {
  count                   = var.kms_key_id == "" ? 1 : 0
  description             = "KMS key for ${var.db_name} ${var.environment} database encryption"
  deletion_window_in_days = var.kms_deletion_window
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow RDS Service"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:CreateGrant"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-database-kms-key"
    Type = "encryption"
  })
}

resource "aws_kms_alias" "database" {
  count         = var.kms_key_id == "" ? 1 : 0
  name          = "alias/${var.db_name}-${var.environment}-database-key"
  target_key_id = aws_kms_key.database[0].key_id
}

# Enhanced DB Subnet Group with additional security
resource "aws_db_subnet_group" "main" {
  name       = "${var.db_name}-${var.environment}-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-subnet-group"
    Type = "database-networking"
  })
}

# Custom DB Parameter Group for security hardening
resource "aws_db_parameter_group" "main" {
  family = var.parameter_group_family
  name   = "${var.db_name}-${var.environment}-params"

  # Security hardening parameters
  dynamic "parameter" {
    for_each = var.db_parameters
    content {
      name  = parameter.value.name
      value = parameter.value.value
    }
  }

  # Financial compliance parameters
  parameter {
    name  = "log_bin_trust_function_creators"
    value = "0"
  }

  parameter {
    name  = "general_log"
    value = "1"
  }

  parameter {
    name  = "slow_query_log"
    value = "1"
  }

  parameter {
    name  = "long_query_time"
    value = var.slow_query_log_threshold
  }

  parameter {
    name  = "log_queries_not_using_indexes"
    value = "1"
  }

  parameter {
    name  = "innodb_file_per_table"
    value = "1"
  }

  parameter {
    name  = "innodb_flush_log_at_trx_commit"
    value = "1"
  }

  parameter {
    name  = "sync_binlog"
    value = "1"
  }

  parameter {
    name  = "max_connections"
    value = var.max_connections
  }

  parameter {
    name  = "connect_timeout"
    value = var.connect_timeout
  }

  parameter {
    name  = "wait_timeout"
    value = var.wait_timeout
  }

  parameter {
    name  = "interactive_timeout"
    value = var.interactive_timeout
  }

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-parameter-group"
    Type = "database-configuration"
  })
}

# Custom DB Option Group for enhanced features
resource "aws_db_option_group" "main" {
  count                    = var.create_option_group ? 1 : 0
  name                     = "${var.db_name}-${var.environment}-options"
  option_group_description = "Option group for ${var.db_name} ${var.environment}"
  engine_name              = var.engine
  major_engine_version     = var.major_engine_version

  dynamic "option" {
    for_each = var.db_options
    content {
      option_name = option.value.option_name

      dynamic "option_settings" {
        for_each = option.value.option_settings
        content {
          name  = option_settings.value.name
          value = option_settings.value.value
        }
      }
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-option-group"
    Type = "database-configuration"
  })
}

# Primary RDS Instance with enhanced security
resource "aws_db_instance" "main" {
  # Basic Configuration
  identifier     = "${var.db_name}-${var.environment}"
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.db_instance_class

  # Storage Configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = true
  kms_key_id            = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn
  iops                  = var.storage_type == "io1" || var.storage_type == "io2" ? var.iops : null
  storage_throughput    = var.storage_type == "gp3" ? var.storage_throughput : null

  # Database Configuration
  db_name  = var.db_name
  username = var.db_username
  password = var.manage_master_user_password ? null : (var.db_password != "" ? var.db_password : random_password.master_password[0].result)

  # Master User Password Management (AWS managed)
  manage_master_user_password   = var.manage_master_user_password
  master_user_secret_kms_key_id = var.manage_master_user_password ? (var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn) : null

  # Network Configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids
  publicly_accessible    = false
  port                   = var.port

  # Parameter and Option Groups
  parameter_group_name = aws_db_parameter_group.main.name
  option_group_name    = var.create_option_group ? aws_db_option_group.main[0].name : null

  # Backup Configuration
  backup_retention_period   = var.backup_retention_period
  backup_window             = var.backup_window
  copy_tags_to_snapshot     = true
  delete_automated_backups  = false
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.db_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Maintenance Configuration
  maintenance_window          = var.maintenance_window
  auto_minor_version_upgrade  = var.auto_minor_version_upgrade
  allow_major_version_upgrade = var.allow_major_version_upgrade

  # High Availability
  multi_az          = var.multi_az
  availability_zone = var.multi_az ? null : var.availability_zone

  # Monitoring and Logging
  monitoring_interval = var.enhanced_monitoring_interval
  monitoring_role_arn = var.enhanced_monitoring_interval > 0 ? aws_iam_role.enhanced_monitoring[0].arn : null

  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_kms_key_id       = var.performance_insights_enabled ? (var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn) : null
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null

  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports

  # Security
  ca_cert_identifier = var.ca_cert_identifier

  # Lifecycle
  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      password,
      final_snapshot_identifier
    ]
  }

  tags = merge(var.common_tags, {
    Name               = "${var.db_name}-${var.environment}"
    Type               = "database-primary"
    Compliance         = join(",", var.compliance_standards)
    DataClassification = var.data_classification
    BackupRetention    = var.backup_retention_period
  })

  depends_on = [
    aws_db_parameter_group.main,
    aws_iam_role.enhanced_monitoring
  ]
}

# Read Replica for disaster recovery and read scaling
resource "aws_db_instance" "read_replica" {
  count = var.create_read_replica ? var.read_replica_count : 0

  identifier = "${var.db_name}-${var.environment}-replica-${count.index + 1}"

  # Replica Configuration
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = var.read_replica_instance_class

  # Storage (inherited from source but can be modified)
  allocated_storage     = var.read_replica_allocated_storage
  max_allocated_storage = var.read_replica_max_allocated_storage
  storage_type          = var.read_replica_storage_type
  storage_encrypted     = true
  iops                  = var.read_replica_storage_type == "io1" || var.read_replica_storage_type == "io2" ? var.read_replica_iops : null

  # Network Configuration
  publicly_accessible = false
  availability_zone   = var.read_replica_availability_zones[count.index % length(var.read_replica_availability_zones)]

  # Monitoring
  monitoring_interval = var.read_replica_monitoring_interval
  monitoring_role_arn = var.read_replica_monitoring_interval > 0 ? aws_iam_role.enhanced_monitoring[0].arn : null

  performance_insights_enabled          = var.read_replica_performance_insights_enabled
  performance_insights_kms_key_id       = var.read_replica_performance_insights_enabled ? (var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn) : null
  performance_insights_retention_period = var.read_replica_performance_insights_enabled ? var.performance_insights_retention_period : null

  # Backup (read replicas don't support automated backups)
  backup_retention_period = 0
  copy_tags_to_snapshot   = true
  deletion_protection     = var.read_replica_deletion_protection
  skip_final_snapshot     = var.read_replica_skip_final_snapshot

  # Maintenance
  maintenance_window         = var.read_replica_maintenance_window
  auto_minor_version_upgrade = var.read_replica_auto_minor_version_upgrade

  tags = merge(var.common_tags, {
    Name         = "${var.db_name}-${var.environment}-replica-${count.index + 1}"
    Type         = "database-replica"
    ReplicaIndex = count.index + 1
  })

  depends_on = [aws_db_instance.main]
}

# Enhanced Monitoring IAM Role
resource "aws_iam_role" "enhanced_monitoring" {
  count = var.enhanced_monitoring_interval > 0 || (var.create_read_replica && var.read_replica_monitoring_interval > 0) ? 1 : 0
  name  = "${var.db_name}-${var.environment}-rds-enhanced-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-enhanced-monitoring-role"
    Type = "database-monitoring"
  })
}

resource "aws_iam_role_policy_attachment" "enhanced_monitoring" {
  count      = var.enhanced_monitoring_interval > 0 || (var.create_read_replica && var.read_replica_monitoring_interval > 0) ? 1 : 0
  role       = aws_iam_role.enhanced_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Database Proxy for connection pooling and security
resource "aws_db_proxy" "main" {
  count         = var.create_db_proxy ? 1 : 0
  name          = "${var.db_name}-${var.environment}-proxy"
  engine_family = var.proxy_engine_family
  auth {
    auth_scheme = "SECRETS"
    secret_arn  = aws_secretsmanager_secret.db_credentials.arn
  }

  role_arn                     = aws_iam_role.db_proxy[0].arn
  vpc_subnet_ids               = var.private_subnet_ids
  require_tls                  = true
  idle_client_timeout          = var.proxy_idle_client_timeout
  max_connections_percent      = var.proxy_max_connections_percent
  max_idle_connections_percent = var.proxy_max_idle_connections_percent

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-proxy"
    Type = "database-proxy"
  })
}

resource "aws_db_proxy_default_target_group" "main" {
  count         = var.create_db_proxy ? 1 : 0
  db_proxy_name = aws_db_proxy.main[0].name

  connection_pool_config {
    connection_borrow_timeout    = var.proxy_connection_borrow_timeout
    init_query                   = var.proxy_init_query
    max_connections_percent      = var.proxy_max_connections_percent
    max_idle_connections_percent = var.proxy_max_idle_connections_percent
    session_pinning_filters      = var.proxy_session_pinning_filters
  }
}

resource "aws_db_proxy_target" "main" {
  count                  = var.create_db_proxy ? 1 : 0
  db_instance_identifier = aws_db_instance.main.identifier
  db_proxy_name          = aws_db_proxy.main[0].name
  target_group_name      = aws_db_proxy_default_target_group.main[0].name
}

# IAM Role for DB Proxy
resource "aws_iam_role" "db_proxy" {
  count = var.create_db_proxy ? 1 : 0
  name  = "${var.db_name}-${var.environment}-db-proxy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-db-proxy-role"
    Type = "database-proxy"
  })
}

resource "aws_iam_role_policy" "db_proxy" {
  count = var.create_db_proxy ? 1 : 0
  name  = "${var.db_name}-${var.environment}-db-proxy-policy"
  role  = aws_iam_role.db_proxy[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${data.aws_region.current.name}.amazonaws.com"
          }
        }
      }
    ]
  })
}

# Secrets Manager for database credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.db_name}-${var.environment}-db-credentials"
  description             = "Database credentials for ${var.db_name} ${var.environment}"
  kms_key_id              = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn
  recovery_window_in_days = var.secret_recovery_window

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-db-credentials"
    Type = "database-secrets"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.manage_master_user_password ? "managed-by-aws" : (var.db_password != "" ? var.db_password : random_password.master_password[0].result)
    engine   = var.engine
    host     = aws_db_instance.main.endpoint
    port     = var.port
    dbname   = var.db_name
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# CloudWatch Log Groups for database logs
resource "aws_cloudwatch_log_group" "database_logs" {
  for_each = toset(var.enabled_cloudwatch_logs_exports)

  name              = "/aws/rds/instance/${aws_db_instance.main.identifier}/${each.value}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-${each.value}-logs"
    Type = "database-logging"
  })
}

# Automated Backup to S3 (for additional compliance)
resource "aws_s3_bucket" "database_backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = "${var.db_name}-${var.environment}-database-backups-${random_id.backup_bucket_suffix[0].hex}"

  tags = merge(var.common_tags, {
    Name = "${var.db_name}-${var.environment}-database-backups"
    Type = "database-backup"
  })
}

resource "random_id" "backup_bucket_suffix" {
  count       = var.create_backup_bucket ? 1 : 0
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "database_backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.database_backups[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "database_backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.database_backups[0].id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.database[0].arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "database_backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.database_backups[0].id

  rule {
    id     = "backup_lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = var.backup_retention_period * 365 # Convert years to days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "aws_s3_bucket_public_access_block" "database_backups" {
  count  = var.create_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.database_backups[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
