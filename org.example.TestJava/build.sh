#!/bin/sh

flatpak update
flatpak-builder --force-clean --repo=repo build org.example.TestJava.json
flatpak remote-add --if-not-exists --no-gpg-verify test-java file://$(pwd)/repo
