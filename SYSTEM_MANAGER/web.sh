#!/bin/bash
dnf install httpd -y
systemctl enable httpd --now
echo “<h1>This is the webpage 8080 port </h1>” >> /var/www/html/index.html
echo “<h2>The region is ap-south-1a/1b/1c </h2>” >> /var/www/html/index.html