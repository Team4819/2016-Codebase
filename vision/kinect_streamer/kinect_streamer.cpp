#include <libfreenect2/libfreenect2.hpp>
#include <libfreenect2/frame_listener_impl.h>
#include <libfreenect2/registration.h>
#include <libfreenect2/packet_pipeline.h>
#include <libfreenect2/logger.h>
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
// GStreamer
#include <gstreamer-1.0/gst/gst.h>
#include <gstreamer-1.0/gst/gstelement.h>
#include <gstreamer-1.0/gst/gstpipeline.h>
#include <gstreamer-1.0/gst/gstutils.h>
#include <gstreamer-1.0/gst/app/gstappsrc.h>
using namespace std;

GstElement *rgb_appsrc;
GstElement *depth_appsrc;
bool end_kinect = false;
libfreenect2::SyncMultiFrameListener listener(libfreenect2::Frame::Color | libfreenect2::Frame::Depth);
libfreenect2::FrameMap frames;

union UStuff
{
        float   f;
        unsigned char   c[4];
};

void do_kinect_frame()
{

      GstFlowReturn ret;

      listener.waitForNewFrame(frames);
      libfreenect2::Frame *rgb = frames[libfreenect2::Frame::Color];
      libfreenect2::Frame *depth = frames[libfreenect2::Frame::Depth];

      guint rgb_size = 1920 * 1080 * 4;
      GstBuffer* rgb_buffer = gst_buffer_new_allocate(NULL, rgb_size, NULL);
      gst_buffer_fill(rgb_buffer, 0, rgb->data, rgb_size);
      g_signal_emit_by_name (rgb_appsrc, "push-buffer", rgb_buffer, &ret);
      gst_buffer_unref(rgb_buffer);

      if (ret != GST_FLOW_OK) {
        /* something wrong, stop pushing */
        end_kinect = true;
      }

      guint depth_size = 512 * 424;
      UStuff conv;
      char * depth_data_buffer = new char[depth_size];
      for (int i=0; i<depth_size; i++){
        int n = i*4;
        conv.c[0] = depth->data[n];
        conv.c[1] = depth->data[n+1];
        conv.c[2] = depth->data[n+2];
        conv.c[3] = depth->data[n+3];
        depth_data_buffer[i] = (char)((4500 - conv.f)/4500*255);
      }
      GstBuffer* depth_buffer = gst_buffer_new_wrapped(depth_data_buffer, depth_size);
      g_signal_emit_by_name (depth_appsrc, "push-buffer", depth_buffer, &ret);
      gst_buffer_unref(depth_buffer);

      if (ret != GST_FLOW_OK) {
        /* something wrong, stop pushing */
        end_kinect = true;
      }

      listener.release(frames);
}

void libfreenect_thread ()
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

  dev->setColorFrameListener(&listener);
  dev->setIrAndDepthFrameListener(&listener);
  dev->start();

  cout << "device serial: " << dev->getSerialNumber() << endl;
  cout << "device firmware: " << dev->getFirmwareVersion() << endl;

  while (!end_kinect) {
    do_kinect_frame();
  }

  dev->stop();
  dev->close();
}

static GMainLoop *loop;

