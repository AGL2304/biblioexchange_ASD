terraform {
  backend "s3" {
    bucket       = "biblioexchange-terraform-state-228870477563"
    key          = "biblioexchange/terraform.tfstate"
    region       = "eu-west-3"
    use_lockfile = true
    encrypt      = true
  }
}
