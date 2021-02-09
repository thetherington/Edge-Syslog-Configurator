import json

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()


class magnum_cache:
    def __init__(self, **kwargs):

        self.nature = "mag-1"
        self.cluster_ip = None
        self.edge_matches = []

        for key, value in kwargs.items():

            if ("host" in key) and value:
                self.host = value

            if ("nature" in key) and value:
                self.nature = value

            if ("cluster_ip" in key) and value:
                self.cluster_ip = value

            if ("edge_matches" in key) and value:
                self.edge_matches.extend(value)

        self.cache_url = "http://{}/proxy/insite/{}/api/-/model/magnum/{}".format(
            self.host, self.nature, self.cluster_ip
        )

    def cache_fetch(self):

        response = requests.get(self.cache_url, verify=False, timeout=15.0)

        return json.loads(response.text)

    def catalog_cache(self):

        cache = self.cache_fetch()

        if cache:

            ipg_ip_db = []

            for device in cache["magnum"]["magnum-controlled-devices"]:

                if device["device"] in self.edge_matches:

                    ipg_ip_db.append(device["control-1-address"]["host"])

                    if device["device"] in ["EXE", "IPX"]:
                        ipg_ip_db.append(device["control-2-address"]["host"])

            return ipg_ip_db


class edge:
    def __init__(self, **kwargs):

        severity = {
            "Emergency": 0,
            "Alert": 1,
            "Critical": 2,
            "Error": 3,
            "Warning": 4,
            "Notice": 5,
            "Informational": 6,
            "Debug": 7,
        }

        self.enable = {"id": "14.0@i", "name": "Enable", "type": "integer", "value": 1}

        self.destination_ip = {
            "id": "15.0@s",
            "name": "Destination IP Address",
            "type": "string",
            "value": kwargs["destination_ip"],
        }

        self.udp_port = {
            "id": "16.0@i",
            "name": "UDP Port",
            "type": "integer",
            "value": kwargs["udp_port"],
        }

        self.physical_port = {
            "id": "13.0@i",
            "name": "Physical Port",
            "type": "integer",
            "value": kwargs["physical_port"],
        }

        self.level = {
            "id": "17.0@i",
            "name": "Level",
            "type": "integer",
            "value": severity[kwargs["severity"]],
        }

        self.parameters = [
            self.enable,
            self.destination_ip,
            self.udp_port,
            self.physical_port,
            self.level,
        ]

        if "magnum" in kwargs.keys():

            collector = magnum_cache(**kwargs["magnum"])

            self.ip_list = collector.catalog_cache()

        self.proto = kwargs["proto"]

    def fetch(self, address, parameters):

        try:

            with requests.Session() as session:

                ## get the session ID from accessing the login.php site
                resp = session.get(
                    "%s://%s/login.php" % (self.proto, address), verify=False, timeout=30.0,
                )

                sessionID = resp.headers["Set-Cookie"].split(";")[0]

                payload = {
                    "jsonrpc": "2.0",
                    "method": "set",
                    "params": {"parameters": parameters},
                    "id": 1,
                }

                url = "%s://%s/cgi-bin/cfgjsonrpc" % (self.proto, address)

                headers = {
                    "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Cookie": sessionID + "; webeasy-loggedin=true",
                }

                response = session.post(
                    url, headers=headers, data=json.dumps(payload), verify=False, timeout=30.0,
                )

                return json.loads(response.text)

        except Exception as error:
            print(error)
            return error


def main():

    params = {
        "magnum": {
            "host": "192.168.42.91",
            "nature": "mag-1",
            "cluster_ip": "192.168.0.250",
            "edge_matches": ["570J2K"],
        },
        "destination_ip": "192.168.42.91",
        "udp_port": 514,
        "physical_port": 2,
        "severity": "Warning",
        "proto": "http",
    }

    edge_setter = edge(**params)

    print(edge_setter.ip_list)

    for ip in edge_setter.ip_list:

        print(ip, edge_setter.fetch(ip, edge_setter.parameters))


if __name__ == "__main__":
    main()
