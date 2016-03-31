cmake_minimum_required(VERSION 2.8)
project( kinect_streamer CXX )
find_package(freenect2 REQUIRED)

####################################################################################################
# G++ Options
####################################################################################################
set( CMAKE_C_COMPILER "gcc" )
set( CMAKE_CXX_COMPILER "g++" )

set( CMAKE_CXX_FLAGS "-g -pthread -O0 -std=c++11 -ggdb -Wall -W -Wunused-variable -Wunused-parameter -Wunused-function -Wunused -Woverloaded-virtual -Wwrite-strings --coverage" )
set( CMAKE_C_FLAGS ${CMAKE_CXX_FLAGS} )

find_package(PkgConfig)
pkg_check_modules( GSTREAMER_1_0 gstreamer-1.0 )
pkg_check_modules( GSTREAMER_1_0_APP gstreamer-app-1.0 )
include_directories( ${GSTREAMER_1_0_INCLUDE_DIRS} )
include_directories( ${GSTREAMER_1_0_APP_INCLUDE_DIRS} )

add_executable( kinect_streamer kinect_streamer.cpp)
add_executable( kinect_reset kinect_reset.cpp)
target_link_libraries(kinect_streamer freenect2 ${GSTREAMER_1_0_LIBRARIES} ${GSTREAMER_1_0_APP_LIBRARIES})
target_link_libraries(kinect_reset freenect2)
set_target_properties( kinect_streamer PROPERTIES LINKER_LANGUAGE CXX )