cmake_minimum_required(VERSION 3.5)

project(Keychain Module)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/MySlicerExtension")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Henry Pehr, Henry Pehr")
set(EXTENSION_DESCRIPTION "creates keychain volume from two lobes (L and R)")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/MySlicerExtension.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/MySlicerExtension/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MySlicerExtension)
add_subdirectory(Keychain)
add_subdirectory(Keychain)
add_subdirectory(KeychainExtension)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
