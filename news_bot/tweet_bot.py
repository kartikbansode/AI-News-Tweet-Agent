import os
import subprocess

def post_tweet(text):
    cmd = f'echo "{text}" | twitter tweet create'
    subprocess.run(cmd, shell=True, check=True)
