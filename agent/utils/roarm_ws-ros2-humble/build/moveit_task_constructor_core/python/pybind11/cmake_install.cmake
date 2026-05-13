# Install script for directory: /workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_else/moveit_task_constructor/core/python/pybind11

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_core")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/llvm-objdump-18")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/moveit/python" TYPE DIRECTORY FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_else/moveit_task_constructor/core/python/pybind11/include/pybind11")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/moveit_task_constructor_core/cmake" TYPE FILE FILES
    "/workspace/roarm_ws/roarm_ws-ros2-humble/build/moveit_task_constructor_core/python/pybind11/pybind11Config.cmake"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/build/moveit_task_constructor_core/python/pybind11/pybind11ConfigVersion.cmake"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_else/moveit_task_constructor/core/python/pybind11/tools/FindPythonLibsNew.cmake"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_else/moveit_task_constructor/core/python/pybind11/tools/pybind11Common.cmake"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_else/moveit_task_constructor/core/python/pybind11/tools/pybind11Tools.cmake"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_else/moveit_task_constructor/core/python/pybind11/tools/pybind11NewTools.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/moveit_task_constructor_core/cmake/pybind11Targets.cmake")
    file(DIFFERENT EXPORT_FILE_CHANGED FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/moveit_task_constructor_core/cmake/pybind11Targets.cmake"
         "/workspace/roarm_ws/roarm_ws-ros2-humble/build/moveit_task_constructor_core/python/pybind11/CMakeFiles/Export/share/moveit_task_constructor_core/cmake/pybind11Targets.cmake")
    if(EXPORT_FILE_CHANGED)
      file(GLOB OLD_CONFIG_FILES "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/moveit_task_constructor_core/cmake/pybind11Targets-*.cmake")
      if(OLD_CONFIG_FILES)
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/moveit_task_constructor_core/cmake/pybind11Targets.cmake\" will be replaced.  Removing files [${OLD_CONFIG_FILES}].")
        file(REMOVE ${OLD_CONFIG_FILES})
      endif()
    endif()
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/moveit_task_constructor_core/cmake" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/moveit_task_constructor_core/python/pybind11/CMakeFiles/Export/share/moveit_task_constructor_core/cmake/pybind11Targets.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/pkgconfig" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/moveit_task_constructor_core/python/pybind11/pybind11.pc")
endif()

