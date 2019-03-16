resource "digitalocean_tag" "orcatag" {
  name = "orca"
}

resource "digitalocean_tag" "tag" {
    name = "${var.instance_id}"
}

resource "digitalocean_volume" "volume" {
    region                  = "${var.region}"
    name                    = "${var.instance_id}-nc-vol"
    size                    = "${var.storage}"
    initial_filesystem_type = "ext4"
    description             = "NextCloud Volume belonging to ${var.instance_id}"
}

resource "digitalocean_droplet" "nextcloud" {
    name                = "${var.instance_id}-nc"
    image               = "${var.image}"
    region              = "${var.region}"
    size                = "${var.vmtype}"
    private_networking  = true
    ipv6                = true
    tags                = ["${digitalocean_tag.tag.id}", "${digitalocean_tag.orcatag.id}"]
    volume_ids          = ["${digitalocean_volume.volume.id}"]
    ssh_keys            = ["${var.ssh_fingerprint}"]
}

output "ipv4" {
    value = "${digitalocean_droplet.nextcloud.ipv4_address}"
}

output "ipv6" {
    value = "${digitalocean_droplet.nextcloud.ipv6_address}"
}