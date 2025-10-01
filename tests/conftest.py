def pytest_addoption(parser):
    parser.addoption("--server_binary_path", action="store", required=True)
    parser.addoption("--arch", action="store", required=True)
    