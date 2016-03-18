
#include <libfreenect2/libfreenect2.hpp>
#include <libfreenect2/frame_listener_impl.h>
#include <libfreenect2/registration.h>
#include <libfreenect2/packet_pipeline.h>
#include <libfreenect2/logger.h>
#include <opencv/cv.hpp>
#include <iostream>
#include <fstream>
using namespace std;

libfreenect2::Freenect2 freenect2;
libfreenect2::Freenect2Device *dev = 0;
libfreenect2::PacketPipeline *pipeline = 0;

int main(int argc, char** argv){
    ofstream fifo;
    fifo.open(argv[1]);
    if(freenect2.enumerateDevices() == 0)
    {
      cout << "no device connected!" << endl;
      return -1;
    }
    string serial = freenect2.getDefaultDeviceSerialNumber();

    pipeline = new libfreenect2::OpenGLPacketPipeline();
    dev = freenect2.openDevice(serial, pipeline);
    libfreenect2::SyncMultiFrameListener listener(libfreenect2::Frame::Color | libfreenect2::Frame::Depth);
    libfreenect2::FrameMap frames;
    dev->setColorFrameListener(&listener);
    dev->setIrAndDepthFrameListener(&listener);
    dev->start();

    cout << "device serial: " << dev->getSerialNumber() << endl;
    cout << "device firmware: " << dev->getFirmwareVersion() << endl;

    while (1) {
        listener.waitForNewFrame(frames);
        libfreenect2::Frame *rgb = frames[libfreenect2::Frame::Color];
        for (int i = 0;  i < 1920*1080; i++) {
            int pixel_id = i*4;
            fifo << rgb->data[pixel_id] << rgb->data[pixel_id+1] << rgb->data[pixel_id+2];
        }
        fifo << rgb->data;
        listener.release(frames);
        //libfreenect2::Frame *depth = frames[libfreenect2::Frame::Depth];
    }

    return 0;
};