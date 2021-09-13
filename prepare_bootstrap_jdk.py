#!/usr/bin/python3

import glob
import hashlib
import os
import shutil
import subprocess
import sys
import yaml

# Invokation: $ ./prepare_bootstrap_jdk.py [fedora] [package]
# Where:
#   [fedora] is the version of Fedora from which to take packages
#   [package] is the JDK package kind, e.g.: 11, 17 or latest
#
# Note: For building on Freedesktop 18.08, bootstrap binaries must be taken from
# Fedora 29 otherwise "`GLIBC_2.29' not found" error occurs
#
# Note: For building on Freedesktop 19.08, bootstrap binaries must be taken from
# Fedora 32 otherwise "`GLIBC_2.32' not found" error occurs

# Custom dumper to get indentation right
class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

if len(sys.argv) < 2:
    fedora = "32"
else:
    fedora = sys.argv[1]
if len(sys.argv) < 3:
    package = "java-latest-openjdk"
else:
    package = "java-%s-openjdk" % sys.argv[2]

if not os.path.isdir("bootstrap_jdk"):
    os.mkdir("bootstrap_jdk")

# Get the verion/release of the latest build from Koji
p = subprocess.run(["koji", "list-tagged", "--quiet", "--latest", "--inherit", "f%s-updates" % fedora, package], stdout=subprocess.PIPE)
verrel = "-".join(p.stdout.decode("utf-8").split()[0].split("-")[-2:])

# Generate tarballs
def gen_tarballs():
    print("Generating tarballs", file=sys.stderr)
    arches = {}
    for arch in ['x86_64', 'armv7hl', 'aarch64']:
        tarball = "bootstrap-openjdk-%s.%s.tar.bz2" % (verrel, arch)
        if not os.path.isfile("bootstrap_jdk/%s" % tarball):
        
            # Download and explode RPMs
            for name in [package, "%s-devel" % package, "%s-headless" % package]:
                nvra = "%s-%s.%s" % (name, verrel, arch)
                if not os.path.isfile("bootstrap_jdk/%s.rpm" % nvra):
                    subprocess.run(["koji", "download-build", "--rpm", nvra], cwd="bootstrap_jdk")
                subprocess.run(["rpm2cpio %s.rpm | cpio -idmuV" % nvra], cwd="bootstrap_jdk", shell=True)

            # Standardise name of directory
            for d in glob.glob("bootstrap_jdk/usr/lib/jvm/java-*"):
                os.rename(d, "bootstrap_jdk/usr/lib/jvm/java-openjdk")

            # Remove unneeded stuff and inject timezone data from host system
            shutil.rmtree("bootstrap_jdk/usr/lib/jvm/java-openjdk/tapset")
            shutil.rmtree("bootstrap_jdk/usr/lib/jvm/java-openjdk/legal")
            os.remove("bootstrap_jdk/usr/lib/jvm/java-openjdk/lib/tzdb.dat")
            shutil.copyfile("/usr/share/javazi-1.8/tzdb.dat", "bootstrap_jdk/usr/lib/jvm/java-openjdk/lib/tzdb.dat")

            # Create tarball and clean up
            subprocess.run(["tar", "caf", tarball, "usr/lib/jvm/java-openjdk"], cwd="bootstrap_jdk")
            shutil.rmtree("bootstrap_jdk/usr")
            shutil.rmtree("bootstrap_jdk/etc")

        # Create mapping of arch to tarball
        flatpak_arch = arch
        if arch == 'armv7hl':
            flatpak_arch = 'arm'
        arches[flatpak_arch] = tarball
    return arches

# Regenerate tarball SHA sums
def gen_sums():
    print("Generating SHA sums", file=sys.stderr)
    sums = []
    for tarball in glob.glob("bootstrap_jdk/*.tar.bz2"):
        m = hashlib.sha512()
        with open(tarball, 'rb') as f:
            while True:
                data = f.read(102400)
                if not data:
                    break
                m.update(data)
        sum = {'file': os.path.basename(tarball), 'sum': m.hexdigest()}
        sums.append(sum)
    with open("bootstrap_jdk/sha512sums", 'w') as f:
        for sum in sums:
            f.write("%s  %s\n" % (sum['sum'], sum['file']))
    return sums

# Update filenames and SHA sums of the bootstrap sources in the Flatpak manifest
def fettle_manifest(arches, sums):
    print("Updating Flatpak manifests", file=sys.stderr)
    major_version = verrel.split('.')[0]
    # 11 is bootstrapped with 11, 17 is bootstrapped with 16 or 17
    if major_version == '11' or major_version == '16' or major_version == '17':
        if major_version == '16':
            major_version = '17'
        extension = "org.freedesktop.Sdk.Extension.openjdk%s" % major_version
    else:
        extension = "org.freedesktop.Sdk.Extension.openjdk"
    manifest = "%s/%s.yaml" % (extension, extension)
    print("  %s" % manifest)
    with open(manifest, 'r') as f:
        manifest_data = yaml.safe_load(f)

    for arch in arches:
        tarball = arches[arch]
        sha512sum = [sum['sum'] for sum in sums if sum['file'] == tarball][0]

        for source in manifest_data['modules'][0]['sources']:
            if source['only-arches'][0] == arch:
                source['url'] = "https://fedorapeople.org/~mbooth/bootstrap_jdk/%s" % tarball
                source['sha512'] = sha512sum

    with open(manifest, 'w') as f:
        yaml.dump(manifest_data, f, Dumper=MyDumper, sort_keys=False, explicit_start=True, width=250, default_flow_style=False)

arch_map = gen_tarballs()
sum_list = gen_sums()
fettle_manifest(arch_map, sum_list)

print("Synching", file=sys.stderr)
subprocess.run(["rsync", "-rv", "--exclude=*.rpm", "bootstrap_jdk", "mbooth@fedorapeople.org:~/public_html"])

