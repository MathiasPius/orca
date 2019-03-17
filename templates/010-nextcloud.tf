# Variables: INSTANCEID

module "nextcloud" {
    source = "../../terraform/modules/nextcloud"
    instance_id = "{{INSTANCEID}}",
    ssh_fingerprint = "${digitalocean_ssh_key.ssh_key.id}"
}

output "ipv4" {
    value = "${module.nextcloud.ipv4}"
}

output "ssh_key" {
    value = "${path.root}/instances/{{INSTANCEID}}/id_ed25519"
}