#!/bin/bash -xe
apt-get install s3cmd -y
wget https://packages.chef.io/stable/ubuntu/10.04/chef_12.9.38-1_amd64.deb
dpkg -i chef_12.9.38-1_amd64.deb

mkdir -p /etc/chef
(
cat << EOF
[default]
access_key = %(access_key)s
gpg_command = /usr/bin/gpg
gpg_passphrase = %(gpg_passphrase)s
secret_key = %(secret_key)s
use_https = True
EOF
) > /home/ubuntu/.s3cfg
(
cat << EOF
log_level :info
log_location STDOUT
chef_server_url 'https://chef.trimastone.com/organizations/trimastone'
validation_client_name 'trimastone-validator'
environment '%(env)s'
EOF
) > /etc/chef/client.rb
(
cat << EOF
{"run_list": ["role[database_server]"]}
EOF
) > /etc/chef/first-boot.json
(
cat << EOF
%(encrypted_data_bag_secret)s
EOF
) > /etc/chef/encrypted_data_bag_secret

s3cmd --skip-existing -c /home/ubuntu/.s3cfg get s3://trimastone/trimastone-validator.pem /etc/chef/validation.pem
knife ssl fetch -c /etc/chef/client.rb
chef-client -j /etc/chef/first-boot.json
