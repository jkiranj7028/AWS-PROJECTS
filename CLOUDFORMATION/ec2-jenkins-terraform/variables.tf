variable "vpc_id" {
  type        = string
  description = "Select the VPC you want to deploy the Jenkins server into."
  default     = "vpc-011749974e90998ae" # <-- REPLACE THIS
}

variable "subnet_id" {
  type        = string
  description = "Select a public subnet (with an Internet Gateway) for the EC2 instance."
  default     = "subnet-01acb027d1ff08b21" # <-- REPLACE THIS
}

variable "my_ip" {
  type        = string
  description = "Your current public IP address CIDR. This will be used to restrict SSH (22) and Jenkins (8080) access."
  default     = "49.37.148.50/32" # <-- REPLACE THIS with your own IP (e.g., "1.2.3.4/32")
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for the Jenkins server."
  default     = "t3.small"
  validation {
    condition     = contains(["t3.small", "t3.medium", "t3.large", "t2.small", "t2.medium", "t2.large", "m7i-flex.large"], var.instance_type)
    error_message = "Must be a valid, approved instance type."
  }
}

variable "key_name" {
  type        = string
  description = "Name of your existing EC2 KeyPair for SSH access."
  default     = "minikube-key" # <-- REPLACE THIS
}