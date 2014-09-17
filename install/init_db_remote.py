import subprocess

command = 'psql -h archpgbase -U cloud_admin -d cloud_admin -f init_cloud.sql'

subprocess.call(command, shell=True)
