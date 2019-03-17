# Orca.
```
Usage:
  orca instances deduce     attempt to deduce active instances based on subfolders
                            in instances/, optionally updates terraform/instances.tf 
                            to reflect this.

  orca instances export     uses terraform output to retrieve real addresses for 
                            already-provisioned instances and writes them to
                            ansible/hosts

  orca provision            runs terraform init and terraform apply to bring real
                            world into compliance with terraform configuration

  orca provision new [--name=NAME] [--storage=SIZE] [--drop=DROP] [--image=IMAGE]
                            interactively generates ssh keys and terraform config
                            for new NextCloud Instance

  orca initialize [--rerun] [--trust=NETWORK]...
                            initializes a newly provisioned instance using the 
                            "managed" role, which installs an orca user and performs
                            basic Ubuntu hardening like firewall rules and disabling
                            root login.

  orca configure            configures all instances using the "nextcloud" ansible role

Options:
  -h --help         show this screen.
  --version         show version.

  --name=NAME       name of the new instance.
                    must ONLY contain letters, digits and underscores.
                    must NOT be longer than 32 characters

  --storage=SIZE    size of the attached nextcloud volume in GB. [default: 10]
                    must be between 1-3000GB

  --drop=DROP       Digital Ocean droplet size to use. [default: s-1vcpu-1gb]

  --image=IMAGE     which Digital Ocean image to use. [default: ubuntu-18-04-x64]
                    only tested with ubuntu-18-04-x64 but others may work too


  --rerun           reinitialize using 'orca' user.
                    this effectively enforces compliance with the 'managed' role,
                    but using the configured orca user, since root login is disabled
                    after the first initialization.

  --trust=NETWORK   source networks to trust for ssh connections. [default: any]
                    these arguments are used when configuring ufw on the endpoint.
                    can be used multiple times to specify more networks or addresses
                    e.g. --trust=192.168.0.25 --trust=10.0.0.0/8
```