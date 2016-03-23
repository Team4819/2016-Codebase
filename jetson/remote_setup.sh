chmod +x start_server.sh
chmod +x start_server_root.sh
chmod +x system_prep.sh

export PATH=/usr/local/cuda-6.5/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LD_LIBRARY_PATH=/usr/local/cuda-6.5/lib:/home/ubuntu/freenect2/lib:/libfreenect2/depends/libusb/lib/:
export LIBRARY_PATH=/home/ubuntu/freenect2/lib:
export C_INCLUDE_PATH=/home/ubuntu/freenect2/include:
export CPLUS_INCLUDE_PATH=/home/ubuntu/freenect2/include:

rm -r kinect_streamer/build || true
mkdir kinect_streamer/build
cd kinect_streamer/build
cmake -Dfreenect2_DIR=$HOME/freenect2/lib/cmake/freenect2 ..
make

#sudo mv /home/ubuntu/rc.local /etc/rc.local
#sudo chown root /etc/rc.local
#sudo chmod +x /etc/rc.local