#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Due to a bug in build tool sometime a network is missing.
"""

import os
import sys
import tempfile
import subprocess
from xml.etree import ElementTree as ET

if len(sys.argv) != 3:
    print("Usage: source.ova dst.ova")
    sys.exit(1)


with tempfile.TemporaryDirectory() as tmp_dir:
    print("Temporary directory: {}".format(tmp_dir))
    subprocess.call(["tar", "-xvzf", sys.argv[1], "-C", tmp_dir])
    tree = ET.parse(os.path.join(tmp_dir, 'GNS3 VM.ovf'))
    root = tree.getroot()

    network_section = root.find("{http://schemas.dmtf.org/ovf/envelope/1}NetworkSection")

    nat_found = False
    hostonly_found = False

    for node in network_section.findall("{http://schemas.dmtf.org/ovf/envelope/1}Network"):
        network_name = node.get("{http://schemas.dmtf.org/ovf/envelope/1}name").lower()
        if network_name == "nat":
            nat_found = True
        elif network_name == "hostonly":
            hostonly_found = True

    if hostonly_found is False:
        network = ET.SubElement(network_section, '{http://schemas.dmtf.org/ovf/envelope/1}Network')
        network.set("{http://schemas.dmtf.org/ovf/envelope/1}name", "hostonly")
        description = ET.SubElement(network, "{http://schemas.dmtf.org/ovf/envelope/1}Description")
        description.text = "The hostonly network"
        print("Fix missing hostonly")

    if nat_found is False:
        network = ET.SubElement(network_section, '{http://schemas.dmtf.org/ovf/envelope/1}Network')
        network.set("{http://schemas.dmtf.org/ovf/envelope/1}name", "nat")
        description = ET.SubElement(network, "{http://schemas.dmtf.org/ovf/envelope/1}Description")
        description.text = "The nat network"
        print("Fix missing nat")

    connection_id = 0
    for item in root.iter('{http://schemas.dmtf.org/ovf/envelope/1}Item'):
        connection = item.find('{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData}Connection')
        if connection is not None:
            if connection_id == 0:
                connection.text = "hostonly"
            elif connection_id == 1:
                connection.text = "nat"
            connection_id += 1

    tree.write(os.path.join(tmp_dir, 'GNS3 VM.ovf'))
    subprocess.call(["ovftool",
                     "--overwrite",
                     "--allowAllExtraConfig",
                     os.path.join(tmp_dir, 'GNS3 VM.ovf'),
                     sys.argv[2]])
