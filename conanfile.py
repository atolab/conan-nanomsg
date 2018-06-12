#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class NanomsgConan(ConanFile):
    name = "nanomsg"
    version = "1.1.2"
    homepage = "https://nanomsg.org/"
    url="https://github.com/k0ekk0ek/conan-nanomsg"
    description = "A socket library that provides several common communication patterns"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    short_paths = True
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    options = {
        "shared": [True, False],
        "enable_doc": [True, False],
        "enable_getaddrinfo_a": [True, False],
        "enable_tests": [True, False],
        "enable_tools": [True, False],
        "enable_nanocat": [True, False],
        "fPIC": [True, False]
    }
    
    default_options = (
        "shared=False", 
        "enable_doc=False", 
        "enable_getaddrinfo_a=True", 
        "enable_tests=False", 
        "enable_tools=True", 
        "enable_nanocat=True",
        "fPIC=True"
    )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/nanomsg/nanomsg"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
        #Rename to "sources" is a convention to simplify later steps

    def configure(self):
        del self.settings.compiler.libcxx

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["NN_STATIC_LIB"] = not self.options.shared
        cmake.definitions["NN_ENABLE_DOC"] = self.options.enable_doc
        cmake.definitions["NN_ENABLE_GETADDRINFO_A"] = self.options.enable_getaddrinfo_a
        cmake.definitions["NN_TESTS"] = self.options.enable_tests
        cmake.definitions["NN_TOOLS"] = self.options.enable_tools
        cmake.definitions["NN_ENABLE_NANOCAT"] = self.options.enable_nanocat
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        if os.path.exists("{0}/lib64".format(self.package_folder)):
            os.rename("{0}/lib64".format(self.package_folder),
                      "{0}/lib".format(self.package_folder))

    def package_info(self):
        self.cpp_info.libs = ["nanomsg"]

        if not self.options.shared:
            self.cpp_info.defines.extend(["NN_STATIC_LIB=ON"])

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.append('mswsock')
                self.cpp_info.libs.append('ws2_32')
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append('anl')
            self.cpp_info.libs.append('pthread')