export PATH=/usr/local/cuda-6.5/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LD_LIBRARY_PATH=/usr/local/cuda-6.5/lib:/home/ubuntu/freenect2/lib:
export LIBRARY_PATH=/home/ubuntu/freenect2/lib:
export C_INCLUDE_PATH=/home/ubuntu/freenect2/include:
export CPLUS_INCLUDE_PATH=/home/ubuntu/freenect2/include:

python3 /home/ubuntu/dashboard/jetson_dashboard.py &
n=0
until [ $n -ge 5 ]
do
   /home/ubuntu/kinect_streamer/build/kinect_streamer && break
   n=$[$n+1]
   sleep 5
done