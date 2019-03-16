variable "instance_id" { }

variable "region" {
    default = "fra1"
}
variable "vmtype" {
    default = "s-1vcpu-1gb"
}

variable "image" {
    default = "ubuntu-18-04-x64"
}

variable "storage" {
    default = 10
}

variable "ssh_fingerprint" {
    type = "string"
}