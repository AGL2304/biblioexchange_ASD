terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Volontairement PAS de backend "s3" ici :
  # ce projet crée l'infra qui hébergera le state des AUTRES projets Terraform.
  # Son propre state reste local (fichier tout petit, sans secret), à ne pas versionner.
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------
# Bucket S3 pour stocker le terraform.tfstate du projet principal
# ---------------------------------------------------------
resource "aws_s3_bucket" "terraform_state" {
  bucket = var.bucket_name

  # Empêche la suppression accidentelle du bucket via terraform destroy
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name    = "biblioexchange-terraform-state"
    Project = "BiblioExchange-ASD"
  }
}

# Versioning : permet de revenir à une version antérieure du state en cas de corruption
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Chiffrement au repos (AES-256, géré par S3)
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Blocage total de l'accès public — le state ne doit jamais être exposé
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ---------------------------------------------------------
# Table DynamoDB pour le verrouillage (empêche deux "terraform apply" simultanés)
# ---------------------------------------------------------
resource "aws_dynamodb_table" "terraform_lock" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name    = "biblioexchange-terraform-lock"
    Project = "BiblioExchange-ASD"
  }
}
