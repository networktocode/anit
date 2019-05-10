import nox

PYTHON = ["2.7", "3.6"]
ANSIBLE = ["2.6.4", "2.7.1", "2.7.10"]
RE_USE_VENV = True


@nox.session(python=PYTHON, reuse_venv=RE_USE_VENV)
@nox.parametrize("ansible", ANSIBLE)
def test_configuration_data(session, ansible):
    """Testing Ansible YAML data with network configuration templates
    """
    py_version = session.python
    session.install("ansible=={}".format(ansible))
    session.run("ansible-playbook", "-i", "localhost,", "pb_test_configs.yml")
    session.run("cat", "job-summary.txt", external=True)
