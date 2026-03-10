variable "image_name" {
    type = string
    default = "ununtu-22.04" # bug in openstack 'ubuntu-22.04'
}

variable "flavor_name" {
    type = string
    default = "m1.small"
}

variable "network_name" {
    type = string
    default = "sutdents-net" # bug in openstack 'students-net'
}

variable "key_pair" {
    type = string
    default = "AnnaZ"
}

variable "volume_size"{
    type = number
    default = 10
}