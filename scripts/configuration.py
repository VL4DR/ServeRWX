import dataclasses
import yaml

@dataclasses.dataclass(frozen=True)
class ServerConfigData():
    """
    All fields which are relevant to the server configuration.
    """
    server_magic : int
    server_max_data_size : int
    server_shellcode_buffer_size : int
    allocate_shellcode_buffer : bool
    server_big_endian : bool


class ServerConfig:
    """
    A wrapper for the server configuration that parses the output configuration
    from the build process and transforms it to a python-friendly configuration.
    """
    def __init__(self, config_path : str):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        self._server_config_data = ServerConfig._parse_config(config_data)


    @staticmethod
    def _parse_config(config_data : dict) -> ServerConfigData:
        for elem in ['server_magic', 'server_max_data_size', 'server_shellcode_buffer_size',
                     'allocate_shellcode_buffer', 'server_big_endian']:
            if not elem in config_data:
                raise KeyError(f"Missing key {elem} in the supplied config data!")

        server_magic = int(config_data['server_magic'], 0)
        server_max_data_size = int(config_data['server_max_data_size'], 0)
        server_shellcode_buffer_size = int(
            config_data['server_shellcode_buffer_size'], 0)
        allocate_shellcode_buffer = config_data['allocate_shellcode_buffer'] == 'ON'
        server_big_endian = config_data['server_big_endian'] == 'ON'

        server_config = ServerConfigData(server_magic,
                                         server_max_data_size,
                                         server_shellcode_buffer_size,
                                         allocate_shellcode_buffer,
                                         server_big_endian)

        return server_config

    @property
    def server_config_data(self):
        """
        A property that holds the entire server configuration
        """
        return self._server_config_data
