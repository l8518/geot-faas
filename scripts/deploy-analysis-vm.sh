
az group create --name $RG --location $LOCATION

az storage account create --name $SA --resource-group $RG --location $LOCATION

az vm create \
	-n geot \
	-g geotvm \
	--boot-diagnostics-storage $SA \
	--image "Canonical:0001-com-ubuntu-server-focal:20_04-lts:latest" \
	-l $LOCATION \
	--size "Standard_B20ms" \
	--admin-username "geot" \
	--admin-password $PW \
	--authentication-type password \
	--public-ip-sku Standard
	
az vm disk attach \
   -g $RG \
   --vm-name geot \
   --name geotdatadisk \
   --new \
   --size-gb 40

az network public-ip update --dns-name geot -g $RG -n geotPublicIP


ssh geot@geot.westeurope.cloudapp.azure.com


// attach disk
lsblk -o NAME,HCTL,SIZE,MOUNTPOINT | grep -i "sd"

// format:
sudo parted /dev/sdc --script mklabel gpt mkpart xfspart xfs 0% 100%
sudo mkfs.xfs /dev/sdc1
sudo partprobe /dev/sdc1


// attach disk always
sudo mount /dev/sdc1 /mnt
sudo cp -rp /home/geot/. /mnt/
sudo umount /dev/sdc1

sudo blkid
/dev/sdc1: UUID="4901ab8f-a78e-48fa-87c9-2304b6e21bcf" TYPE="xfs" PARTLABEL="xfspart" PARTUUID="1ae24f49-a7cf-4bcc-99d3-29f7cc8b856a"

sudo vim /etc/fstab
UUID=010855f2-d92c-4feb-a482-0c504e8f3e04   /home/geot/   xfs   defaults,nofail   1   2
sudo reboot

git clone https://github.com/l8518/geot-faas.git
cd geot-faas
sudo apt update
sudo apt install python3-pip -y
pip3 install -r requirements.txt

cp scripts/jupyterasservice/jupyter_notebook_config.py ~/jupyter_notebook_config.py
sudo cp scripts/jupyterasservice/jupyter.service /etc/systemd/system/jupyter.service
sudo systemctl daemon-reload
sudo systemctl enable jupyter
sudo service jupyter start
sudo service jupyter status

# Setup NSGs
az network nsg rule create --name allow-jupyter --nsg-name geotNSG --resource-group $RG --access Allow --source-port-ranges '*' --destination-port-ranges 8888 --priority 100
az network nsg rule update --name default-allow-ssh --nsg-name geotNSG --resource-group $RG --access Deny
