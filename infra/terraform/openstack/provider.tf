# Define required providers
terraform {
    required_version = ">= 0.14.0"
    required_providers {
        openstack = {
            source  = "terraform-provider-openstack/openstack"
            version = "~> 1.53"
        }
    }
}

# Configure the OpenStack Provider
provider "openstack" {}

# provider "openstack" {
#     user_name   = "master2025"
#     tenant_name = "students"
#     password    = ""
#     auth_url    = "https://cloud.crplab.ru:5000/v3"
#     region      = "RegionOne"
# }