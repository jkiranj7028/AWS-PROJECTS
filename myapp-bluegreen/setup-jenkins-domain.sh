#!/usr/bin/env bash
# --------------------------------------------------------------------
# Script: setup-jenkins-cloudfront.sh
# Purpose: Configure Jenkins with Nginx, CloudFront & Route53 (HTTPS)
# OS: Amazon Linux 2023
# Cost Optimization: Uses Free Tier (t2.micro, ACM, CloudFront Free Tier)
# --------------------------------------------------------------------

set -euo pipefail

# === CONFIGURATION ===
DOMAIN="jenkins.devopscloudai.com"
ROOT_DOMAIN="devopscloudai.com"
JENKINS_PORT="8080"
AWS_REGION="ap-south-1"
AWS_REGION_US="us-east-1"    # update to your region
#EMAIL="admin@${ROOT_DOMAIN}"

echo "🌍 Starting Jenkins + CloudFront + Route53 setup for ${DOMAIN}..."

# === UPDATE SYSTEM ===
sudo dnf update -y

# === INSTALL DEPENDENCIES ===
echo "📦 Installing dependencies (Nginx, AWS CLI, Firewalld)..."
sudo dnf install -y nginx awscli firewalld jq

# === START FIREWALL ===
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

# === ENABLE & START NGINX ===
sudo systemctl enable nginx
sudo systemctl start nginx

# === CREATE NGINX CONFIG (REVERSE PROXY) ===
NGINX_CONF="/etc/nginx/conf.d/jenkins.conf"
echo "🧱 Configuring Nginx reverse proxy for Jenkins..."
sudo tee $NGINX_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${JENKINS_PORT}; # No trailing slash
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Cache optimization
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 30d;
        access_log off;
        add_header Cache-Control "public";
        proxy_pass http://127.0.0.1:${JENKINS_PORT}; # No trailing slash here for assets
    }
}
EOF

sudo nginx -t
sudo systemctl reload nginx

# === GET EC2 PUBLIC DNS / IP ===
# Use IMDSv2 for Amazon Linux 2023 and newer
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
EC2_DNS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-hostname)
EC2_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.245/latest/meta-data/public-ipv4)

echo "✅ EC2 Public DNS: ${EC2_DNS}"
echo "✅ EC2 Public IP: ${EC2_IP}"

# === CREATE/VALIDATE ACM CERTIFICATE ===
echo "🔐 Requesting ACM Certificate for ${DOMAIN}..."
CERT_ARN=$(aws acm list-certificates --region ${AWS_REGION_US} \
  --query "CertificateSummaryList[?DomainName=='${DOMAIN}'].CertificateArn" --output text)

if [ -z "$CERT_ARN" ]; then
  CERT_ARN=$(aws acm request-certificate \
    --domain-name "${DOMAIN}" \
    --validation-method DNS \
    --region ${AWS_REGION_US} \
    --query CertificateArn --output text)
  echo "📜 Certificate requested: ${CERT_ARN}"
else
  echo "✅ Existing ACM certificate found: ${CERT_ARN}"
fi

# === VALIDATE CERTIFICATE (AUTOMATICALLY ADD DNS RECORD) ===
echo "🔎 Adding DNS validation record to Route 53..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name \
  --dns-name ${ROOT_DOMAIN} --query "HostedZones[0].Id" --output text | cut -d'/' -f3)

RECORD_JSON=$(aws acm describe-certificate \
  --certificate-arn ${CERT_ARN} \
  --region ${AWS_REGION_US} \
  --query "Certificate.DomainValidationOptions[0].ResourceRecord" \
  --output json)

RECORD_NAME=$(echo "$RECORD_JSON" | jq -r '.Name')
RECORD_VALUE=$(echo "$RECORD_JSON" | jq -r '.Value')

cat > /tmp/route53-validation.json <<EOF
{
  "Comment": "Add domain validation record for ACM",
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${RECORD_NAME}",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "${RECORD_VALUE}"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id ${HOSTED_ZONE_ID} \
  --change-batch file:///tmp/route53-validation.json

echo "⏳ Waiting for ACM certificate validation..."
aws acm wait certificate-validated --certificate-arn ${CERT_ARN} --region ${AWS_REGION_US}
echo "✅ Certificate validated: ${CERT_ARN}"

# === CREATE CLOUDFRONT DISTRIBUTION ===
echo "🌩️ Creating CloudFront distribution..."

CF_CONFIG_FILE="/tmp/cloudfront-distribution.json"
CALLER_REFERENCE=$(date +%s) # Unique reference to prevent replay errors

cat > ${CF_CONFIG_FILE} <<EOF
{
  "Comment": "Jenkins distribution for ${DOMAIN}",
  "CallerReference": "${CALLER_REFERENCE}",
  "Aliases": {
    "Quantity": 1,
    "Items": ["${DOMAIN}"]
  },
  "DefaultRootObject": "",
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "jenkins-origin",
      "DomainName": "${EC2_DNS}",
      "CustomOriginConfig": {
        "HTTPPort": 80,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "http-only"
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "jenkins-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {"Quantity":7, "Items":["GET","HEAD","OPTIONS","PUT","POST","PATCH","DELETE"]},
    "ForwardedValues": {"QueryString":true, "Cookies":{"Forward":"all"}},
    "MinTTL": 0, "DefaultTTL": 0, "MaxTTL": 0
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "${CERT_ARN}",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "Enabled": true
}
EOF

CF_DIST=$(aws cloudfront create-distribution \
  --distribution-config file://${CF_CONFIG_FILE} \
  --query "Distribution.DomainName" --output text)

echo "✅ CloudFront Domain: ${CF_DIST}"

# === CREATE ROUTE 53 RECORD POINTING TO CLOUDFRONT ===
echo "🧭 Creating Route 53 Alias record..."
cat > /tmp/route53-cf.json <<EOF
{
  "Comment": "Route traffic to CloudFront",
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${DOMAIN}",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "${CF_DIST}",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id ${HOSTED_ZONE_ID} \
  --change-batch file:///tmp/route53-cf.json

# === RESTART SERVICES ===
sudo systemctl restart nginx
sudo systemctl restart jenkins || echo "⚠️ Jenkins restart skipped (check if service is installed)"

# === FIREWALL OPTIMIZATION ===
echo "🚫 Locking down direct Jenkins port access..."
sudo firewall-cmd --permanent --add-rich-rule="rule family='ipv4' port port=${JENKINS_PORT} protocol=tcp drop"
sudo firewall-cmd --reload

# === OUTPUT SUMMARY ===
echo "🎉 SETUP COMPLETE!"
echo "🌐 Jenkins is now accessible at: https://${DOMAIN}"
echo "☁️ CloudFront Distribution: ${CF_DIST}"
echo "🔒 SSL: Managed by AWS ACM (auto-renew)"
echo "💰 Cost Optimization: EC2 Free Tier + CloudFront + ACM + Route53"