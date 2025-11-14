# ChromaFrame - 2D Flip-Book Animator
# CMake build configuration

cmake_minimum_required(VERSION 3.20)

project(ChromaFrame
    VERSION 0.1.0
    DESCRIPTION "Professional 2D flip-book animation software"
    LANGUAGES CXX
)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Options
option(CHROMAFRAME_BUILD_TESTS "Build tests" ON)
option(CHROMAFRAME_USE_VULKAN "Use Vulkan instead of OpenGL" OFF)
option(CHROMAFRAME_ENABLE_PROFILING "Enable profiling support" OFF)

# Find dependencies
find_package(Qt6 6.5 REQUIRED COMPONENTS
    Core
    Gui
    Widgets
    OpenGL
    OpenGLWidgets
)

find_package(OpenGL REQUIRED)

# FFmpeg (will need custom find module or pkg-config)
# find_package(FFmpeg REQUIRED COMPONENTS
#     avcodec
#     avformat
#     avutil
#     swscale
# )

# Platform-specific settings
if(WIN32)
    # Windows-specific settings
    add_definitions(-DPLATFORM_WINDOWS)
elseif(APPLE)
    # macOS-specific settings
    add_definitions(-DPLATFORM_MACOS)
elseif(UNIX)
    # Linux-specific settings
    add_definitions(-DPLATFORM_LINUX)
endif()

# Compiler warnings
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/src
)

# Source files (placeholder - will be organized by module)
set(CHROMAFRAME_SOURCES
    # Core
    src/core/Application.cpp
    src/core/Project.cpp
    src/core/Scene.cpp
    src/core/Layer.cpp
    src/core/Frame.cpp

    # Data Model
    src/data/AnimationData.cpp
    src/data/Stroke.cpp

    # Graphics
    src/graphics/GraphicsEngine.cpp
    src/graphics/CanvasRenderer.cpp
    src/graphics/BrushEngine.cpp

    # Tools
    src/tools/ToolManager.cpp
    src/tools/BrushTool.cpp
    src/tools/EraserTool.cpp

    # UI
    src/ui/MainWindow.cpp
    src/ui/Canvas.cpp
    src/ui/Timeline.cpp
    src/ui/ToolPalette.cpp

    # Export
    src/export/RenderPipeline.cpp
    src/export/VideoEncoder.cpp

    # I/O
    src/io/FileIO.cpp
    src/io/ProjectSerializer.cpp

    # Main
    src/main.cpp
)

set(CHROMAFRAME_HEADERS
    include/chromaframe/Application.h
    include/chromaframe/Project.h
    # ... add more as developed
)

# Executable
add_executable(chromaframe
    ${CHROMAFRAME_SOURCES}
    ${CHROMAFRAME_HEADERS}
)

# Link libraries
target_link_libraries(chromaframe
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::OpenGL
    Qt6::OpenGLWidgets
    OpenGL::GL
    # FFmpeg::avcodec
    # FFmpeg::avformat
    # FFmpeg::avutil
    # FFmpeg::swscale
)

# Include Qt MOC
set_target_properties(chromaframe PROPERTIES
    AUTOMOC ON
    AUTORCC ON
    AUTOUIC ON
)

# Tests
if(CHROMAFRAME_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Installation
install(TARGETS chromaframe
    RUNTIME DESTINATION bin
)

# Print configuration summary
message(STATUS "")
message(STATUS "ChromaFrame Configuration Summary")
message(STATUS "==================================")
message(STATUS "Version:          ${PROJECT_VERSION}")
message(STATUS "Build type:       ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard:     ${CMAKE_CXX_STANDARD}")
message(STATUS "Build tests:      ${CHROMAFRAME_BUILD_TESTS}")
message(STATUS "Graphics API:     ${CHROMAFRAME_USE_VULKAN}")
message(STATUS "Profiling:        ${CHROMAFRAME_ENABLE_PROFILING}")
message(STATUS "Qt version:       ${Qt6_VERSION}")
message(STATUS "Install prefix:   ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")
