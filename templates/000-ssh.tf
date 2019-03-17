# Variables: INSTANCEID

resource "digitalocean_ssh_key" "ssh_key" {
    name       = "{{INSTANCEID}}-ed25519"
    public_key = "${file("${path.module}/id_ed25519.pub")}"
}