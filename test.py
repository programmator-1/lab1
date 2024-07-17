import pytest
import subprocess
import time
import requests


def setup_module(module):
    module.uvicorn = subprocess.Popen(args=["uvicorn", "--host", "127.0.0.1", "--port", "8888", "lab1:app"])
    time.sleep(3)


def teardown_module(module):
    module.uvicorn.kill()


def test_index():
    r = requests.get('http://localhost:8888/v1')
    assert (r.status_code == 200)
    r = requests.get('http://localhost:8888/v2')
    assert (r.status_code == 200)


def test_get_image_form():
    r = requests.get('http://localhost:8888/v1/image_form')
    assert (r.status_code == 200)
    r = requests.get('http://localhost:8888/v2/image_form')
    assert (r.status_code == 200)


def test_post_image_form():
    r = requests.post('http://localhost:8888/v1/image_form', data={})
    assert (r.status_code == 200)
    r = requests.post('http://localhost:8888/v2/image_form', data={})
    assert (r.status_code == 422)
