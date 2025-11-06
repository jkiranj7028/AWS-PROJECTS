provider "aws" {
  region = "ap-south-1" # Or your preferred region
}

# Dynamically get the latest Amazon Linux 2023 AMI
data "aws_ssm_parameter" "al2023_ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# ------------------------------------------------------------------
# IAM Role and Instance Profile for the Jenkins EC2 Instance
# ------------------------------------------------------------------

# Assume Role Policy for EC2
data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "jenkins_iam_role" {
  name               = "JenkinsIAMRole"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

# Inline policy with CI/CD permissions
resource "aws_iam_role_policy" "jenkins_cicd_policy" {
  name = "JenkinsCICDPermissions"
  role = aws_iam_role.jenkins_iam_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          # Permissions for ECS & ECR
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "s3:GetObject",
          "s3:PutObject",
          # CRITICAL: Allow Jenkins to pass roles to ECS Tasks
          "iam:PassRole"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "jenkins_instance_profile" {
  name = "JenkinsInstanceProfile"
  path = "/"
  role = aws_iam_role.jenkins_iam_role.name
}

# ------------------------------------------------------------------
# Security Group for the Instance
# ------------------------------------------------------------------
resource "aws_security_group" "jenkins_sg" {
  name        = "Jenkins-SG"
  description = "Allow SSH (22) and Jenkins (8080) access"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  ingress {
    description = "Jenkins UI access"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  tags = {
    Name = "Jenkins-SG"
  }
}

# ------------------------------------------------------------------
# The EC2 Instance
# ------------------------------------------------------------------
resource "aws_instance" "jenkins_instance" {
  instance_type               = var.instance_type
  key_name                    = var.key_name
  ami                         = data.aws_ssm_parameter.al2023_ami.value
  iam_instance_profile        = aws_iam_instance_profile.jenkins_instance_profile.name
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.jenkins_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "Jenkins-Server"
  }

  # --- This UserData script installs and configures everything ---
  user_data = <<-EOT
    #!/bin/bash
    set -ex
    dnf update -y
    dnf install -y java-17-amazon-corretto
    wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
    rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
    sed -i 's/jenkins.io.key/jenkins.io-2023.key/g' /etc/yum.repos.d/jenkins.repo
    dnf upgrade -y
    dnf install -y jenkins git docker
    systemctl enable docker
    systemctl start docker
    usermod -aG docker jenkins
    systemctl enable jenkins
    systemctl start jenkins
    systemctl restart jenkins
  EOT
}