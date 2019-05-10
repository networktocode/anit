# Ansible Network Infrastructure Testing (ANIT)

## Introduction 

ANIT is a framework to show how traditional unittesting concepts can be applied to the process of generating Cisco network configuration files when using Ansible.  All examples provided focus on having a robust templating framework for Cisco device management.  

Not only will this testing approach allow a user to verify that different data files (YAML) render the proper expected CLI network configurations using the same or different Jinja templates, **it will do so across different versions of both Python and Ansible**.  

In other words, it'll verify your network YAML data (the YAML files), Jinja template(s), Python version, and Ansible version won't break the configuration being built and deployed to network infrastructure.  This comes in to be super handy to test various YAML data structures to ensure your Jinja logic is sound and accounts for both required and optional variables in the data.

The project uses `nox`, a Python testing framework.  It's similar to `tox`, but uses a Python-based config file allowing for maximum flexibility.  You would trigger `nox` via Jenkins or Travis if you choose to use this framework.

## Using ANIT

1. Install `nox` in your Python 3.6+ environment.
2. Determine a feature you're testing, e.g BGP, VLANs, interfaces, OSPF
3. Create a sub-directory with the feature name inside the `tests` directory 
4. Create test cases: create as many sub-directories inside the _feature_ directory equal to the number of tests for that feature, e.g. the number of data files and/or templates needed to test.  The names of these sub-directories could be a descriptive name or something like `test_01`, `test_02` as shown in the repository.
5. Create a Jinja template and at a minimum, place it in the `templates` directory named `{{ feature }}.j2`, e.g. `vlans.j2`.  _More on the template directory structure below._
6. In each test sub-directory (`test01` as an example), create `data.yml` and `expected_config.cfg`. `data.yml` is a YAML file of the data used in your Jinja template for that feature.  It must also include a `meta` key that includes `os` and `vendor` attributes.  The `expected_config.cfg` is the CLI commands that should get generated from the data and Jinja2 template.  All data files will be rendered with the template in the previous step.  This is based on N data files and 1 Jinja template.  Optionally, you can add a Jinja template per test case in this directory, also called `{{ feature }}.j2`.  This template will take priority over one with the same in the `templates` directory.
7. Edit `noxfile.py` with the versions of Python and Ansible you want to test against.
8. Execute your tests by

  (a) Running `nox` (to test all environments)
  
  (b) Running `ansible-playbook -i localhost, pb_test_configs.yml` to test in your working environment.


If you run the playbook locally, you can just view the `job-summary.txt` generated.  However, since `nox` uses Python venv's, we also write all job summaries to `/tmp/ntc`.  You'll see files like this get generated: `2019-05-10-16-18-24-ansible2.6.4-python-job-summary.txt`.  It will be a file per test permutation.  So, if you're testing 3 versions of Python and 3 versions of Ansible, you'll have 9 tests executed and 9 test reports generated.


> Note: `nox` requires Python 3.6+ while it can still test Python 2 virtual environments.

For each playbook that runs, it generates a `job-summary.txt` that looks like this:

```
(noxy) ntc@ntc:ansible-build-test$ cat job-summary.txt 
Configuration Build Testing Job Summary
   -> Ansible Version: 2.6.4
   -> Python Version: python
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
**INFO: FEATURE vlans      TEST: test_03    ---------> FAILED    
AnsibleUndefinedVariable: 'dict object' has no attribute 'name'

Summary: 5 data files tested
```

This tells us that the VLANs `test_02` and `test_03` failed.

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

meta:
  os: ios
  vendor: cisco

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

The results from `test_02`, which is shown in the job summary:

```
(noxy) ntc@ntc:ansible-build-test $ cat outputs/vlans/test_02/test_results.cfg  
--- tests/vlans/test_02/expected_config.cfg
+++ outputs/vlans/test_02/generated_config.cfg
@@ -2,5 +2,5 @@
   name web
 vlan 20
   name app
-vlan 30
+vlan 300
   name db
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


`test02` is showing bad data while `test03` is showing the output when there is a bad template.


### Creating Templates 

In Step 6 above, it stated you must at a **minimum** store a feature template in `templates`.  However, this test framework is much more robust because in production, you definitely will not have a single templates directory.

Here is an example `tree` output from the directory structure:

```
(noxy) ntc@ntc:ansible-build-test (master)$ tree templates/
templates/
├── cisco
│   ├── defaults
│   │   ├── bgp.j2
│   │   └── vlans.j2
│   ├── ios
│   │   ├── catalyst
│   │   │   └── 6500
│   │   │       ├── 6509
│   │   │       └── defaults
│   │   └── defaults
│   └── nxos
│       └── nexus
│           ├── 7000
│           │   └── defaults
│           │       └── vdc.j2
│           ├── 9000
│           │   ├── 9396
│           │   └── defaults
│           └── defaults
└── report.j2

16 directories, 4 files
```

Given Cisco has many OS types, product families, and hardware/software models, you wouldn't want to have duplicate templates and ideally have complex templates.  One approach as shown here is to have a well-designed template directory structure that offers as much flexibility as possible.

This structure and project will search for templates (in priority order):

1. Template Specific to the test case
2. Model Templates
2. Family Templates
3. Platform Templates
4. OS Templates 
5. Cisco (or Vendor) Templates 
6. Generic template found in the `templates` directory

This can be seen more clearly with the specific task in the tasks file:

```yaml
  - name: "{{ feature | upper }}: {{ test_name | upper }}-> GENERATE {{ feature | upper }} CONFIG"
    template:
      src: "{{ template }}"
      dest: ./{{ test_path }}/generated_config.cfg
    with_first_found:
      - "{{ test_dir }}/{{ feature }}/{{ test_name }}/{{ feature }}.j2"
      - "templates/{{ meta['vendor'] }}/{{ meta['os'] }}/{{ platform }}/{{ family }}/{{ model }}/{{ feature }}.j2"
      - "templates/{{ meta['vendor'] }}/{{ meta['os'] }}/{{ platform }}/{{ family }}/defaults/{{ feature }}.j2"
      - "templates/{{ meta['vendor'] }}/{{ meta['os'] }}/{{ platform }}/defaults/{{ feature }}.j2"
      - "templates/{{ meta['vendor'] }}/{{ meta['os'] }}/defaults/{{ feature }}.j2"
      - "templates/{{ meta['vendor'] }}/defaults/{{ feature }}.j2"
      - "{{ feature }}.j2"
    loop_control:
      loop_var: template
    ignore_errors: true
    register: template_status
```


## TODO

* Explore the use of `testinfra` and `pytest-ansible`.


