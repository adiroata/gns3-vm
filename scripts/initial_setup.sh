#
# Update script called at VM first launch
#

set -e

curl "https://raw.githubusercontent.com/GNS3/gns3-vm/master/scripts/welcome.py" > /tmp/gns3welcome.py
sudo mv "/tmp/gns3welcome.py" "/usr/local/bin/gns3welcome.py"
sudo chmod 755 "/usr/local/bin/gns3welcome.py"

pip3 install --ignore-installed --pre gns3-server

echo -n "testing" > /home/gns3/.config/gns3/gns3_release

echo "Reboot in 5s"
sleep 5

sudo reboot

