gst-launch-1.0 --eos-on-shutdown -v \
    filesrc location="stream_fifo" do-timestamp=true \
    ! videoparse format="GST_VIDEO_FORMAT_BGR" width="1920" height="1080" framerate="10/1"\
    ! videoconvert \
    ! "video/x-raw, format=(string)I420, width=(int)1920,\
      height=(int)1080" \
    ! xvimagesink sync=false