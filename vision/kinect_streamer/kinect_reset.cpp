#include <libfreenect2/libfreenect2.hpp>
#include <libfreenect2/frame_listener_impl.h>
#include <libfreenect2/registration.h>
#include <libfreenect2/packet_pipeline.h>
#include <libfreenect2/logger.h>
#include <string>
#include <unistd.h>
#include <iostream>

using namespace std;

int main (int argc, char *argv[])
{
  libfreenect2::Freenect2 freenect2;
  libfreenect2::Freenect2Device *dev = 0;
  //libfreenect2::SyncMultiFrameListener listener(libfreenect2::Frame::Color | libfreenect2::Frame::Depth);


  // Init kinect
  if(freenect2.enumerateDevices() == 0)
  {
    cout << "no device connected!" << endl;
  }
  string serial = freenect2.getDefaultDeviceSerialNumber();

  dev = freenect2.openDevice(serial, new libfreenect2::CudaPacketPipeline());
  //dev = freenect2.openDevice(serial);

  dev->start();
  sleep(2);
  dev->stop();
  dev->close();
}