int main (int argc, char *argv[])
{
  std::cout << "Error setting rgb pipeline to playing.";

  GstElement *rgb_pipeline, *rgb_conv, *rgb_scale, *rgb_rate, *rgb_enc, *rgb_mux, *rgb_serversink;
  GstElement *depth_pipeline, *depth_conv, *depth_scale, *depth_rate, *depth_enc, *depth_mux, *depth_serversink;
  GstElement *depth_tee, *depth_queue, *depth_raw_queue *depth_raw_scale, *depth_raw_rate, *depth_raw_serversink;

  /* init GStreamer */
  gst_init (&argc, &argv);
  loop = g_main_loop_new (NULL, FALSE);

  /* setup pipeline */
  rgb_pipeline = gst_pipeline_new ("rgb_pipeline");
  rgb_appsrc = gst_element_factory_make ("appsrc", "kinect rgb appsrc");
  rgb_conv = gst_element_factory_make ("videoconvert", "rgb converter");
  rgb_rate = gst_element_factory_make ("videorate", "rgb rater");
  rgb_scale = gst_element_factory_make ("videoscale", "rgb scaler");

  rgb_enc = gst_element_factory_make ("jpegenc", "rgb h264 enc");
  rgb_mux = gst_element_factory_make ("multipartmux", "rgb muxer");
  rgb_serversink = gst_element_factory_make ("tcpserversink", "rgb tcp server");

  if (!rgb_pipeline || !rgb_appsrc || !rgb_conv || !rgb_rate || !rgb_scale) {
    g_printerr ("One element could not be created. Exiting.\n");
    return -1;
  }

  if (!rgb_enc) {
    g_printerr ("encoder could not be created. Exiting.\n");
    return -1;
  }

  if (!rgb_mux) {
    g_printerr ("muxer could not be created. Exiting.\n");
    return -1;
  }

  if (!rgb_serversink) {
    g_printerr ("tcpserversink could not be created. Exiting.\n");
    return -1;
  }

  /* setup */
  g_object_set (G_OBJECT (rgb_appsrc), "caps",
  		gst_caps_new_simple ("video/x-raw",
				     "format", G_TYPE_STRING, "RGBx",
				     "width", G_TYPE_INT, 1920,
				     "height", G_TYPE_INT, 1080,
				     "framerate", GST_TYPE_FRACTION, 0, 1,
				     NULL), NULL);
  gst_bin_add_many (GST_BIN (rgb_pipeline), rgb_appsrc, rgb_rate, rgb_scale, rgb_conv, rgb_enc, rgb_mux, rgb_serversink, NULL);
  gst_element_link_many (rgb_appsrc, rgb_rate, rgb_scale, rgb_conv, NULL);
  GstCaps *rgb_caps = gst_caps_new_simple ("video/x-raw",
                     //"format", G_TYPE_STRING, "I420",
				     "width", G_TYPE_INT, 480,
				     "height", G_TYPE_INT, 270,
				     "framerate", GST_TYPE_FRACTION, 15, 1,
				     NULL);
  gst_element_link_filtered (rgb_conv, rgb_enc, rgb_caps);
  gst_element_link_many (rgb_enc, rgb_mux, rgb_serversink, NULL);

  /* setup appsrc */
  g_object_set (G_OBJECT (rgb_appsrc),
		"stream-type", GST_APP_STREAM_TYPE_STREAM,
		"format", GST_FORMAT_TIME,
		"is-live", true,
		//"block", true,
		//"min-latency", 0,
		//"max-latency", 5,
		//"do-timestamp", true,
		NULL);

  //g_object_set (G_OBJECT (rgb_enc),
      //"low-latency", true,
      //"framerate", 10,
      //"bitrate", 300000,
      //"tune", "Zero latency",
      //"target-bitrate", 256000,
      //"end-usage", 1,
      //"deadline", 1,
      //"buffer-size", 100,
      //"speed_preset", 1,
      //"bitrate"
      //"buffer-initial-size", 100,
      //"lag-in-frames", 0,
   //   NULL);

  //g_object_set (G_OBJECT (rgb_mux),
  //      "streamable", true,
  //      NULL);

  g_object_set (G_OBJECT (rgb_serversink),
        "sync", false,
        //"async", false,
        //"max-lateness", 50000000,
        "sync-method", 2,
        //"buffers-max", 10,
        //"units-max", 10,
        //"max-bitrate", 1000000,
        //"recover-policy", 1,
        "host", "10.48.19.6",
        "port", 5805,
        NULL);

  // DEPTH PIPELINE

  depth_pipeline = gst_pipeline_new ("depth_pipeline");
  depth_appsrc = gst_element_factory_make ("appsrc", "kinect depth appsrc");
  depth_conv = gst_element_factory_make ("videoconvert", "depth converter");
  depth_rate = gst_element_factory_make ("videorate", "depth rate");
  depth_scale = gst_element_factory_make ("videoscale", "depth scale");

  depth_tee = gst_element_factory_make ("tee", "depth tee");

  depth_queue = gst_element_factory_make ("queue", "depth jpeg queue");
  depth_enc = gst_element_factory_make ("jpegenc", "depth jpeg enc");
  depth_mux = gst_element_factory_make ("multipartmux", "depth muxer");
  depth_serversink = gst_element_factory_make ("tcpserversink", "depth tcp server");

  depth_raw_queue = gst_element_factory_make ("queue", "depth raw queue");
  depth_raw_rate = gst_element_factory_make ("videorate", "depth raw rate");
  depth_raw_scale = gst_element_factory_make ("videoscale", "depth raw scale");
  depth_raw_serversink = gst_element_factory_make ("tcpserversink", "depth raw tcp server");

  /* setup */
  g_object_set (G_OBJECT (depth_appsrc), "caps",
  		gst_caps_new_simple ("video/x-raw",
  				     "format", G_TYPE_STRING, "GRAY8",
  				     "width", G_TYPE_INT, 512,
  				     "height", G_TYPE_INT, 424,
  				     "framerate", GST_TYPE_FRACTION, 0, 1,
  				     NULL), NULL);
  gst_bin_add_many (GST_BIN (depth_pipeline), depth_appsrc, depth_rate, depth_scale, depth_conv, depth_enc, depth_mux, depth_serversink, depth_raw_rate, depth_raw_scale, depth_raw_serversink, NULL);
  gst_element_link_many (depth_appsrc, depth_rate, depth_scale, depth_conv, depth_tee, NULL);

  // Encoded tcp socket
  GstCaps *depth_encoded_caps = gst_caps_new_simple ("video/x-raw",
  				     "width", G_TYPE_INT, 256,
  				     "height", G_TYPE_INT, 212,
  				     "framerate", GST_TYPE_FRACTION, 15, 1,
  				     NULL);
  gst_element_link_filtered (depth_tee, depth_enc, depth_encoded_caps);
  gst_element_link_many (depth_enc, depth_mux, depth_serversink, NULL);

  // Raw tcp socket
  GstCaps *depth_raw_caps = gst_caps_new_simple ("video/x-raw",
  			     "width", G_TYPE_INT, 128,
  			     "height", G_TYPE_INT, 106,
  			     "framerate", GST_TYPE_FRACTION, 10, 1,
  			     NULL);
  gst_element_link_many (depth_tee, depth_raw_rate, depth_raw_scale, NULL);
  gst_element_link_filtered (depth_raw_scale, depth_raw_serversink, depth_raw_caps);

  /* setup appsrc */
  g_object_set (G_OBJECT (depth_appsrc),
		"stream-type", GST_APP_STREAM_TYPE_STREAM,
		"format", GST_FORMAT_TIME,
		"is-live", true,
		//"block", true,
		//"min-latency", 0,
		//"max-latency", 5,
		//"do-timestamp", true,
		NULL);

  g_object_set (G_OBJECT (depth_serversink),
        "sync", false,
        "sync-method", 2,
        "host", "10.48.19.6",
        "port", 5806,
        NULL);

  g_object_set (G_OBJECT (depth_raw_serversink),
        "sync", false,
        "host", "10.48.19.6",
        "port", 5807,
        NULL);

  std::thread t1(libfreenect_thread);

  /* play */
  //gst_element_set_state( rgb_pipeline, GST_STATE_PAUSED );
  //std::this_thread::sleep_for(std::chrono::seconds(5));
  GstStateChangeReturn ret1 = gst_element_set_state( rgb_pipeline, GST_STATE_PLAYING );
    if( ret1 == GST_STATE_CHANGE_FAILURE ) {
      std::cout << "Error setting rgb pipeline to playing.";
      return 2;
  }


  GstStateChangeReturn ret2 = gst_element_set_state( depth_pipeline, GST_STATE_PLAYING );
  if( ret2 == GST_STATE_CHANGE_FAILURE ) {
      std::cout << "Error setting depth pipeline to playing.";
      return 2;
  }
  g_main_loop_run (loop);

  end_kinect = true;
  t1.join();

  /* clean up */
  gst_element_set_state (rgb_pipeline, GST_STATE_NULL);
  gst_element_set_state (depth_pipeline, GST_STATE_NULL);
  gst_object_unref (GST_OBJECT (rgb_pipeline));
  gst_object_unref (GST_OBJECT (depth_pipeline));
  g_main_loop_unref (loop);

  return 0;
}
