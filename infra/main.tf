terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Data sources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_vpc" "main" {
  id = "vpc-016a23969cbf4e117"  # Your existing VPC
}

# Create a public subnet for our EC2 instance
resource "aws_subnet" "public" {
  vpc_id                  = data.aws_vpc.main.id
  cidr_block              = "172.31.0.0/24"  # Small subnet for our instance
  availability_zone       = "ap-southeast-2a"
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-public-subnet"
  })
}

# Create Internet Gateway if it doesn't exist
resource "aws_internet_gateway" "main" {
  vpc_id = data.aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "${var.project_name}-igw"
  })
}

# Create route table for public subnet
resource "aws_route_table" "public" {
  vpc_id = data.aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-public-rt"
  })
}

# Associate public subnet with route table
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Key pair
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-key"
  public_key = file(var.public_key_path)
}

# Security Group
resource "aws_security_group" "main" {
  name_prefix = "${var.project_name}-sg"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ingress_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# IAM Role
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for S3 access
resource "aws_iam_policy" "s3_policy" {
  count = var.create_s3 ? 1 : 0
  name  = "${var.project_name}-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.main[0].arn,
          "${aws_s3_bucket.main[0].arn}/*"
        ]
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for ECR access
resource "aws_iam_policy" "ecr_policy" {
  count = var.create_ecr ? 1 : 0
  name  = "${var.project_name}-ecr-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = var.create_ecr ? aws_ecr_repository.main[0].arn : ""
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for CloudWatch Logs
resource "aws_iam_policy" "cloudwatch_policy" {
  name = "${var.project_name}-cloudwatch-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })

  tags = var.tags
}

# Attach policies to role
resource "aws_iam_role_policy_attachment" "s3_attachment" {
  count      = var.create_s3 ? 1 : 0
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_policy[0].arn
}

resource "aws_iam_role_policy_attachment" "ecr_attachment" {
  count      = var.create_ecr ? 1 : 0
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ecr_policy[0].arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.cloudwatch_policy.arn
}

# Instance Profile
resource "aws_iam_instance_profile" "main" {
  name = "${var.project_name}-instance-profile"
  role = aws_iam_role.ec2_role.name

  tags = var.tags
}

# Elastic IP
resource "aws_eip" "main" {
  domain = "vpc"
  tags = merge(var.tags, {
    Name = "${var.project_name}-eip"
  })
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.main.key_name
  vpc_security_group_ids = [aws_security_group.main.id]
  subnet_id              = aws_subnet.public.id
  iam_instance_profile   = aws_iam_instance_profile.main.name

  user_data = file("${path.module}/user_data.sh")

  tags = merge(var.tags, {
    Name = "${var.project_name}-instance"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Associate Elastic IP
resource "aws_eip_association" "main" {
  instance_id   = aws_instance.main.id
  allocation_id = aws_eip.main.id
}
