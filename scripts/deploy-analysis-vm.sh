PW="<PASSWORD>"
LOCATION="WESTEUROPE"
SA="geotdiag"
RG="geotvm"

az group create --name $RG --location $LOCATION

az storage account create --name $SA --resource-group $RG --location $LOCATION

az vm create \
	-n geot \
	-g geotvm \
	--boot-diagnostics-storage $SA \
	--image UbuntuLTS \
	-l $LOCATION \
	--size "Standard_D16as_v4" \
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
sudo mkdir ~/data
sudo mount /dev/sdc1 ~/data

sudo blkid
/dev/sdc1: UUID="4901ab8f-a78e-48fa-87c9-2304b6e21bcf" TYPE="xfs" PARTLABEL="xfspart" PARTUUID="1ae24f49-a7cf-4bcc-99d3-29f7cc8b856a"

sudo vim /etc/fstab
UUID=4901ab8f-a78e-48fa-87c9-2304b6e21bcf   /home/geot/data   xfs   defaults,nofail   1   2