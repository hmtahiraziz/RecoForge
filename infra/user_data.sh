#!/bin/bash
set -eux

# Update system
apt-get update

# Install prerequisites
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    unzip \
    jq

# Install Docker CE
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install Caddy
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

apt-get update
apt-get install -y caddy

# Enable and start Caddy
systemctl enable caddy
systemctl start caddy

# Create app directory
mkdir -p /opt/app
chown ubuntu:ubuntu /opt/app

# Create initial Caddyfile
cat > /etc/caddy/Caddyfile << 'EOF'
:80 {
    reverse_proxy localhost:3000
}
EOF

# Reload Caddy configuration
systemctl reload caddy

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Create swap file for small instances (1GB)
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Set up log rotation for Docker
cat > /etc/logrotate.d/docker << 'EOF'
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF

# Create a simple health check script
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash
# Simple health check script
echo "System uptime: $(uptime)"
echo "Docker status: $(systemctl is-active docker)"
echo "Caddy status: $(systemctl is-active caddy)"
echo "Disk usage: $(df -h /)"
echo "Memory usage: $(free -h)"
EOF

chmod +x /opt/health-check.sh
chown ubuntu:ubuntu /opt/health-check.sh

# Log completion
echo "User data script completed successfully at $(date)" >> /var/log/user-data.log
