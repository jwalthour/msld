
# Software setup notes

TODO: this needs a lot of details added

* Installed python3 and uninstalled python2 prior to installing the rpi module
* These commands were used to install python3 and the rgb-led-matrix library:
````bash
sudo rm /usr/bin/python
sudo ln -s /usr/bin/python3 /usr/bin/python
ls -l /usr/bin/python*
python --version
sudo update-alternatives --install $(which python) python $(readlink -f $(which python3)) 3
sudo apt remove python2.7*
sudo apt install python3
sudo apt install python3-dev
sudo apt autoremove
ls -l /usr/bin/python*
sudo ln -s /usr/bin/python3 /usr/bin/python
# cd to rpi-rgb-led-matrix
make build-python
sudo make install-python
sudo apt install python3-pil
````

* I have some extra partitions in my Pi setup to make it easier to configure things from a Windows PC:

````bash
msld@msld:/mnt/source/msld $ lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
mmcblk0     179:0    0 59.5G  0 disk
├─mmcblk0p1 179:1    0  256M  0 part /boot
├─mmcblk0p2 179:2    0   37G  0 part /
├─mmcblk0p3 179:3    0  954M  0 part /mnt/config
└─mmcblk0p4 179:4    0 19.6G  0 part /mnt/source
msld@msld:/mnt/source/msld $ blkid
/dev/mmcblk0p1: LABEL_FATBOOT="boot" LABEL="boot" UUID="5DE4-665C" TYPE="vfat" PARTUUID="9730496b-01"
/dev/mmcblk0p2: LABEL="rootfs" UUID="7295bbc3-bbc2-4267-9fa0-099e10ef5bf0" TYPE="ext4" PARTUUID="9730496b-02"
/dev/mmcblk0p3: LABEL_FATBOOT="CONFIG" LABEL="CONFIG" UUID="8A10-B881" TYPE="vfat" PARTUUID="9730496b-03"
/dev/mmcblk0p4: UUID="b2668c6f-837f-40c7-9606-1532f0bb9e86" TYPE="ext4" PARTUUID="9730496b-04"
msld@msld:/mnt/source/msld $ cat /etc/fstab
proc            /proc           proc    defaults          0       0
PARTUUID=9730496b-01  /boot           vfat    defaults          0       2
PARTUUID=9730496b-02  /               ext4    defaults,noatime  0       1
# a swapfile is not a swap partition, no line here
#   use  dphys-swapfile swap[on|off]  for that
UUID=8A10-B881  /mnt/config     vfat    rw,user 0       2
UUID=b2668c6f-837f-40c7-9606-1532f0bb9e86       /mnt/source     ext4    rw,user,exec    0       2
msld@msld:/mnt/source/msld $ mount
/dev/mmcblk0p2 on / type ext4 (rw,noatime)
...
/dev/mmcblk0p3 on /mnt/config type vfat (rw,nosuid,nodev,noexec,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro,user)
/dev/mmcblk0p4 on /mnt/source type ext4 (rw,nosuid,nodev,relatime,user)
/dev/mmcblk0p1 on /boot type vfat (rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro)
tmpfs on /run/user/1001 type tmpfs (rw,nosuid,nodev,relatime,size=191132k,mode=700,uid=1001,gid=1001)


````

### Prerequisites
````bash
sudo pip3 install pytz tzlocal requests
````