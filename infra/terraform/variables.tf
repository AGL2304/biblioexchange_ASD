variable "aws_region" {
  default = "eu-west-3"
}

variable "ami_id" {
  description = "AMI Ubuntu 24.04 LTS de la région choisie"
  type        = string
}

variable "instance_type" {
  default = "t3.micro"
}

variable "key_name" {
  description = "Nom de la paire de clés SSH existante sur AWS"
  type        = string
}

variable "admin_cidr" {
  description = "CIDR autorisé pour le SSH (ex: votre IP publique /32)"
  type        = string
}
