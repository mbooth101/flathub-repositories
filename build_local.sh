#!/bin/sh

flatpak update

for jdk in 9 10 ; do
	ext=org.freedesktop.Sdk.Extension.openjdk${jdk}
	flatpak-builder --force-clean --repo=repo jdk${jdk}-build $ext/$ext.json
	flatpak remote-add --if-not-exists --no-gpg-verify test-java file://$(pwd)/repo
	flatpak install -y test-java $ext
done

flatpak-builder --force-clean --repo=repo test-build com.example.TestJava/com.example.TestJava.json
