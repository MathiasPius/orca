variable do_token {
    description = "DigitalOcean API Token"
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