#!/usr/bin/python3

import re
from time import sleep
from os import system, chdir
from os.path import join, dirname, realpath
from urllib.parse import quote_plus
from random import randint

extensions = []
# Extension name, download URL, Unpack after download (some extensions need to be unpacked before you can use them)
extensions.append(['sls', 'https://addons.mozilla.org/firefox/downloads/latest/463075/', False])
extensions.append(['firetray', 'https://addons.mozilla.org/thunderbird/downloads/latest/4868/platform:2/', True])
extensions.append(['shrunked', 'https://addons.mozilla.org/thunderbird/downloads/latest/11005/', False])
extensions.append(['importexporttools', 'https://addons.mozilla.org/thunderbird/downloads/file/348080/', False])

# Set profile dir
script_dir = dirname(realpath(__file__))
profile_dir = join(script_dir, "etc/skel/.thunderbird/pjzwmea6.default")


# Download xpi function
def download_from_url(url, target_dir, unzip=False):
    print((""))
    print(("======================== START DOWNLOAD ========================"))
    print((">> Download: %s" % url))
    print((">> Save to: %s" % target_dir))
    print((">> Unzip in target: %s" % str(unzip)))
    print(("================================================================"))
    print((""))

    # Return a dictionary with id and version of the xpi
    ret_dict = {}
    ret_dict["id"] = ''
    ret_dict["version"] = ''

    # Wait between 1 and 10 seconds to prevent server error
    secs = randint(2, 9)
    sleep(secs)

    system("mkdir -p %s" % target_dir)
    chdir(target_dir)

    try:
        # Download the xpi
        system("wget -nc %s -O tmp.xpi" % url)
    except:
        print(("FAILED: Could not download %s" % url))
        return ret_dict

    try:
        # Read info from install.rdf
        system("unzip tmp.xpi install.rdf")
        rdf = ""
        with open("install.rdf", 'r') as f:
            rdf = f.read()
        system("rm install.rdf")

        matchVersion = re.search("\<[em:]*version\>(.*)\<[/em:]*version\>", rdf)
        matchId = re.search('id[>="]+(.*)[<"]', rdf)

        if matchVersion:
            ret_dict["version"] = matchVersion.group(1)

        if matchId:
            ret_dict["id"] = matchId.group(1)
            if unzip:
                system("unzip -o tmp.xpi -d %s" % ret_dict["id"])
                system("rm tmp.xpi")
            else:
                system("mv -vf tmp.xpi %s.xpi" % ret_dict["id"])
        else:
            print(("FAILED: Could not get Id from %s" % url))
            system("rm -v tmp.xpi")
            return ret_dict
    except:
        print(("FAILED: Could not info read from %s" % url))
        system("rm tmp.xpi")
        return ret_dict

    # All's well
    return ret_dict

# Add extensions
ext_list = []
prefs_list = []

# Get the default preferences first
prefs_path = join(script_dir, "templates/prefs.js")
with open(prefs_path, 'r') as f:
    prefs_list = f.readlines()

# Loop through the extensions
for extension in extensions:
    ret_dict = download_from_url(extension[1], join(profile_dir, "extensions"), extension[2])
    if ret_dict["version"] != '' and ret_dict["id"] != '':
        # Extension specific configuration
        if extension[0] == 'firetray':
            prefs_list.append("user_pref(\"extensions.firetray.app_browser_icon_names\", \"[\\\"web-browser\\\",\\\"firefox\\\"]\");\n")
            prefs_list.append("user_pref(\"extensions.firetray.firstrun\", false);\n")
            prefs_list.append("user_pref(\"extensions.firetray.installedVersion\", \"%s\");\n" % ret_dict["version"])
            prefs_list.append("user_pref(\"extensions.firetray.show_icon_on_hide\", true);\n")
        elif extension[0] == "adblockplus":
            prefs_list.append("user_pref(\"extensions.adblockplus.currentVersion\", \"%s\");\n" % ret_dict["version"])
        elif extension[0] == "qls":
            prefs_list.append("user_pref(\"extensions.qls.switch_gulocale\", true);\n")
            prefs_list.append("user_pref(\"extensions.qls.visiblemenuitems\", \"en-US\");\n")
        elif extension[0] == 'sls':
            buttons = '{\"placements\":{\"PanelUI-contents\":[\"edit-controls\",\"zoom-controls\",\"new-window-button\",\"privatebrowsing-button\",\"save-page-button\",\"print-button\",\"history-panelmenu\",\"fullscreen-button\",\"find-button\",\"preferences-button\",\"add-ons-button\",\"developer-button\",\"simplels-widget\"]}}'
            prefs_list.append('user_pref("browser.uiCustomization.state", "%s");\n' % buttons.replace('\"', '\\\"'))

        # Save version
        print((">>> Extension info: %s:%s" % (ret_dict["id"], ret_dict["version"])))
        ext_list.append("%s:%s" % (ret_dict["id"], ret_dict["version"]))

# Write prefs.js
enabled_addons = quote_plus(",".join(ext_list), ":,")
prefs_list.append("user_pref(\"extensions.enabled_addons\", \"%s\");\n" % enabled_addons)
prefs_path = join(profile_dir, "prefs.js")
with open(prefs_path, 'w') as f:
    f.write("".join(prefs_list))
