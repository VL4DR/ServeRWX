def pytest_addoption(parser):
    parser.addoption("--server_binary_path", action="store")
    parser.addoption("--arch", action="store")
    