# Ansible Network Infrastructure Testing (ANIT)

## Introduction 

This repository is a framework to show how traditional unittesting concepts can be applied to the process of generating network configuration files when using Ansible.  

This testing process allows a user to verify that different data files (YAML) render the proper expected CLI network configurations using the same or different Jinja templates and across different versions of both Python and Ansible.  

In other words, it'll verify your network YAML data (the YAML files), Jinja template(s), Python version, and Ansible version won't break the configuration being built and deployed to network infrastructure.  This comes in to be super handy to test various YAML data structures to ensure your Jinja logic is sound and accounts for both required and optional variables and data.

The project uses `nox`, a Python testing framework.  It's similar to `tox`, but uses a Python-based config file allowing for maximum flexibility.

## Using ANIT

1. Install `nox` in your Python 3.6+ environment.
2. Determine a feature you're testing, e.g BGP, VLANs, interfaces, OSPF
3. Create a sub-directory with the feature name inside the `tests` directory 
4. Create as many sub-directories inside the _feature_ directory equal to the number of tests for that feature, e.g. the number of data files and/or templates needed to test.  The names of these sub-directories could be a descriptive name or something like `test_01`, `test_02` as shown in the repository.
5. Create a Jinja template and place it in the `templates` directory named `{{ feature }}.j2`, e.g. `vlans.j2`.  
6. In each test sub-directory (`test01` as an example), create `data.yml` and `expected_config.cfg`. `data.yml` is a YAML file of the data used in your Jinja template for that feature.  The `expected_config.cfg` is the CLI commands that should get generated from the data and Jinja2 template.  All data files will be rendered with the template in the previous step.  This is based on N data files and 1 Jinja template.  Optionally, you can add a Jinja template per test case in this directory, also called `{{ feature }}.j2`.  This template will take priority over one with the same in the `templates` directory.
7. Edit `noxfile.py` with the versions of Python and Ansible you want to test against.
8. Execute your tests by
  (a) Running `nox` (to test all environments)
  (b) Running `ansible-playbook -i localhost, pb_test_configs.yml` to test in your working environment.

> Note: `nox` requires Python 3.6+ while it can still test Python 2 virtual environments.

For each playbook that runs, it generates a `job-summary.txt` that looks like this:

```
(noxy) ntc@ntc:ansible-build-test$ cat job-summary.txt 
Configuration Build Testing Job Summary
-------------------------------------------------------------

**INFO: FEATURE bgp        TEST: test_01    ---------> PASSED    
**INFO: FEATURE bgp        TEST: test_02    ---------> PASSED    
**INFO: FEATURE vlans      TEST: test_01    ---------> PASSED    
**INFO: FEATURE vlans      TEST: test_02    ---------> FAILED    
--- tests/vlans/test_02/expected_config.cfg
+++ outputs/vlans/test_02/generated_config.cfg
@@ -2,5 +2,5 @@
   name web
 vlan 20
   name app
-vlan 30
+vlan 300
   name db

Summary: 4 data files tested
```

This tells us that the VLANs `test_02` failed.

If we show that actual data (also in the repository), you'd see this:

```
(noxy) ntc@ntc:ansible-build-test$ tree tests/vlans/test_02/
tests/vlans/test_02/
├── data.yml
└── expected_config.cfg

0 directories, 2 files
(noxy) ntc@ntc:ansible-build-test$
```

The bad data:

```
(noxy) ntc@ntc:ansible-build-test$ cat tests/vlans/test_02/data.yml      
---

vlans:
  - id: 10
    name: web
  - id: 20
    name: app
  - id: 300
    name: db
(noxy) ntc@ntc:ansible-build-test$
```

The expected config:

```
(noxy) ntc@ntc:ansible-build-test$ cat tests/vlans/test_02/expected_config.cfg 
vlan 10
  name web
vlan 20
  name app
vlan 30
  name db
(noxy) ntc@ntc:ansible-build-test$ 
```

The template being used to generate the config and compared against the expected config:

```
(noxy) ntc@ntc:ansible-build-test$ cat templates/vlans.j2 
{% for vlan in vlans %}
vlan {{ vlan['id'] }}
  name {{ vlan['name'] }}
{% endfor %}
(noxy) ntc@ntc:ansible-build-test$ 
```

