variable "aws_region" {
  description = "Région AWS où créer le bucket et la table de lock"
  type        = string
  default     = "eu-west-3"
}

variable "bucket_name" {
  description = "Nom du bucket S3 pour le state Terraform (doit être globalement unique)"
  type        = string
  default     = "biblioexchange-terraform-state-228870477563"
}

variable "dynamodb_table_name" {
  description = "Nom de la table DynamoDB pour le lock Terraform"
  type        = string
  default     = "biblioexchange-terraform-lock"
}
