#!/bin/bash

localrepo="local-repo"

openjdk=
for app in $* ; do
	app=${app%/}
	if [[ $app == openjdk* ]] ; then
		app="org.freedesktop.Sdk.Extension.$app"
		openjdk="true"
	fi
	if [ -f "$app/$app.yaml" ] ; then
		flatpak-builder --force-clean --disable-cache --user --install local-build $app/$app.yaml
	else
		flatpak-builder --force-clean --disable-cache --user --install local-build $app/$app.json
	fi
done

# If we built an openjdk, build the test app
if [ -n "$openjdk" ] ; then
	flatpak-builder --force-clean --repo=$localrepo local-build com.example.TestJava/com.example.TestJava.json
	flatpak remote-add --if-not-exists --no-gpg-verify $localrepo file://$(pwd)/$localrepo
	flatpak install -y $localrepo com.example.TestJava
	flatpak update -y com.example.TestJava
fi
