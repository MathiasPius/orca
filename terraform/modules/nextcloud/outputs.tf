output "ip" {
    value = "${digitalocean_droplet.nextcloud.ipv4_address}"
}