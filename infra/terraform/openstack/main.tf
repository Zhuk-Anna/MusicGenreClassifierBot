data "openstack_images_image_v2" "ubuntu" {
    name = var.image_name
}

resource "openstack_compute_instance_v2" "AZ_server" {
    name        = "AZ-music-app-server-lab5"
    flavor_name = var.flavor_name
    key_pair    = var.key_pair

    security_groups = ["default", "students-general"]

    network {
        name = var.network_name
    }

    # Boot from Volume
    block_device {
        uuid                  = data.openstack_images_image_v2.ubuntu.id
        source_type           = "image"
        volume_size           = var.volume_size
        destination_type      = "volume"
        boot_index            = 0
        delete_on_termination = true
    }
}