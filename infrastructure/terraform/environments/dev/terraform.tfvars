# Development Environment Configuration
# WARNING: This file contains example values only
# For actual deployment, use terraform.tfvars (gitignored) or env variables

aws_region  = "us-west-2"
environment = "dev"
app_name    = "carbonxchange"

vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["us-west-2a", "us-west-2b", "us-west-2c"]
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

instance_type = "t3.micro"
key_name      = null # Set via: export TF_VAR_key_name="your-key"

db_instance_class = "db.t3.micro"
db_name           = "carbonxchangedb"
db_username       = "dbadmin"
# SECURITY: Set via environment variable
# export TF_VAR_db_password="your-secure-password"
db_password = null # Must be provided via env var or CLI

default_tags = {
  Terraform   = "true"
  Environment = "dev"
  Project     = "carbonxchange"
}
