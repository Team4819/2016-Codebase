sshpass -p 'ubuntu' scp -r jetson/* ubuntu@10.48.19.6:~/
sshpass -p 'ubuntu' scp -r vision/kinect_streamer ubuntu@10.48.19.6:~/
sshpass -p 'ubuntu' scp -r dashboard ubuntu@10.48.19.6:~/
sshpass -p 'ubuntu' ssh -t ubuntu@10.48.19.6 'chmod +x ~/remote_setup.sh && ./remote_setup.sh'
