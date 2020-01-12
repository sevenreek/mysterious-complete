if [ "$(id -u)" != 0 ]; then
  echo 'Blad! Uruchom skrypt z sudo: sudo bash rpi_configure.bash.'
  exit 1
fi
echo '>>> Sprawdzam polaczenie z internetem...'
if ping -q -c 1 -W 1 8.8.8.8 >/dev/null; then
  echo "OK"
else
  echo "Blad! Brak polaczenia z internetem"
  exit 1
fi
echo '>>> Aktualizuje system...'
sudo apt -y upgrade
sudo apt -y update
sudo apt -y clean
echo '>>> Instaluje pulpit zdalny...'
sudo apt -y install xrdp
echo '>>> Uruchamiam SSH...'
sudo systemctl enable ssh
sudo systemctl start ssh
echo '>>> Uruchamiam I2C...'
if grep -q 'i2c-bcm2708' /etc/modules; then
  echo 'i2c-bcm2708 module already exists, skip this step.'
else
  echo 'i2c-bcm2708' >> /etc/modules
fi
if grep -q 'i2c-dev' /etc/modules; then
  echo 'i2c-dev module already exists, skip this step.'
else
  echo 'i2c-dev' >> /etc/modules
fi
if grep -q 'dtparam=i2c1=on' /boot/config.txt; then
  echo 'i2c1 parameter already set, skip this step.'
else
  echo 'dtparam=i2c1=on' >> /boot/config.txt
fi
if grep -q 'dtparam=i2c_arm=on' /boot/config.txt; then
  echo 'i2c_arm parameter already set, skip this step.'
else
  echo 'dtparam=i2c_arm=on' >> /boot/config.txt
fi
if [ -f /etc/modprobe.d/raspi-blacklist.conf ]; then
  sed -i 's/^blacklist spi-bcm2708/#blacklist spi-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
  sed -i 's/^blacklist i2c-bcm2708/#blacklist i2c-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
else
  echo 'raspi-blacklist.conf does not exist, skip this step.'
fi
sudo apt install -y i2c-tools
echo '>>> Instaluje bilbioteki python...'
sudo pip3 install --upgrade pip
sudo pip3 install bottle
sudo pip3 install adafruit-blinka --ignore-installed
sudo pip3 install adafruit-circuitpython-ht16k33 --ignore-installed
sudo pip3 install python-vlc

read -p "Konfiguracja zakonczona. Uruchomic ponownie? [y/n]" -n 1 -r
echo    
if [[ $REPLY =~ ^[Yy]$ ]]
then
   sudo reboot
fi