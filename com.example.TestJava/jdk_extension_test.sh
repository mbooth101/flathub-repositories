#!/bin/bash
set -e

# Pass one argument that is the location of the JDK, i.e.:
#   $ ./jdk_extension_test.sh "/usr/lib/sdk/openjdk"

jdk=$1
echo "# Testing $jdk..."
echo

source $jdk/enable.sh

echo '## Execute Java:'
echo
java -version
echo

echo '## Execute Java Compiler:'
echo
javac -version
echo

echo '## Execute Maven:'
echo
mvn -version
echo

echo '## Installed Sizes:'
echo
$jdk/install.sh
$jdk/installjdk.sh
version=$(/app/jre/bin/java -version 2>&1 | head -n1 | sed 's/.*"\(.*\)".*/\1/')
mv /app/jre /app/jre${version}
du /app/jre${version}/ -sh
version=$(/app/jdk/bin/java -version 2>&1 | head -n1 | sed 's/.*"\(.*\)".*/\1/')
mv /app/jdk /app/jdk${version}
du /app/jdk${version}/ -sh
echo

