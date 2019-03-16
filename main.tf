variable do_token {
    description = "DigitalOcean API Token"
}

resource "digitalocean_tag" "orcatag" {
  name = "orca"
}

provider "digitalocean" {
  token = "${var.do_token}"
}

module "terraform" {
  source = "./terraform/"
}

output "hosts" {
  value = "${module.terraform.hosts}"
}