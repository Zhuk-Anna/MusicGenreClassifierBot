output "server_ip" {
  value = openstack_compute_instance_v2.AZ_server.network[0].fixed_ip_v4
  # value = [for i in openstack_compute_instance_v2.AZ_server : i.network[0].fixed_ip_v4]
}