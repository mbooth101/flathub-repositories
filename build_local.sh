#!/bin/bash

for jdk in $* ; do
	flatpak-builder --force-clean --repo=repo jdk-build org.freedesktop.Sdk.Extension.openjdk$jdk/org.freedesktop.Sdk.Extension.openjdk$jdk.json
	flatpak remote-add --if-not-exists --no-gpg-verify test-java file://$(pwd)/repo
	flatpak install -y test-java org.freedesktop.Sdk.Extension.openjdk$jdk
	flatpak update -y org.freedesktop.Sdk.Extension.openjdk$jdk
done

flatpak-builder --force-clean --repo=repo jdk-build com.example.TestJava/com.example.TestJava.json
flatpak install -y test-java com.example.TestJava
flatpak update -y com.example.TestJava
