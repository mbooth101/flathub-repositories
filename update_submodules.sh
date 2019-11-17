#!/bin/bash

git submodule init
git submodule update --remote
git add org.eclipse.* org.freedesktop.Sdk.Extension.*
git diff --cached --exit-code
if [ $? -ne 0 ] ; then
	git commit --signoff -m "Update submodules to latest snapshots"
fi
