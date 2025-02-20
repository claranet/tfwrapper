import sshtunnel
import os

LOG_FORMAT = "{log_color}{levelname: <7}{reset} {purple}tfwrapper{reset} : {bold}{message}{reset}"

class Tunnels:
    def __init__(self, tunnels, logger):
        self.logger = logger
        self.opened_tunnels = []

        for tunnel_name in tunnels.keys():
            sshtunnel.DEFAULT_LOGLEVEL = 0
            server = sshtunnel.SSHTunnelForwarder(
                tunnels[tunnel_name]["gateway_host"],
                ssh_username=tunnels[tunnel_name]["gateway_login"],
                ssh_pkey=os.path.expanduser(tunnels[tunnel_name]["gateway_private_key"]),
                remote_bind_address=(tunnels[tunnel_name]["remote_host"], tunnels[tunnel_name]["remote_port"]),
                local_bind_address=('127.0.0.1', tunnels[tunnel_name]["local_port"])
            )
            self.logger.info(f'Starting tunnel : {tunnels[tunnel_name]}')
            server.start()
            self.opened_tunnels.append(server)

    def stop_all(self):
        for tunnel in self.opened_tunnels:
            tunnel.stop()