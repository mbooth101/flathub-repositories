#!/bin/bash

for jdk in $* ; do
	flatpak run org.freedesktop.appstream-glib validate org.freedesktop.Sdk.Extension.$jdk/*.xml
	flatpak-builder --force-clean --repo=repo jdk-build org.freedesktop.Sdk.Extension.$jdk/org.freedesktop.Sdk.Extension.$jdk.json
	flatpak remote-add --if-not-exists --no-gpg-verify test-java file://$(pwd)/repo
	flatpak install -y test-java org.freedesktop.Sdk.Extension.$jdk
	flatpak update -y org.freedesktop.Sdk.Extension.$jdk
done

flatpak-builder --force-clean --repo=repo jdk-build com.example.TestJava/com.example.TestJava.json
flatpak remote-add --if-not-exists --no-gpg-verify test-java file://$(pwd)/repo
flatpak install -y test-java com.example.TestJava
flatpak update -y com.example.TestJava
