output "public_ip" {
  value = aws_instance.biblioexchange.public_ip
}

output "instance_id" {
  value = aws_instance.biblioexchange.id
}
