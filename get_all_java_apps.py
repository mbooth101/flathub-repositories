#!/usr/bin/python3

# Requires: python3-pygithub python3-json-minify python3-pyyaml

from github import Github
import requests
import os

gh = Github(os.getenv("GH_ACCESS_TOKEN"))
gh_org = gh.get_organization("flathub")
gh_repos = gh_org.get_repos()

java_apps = {}
error_apps = {}

for r in gh_repos:
    # Skip themes and SDK extensions, no point in checking them
    if r.name.startswith('org.gtk.Gtk3theme') or r.name.startswith('org.freedesktop.Sdk.Extension') or r.name.startswith('org.kde.PlatformTheme'):
        continue
    # Attempt to download a manifest
    url_json = "https://raw.githubusercontent.com/%s/%s/%s.json" % (r.full_name, r.default_branch, r.name)
    url_yaml = "https://raw.githubusercontent.com/%s/%s/%s.yaml" % (r.full_name, r.default_branch, r.name)
    url_yml = "https://raw.githubusercontent.com/%s/%s/%s.yml" % (r.full_name, r.default_branch, r.name)
    res = requests.get(url_json)
    doc_type = "json"
    if res.status_code == 404:
        res = requests.get(url_yaml)
        doc_type = "yaml"
    if res.status_code == 404:
        res = requests.get(url_yml)
        doc_type = "yaml"
    # Skip any repo that has no manifest
    if res.status_code != 200:
        continue
    # Attempt to parse yaml/json manifests
    print("Parsing %s for %s" % (doc_type, r.full_name))
    manifest_data = None
    if doc_type == "json":
        import json
        try:
            manifest_data = json.loads(res.content)
        except json.decoder.JSONDecodeError:
            from json_minify import json_minify
            try:
                manifest_data = json.loads(json_minify(res.text))
            except json.decoder.JSONDecodeError as e:
                error_apps[r.name] = e
                continue
    if doc_type == "yaml":
        import yaml
        manifest_data = yaml.load(res.text, Loader=yaml.FullLoader)
    # Check if openjdk extension is used
    if 'sdk-extensions' in manifest_data.keys():
        exts = manifest_data['sdk-extensions']
        for ext in exts:
            if ext.startswith('org.freedesktop.Sdk.Extension.openjdk'):
                java_apps[r.name] = r.clone_url
                break

java_apps_sorted = dict(sorted(java_apps.items()))
os.makedirs("java_apps", exist_ok=True)
f = open('java_apps/list', 'w')
print("\nJava applications found:")
for key, value in java_apps_sorted.items():
    print("%s" % key)
    f.write("%s %s\n" % (key, value))
f.close()

print("\nApplications whose manifest failed to parse:")
for app in error_apps:
    print("%s: %s" % (app, error_apps[app]))

print("\nCloning known Java applications:")
for key, value in java_apps_sorted.items():
    if not os.path.isdir("java_apps/%s" % key):
        os.system("git clone %s java_apps/%s" % (value, key))
