jack_control start

cd /home/orangepi/Downloads/RTPMIROIR/

git config pull.rebase true
git pull

hostname -I | sudo tee /home/orangepi/Downloads/ip.txt

source bin/activate

pip3 install -r requirements.txt

python3 scriptmidi.py