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

        self.enable = {"id": "14.0@i", "name": "Enable", type: "integer", "value": 0}

        self.destination_ip = {
            "id": "15.0@s",
            "name": "Destination IP Address",
            type: "string",
            "value": kwargs["destination_ip"],
        }

        self.udp_port = {
            "id": "16.0@i",
            "name": "UDP Port",
            type: "integer",
            "value": kwargs["udp_port"],
        }

        self.physical_port = {
            "id": "13.0@i",
            "name": "Physical Port",
            type: "integer",
            "value": kwargs["physical_port"],
        }

        self.level = {
            "id": "17.0@i",
            "name": "Level",
            type: "integer",
            "value": severity[kwargs["severity"]],
        }

        if "magnum" in kwargs.keys():

            collector = magnum_cache(**kwargs["magnum"])

            self.ip_list = collector.catalog_cache()

            print(self.ip_list)


def main():

    params = {
        "magnum": {
            "host": "10.10.232.25",
            "nature": "mag-1",
            "cluster_ip": "10.10.232.16",
            "edge_matches": ["3067VIP10G-3G"],
        },
        "destination_ip": "127.0.0.1",
        "udp_port": 514,
        "physical_port": 1,
        "severity": "Warning",
    }

    edge_setter = edge(**params)


if __name__ == "__main__":
    main()
