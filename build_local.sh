#!/bin/sh

flatpak update

for jdk in org.freedesktop.Sdk.Extension.openjdk* ; do
	flatpak-builder --force-clean --repo=repo build-jdk $jdk/$jdk.json
	flatpak remote-add --if-not-exists --no-gpg-verify test-java file://$(pwd)/repo
	flatpak install -y test-java $jdk
	flatpak update -y $jdk
done

flatpak-builder --force-clean --repo=repo build-test com.example.TestJava/com.example.TestJava.json
flatpak install -y test-java com.example.TestJava
flatpak update -y com.example.TestJava
