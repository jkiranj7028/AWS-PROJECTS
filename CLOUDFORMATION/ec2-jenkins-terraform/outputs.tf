output "instance_id" {
  description = "The Instance ID of the new Jenkins server"
  value       = aws_instance.jenkins_instance.id
}

output "jenkins_url" {
  description = "The URL to access the Jenkins UI"
  value       = "http://${aws_instance.jenkins_instance.public_dns}:8080"
}

output "initial_password_command" {
  description = "Run this command on the EC2 instance to get the admin password"
  value       = "sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
}

output "ssh_command" {
  description = "The command to SSH into your instance"
  value       = "ssh -i <your-key.pem> ec2-user@${aws_instance.jenkins_instance.public_dns}"
}