#!/usr/bin/env python

import os
import subprocess
import shutil

# Based on https://nix.dev/manual/nix/2.18/installation/uninstall

def remove_nix_block_from_profile(profile_name):
    print (f"Removing Nix startup daemon from profile {profile_name} ...")
    with open(profile_name, "r") as r, open(f"{profile_name}.after_restored", "w") as w:
        removing = False
        for line in r:
            if "# Nix" in line:
                removing = True
            if not removing:
                w.write(line)
            if "# End Nix" in line:
                removing = False
    os.rename(profile_name, f"{profile_name}.before_restore")
    os.rename(f"{profile_name}.after_restored", profile_name)
    os.remove(f"{profile_name}.backup-before-nix")

def remove_daemon(daemon_file):
    print (f"Removing daemon {daemon_file} ...")
    if os.path.exists(daemon_file):
        instance = subprocess.run([ "launchctl", "unload", daemon_file ], capture_output=True, text=True)
        if instance.returncode != 0:
            raise RuntimeError(f"Unable to remove daemon.\n{instance.stderr}")
        os.remove(daemon_file)
    else:
        print (f"Daemon {daemon_file} is missing ... skipped")
    
def remove_nix_groups_and_users():
    print ("Removing Nix group ...")
    instance = subprocess.run([ "dscl", ".", "-list", "/Groups/nixbld" ], capture_output=True, text=True)
    if instance.returncode == 0:
        instance = subprocess.run([ "dscl", ".", "-delete", "/Groups/nixbld" ])
    else:
        if instance.returncode == 185: # No group found
            print("Nix group nixbld is missing ... skipped")
    
    print ("Removing Nix users ...")
    instance = subprocess.run([ "dscl", ".", "-list", "/Users" ], capture_output=True, text=True)
    if instance.returncode == 0:
        output = instance.stdout
        user_list = list(filter(lambda l: "_nixbld" in l, output.split("\n")))
        if len(user_list) > 0:
            for user in user_list:
                print (f"Removing Nix user: {user} ...")
                instance = subprocess.run([ "dscl", ".", "-delete", f"/Users/{user}" ], capture_output=True, text=True)
                if instance.returncode != 0:
                    print(f"Unable to remove Nix user.\n{instance.stdout}")
        else:
            print("Nix users with nixbld is missing ... skipped")

def remove_fstab():
    print ("Removing Nix volume mounting ...")
    with open("/etc/fstab", "r") as r, open(f"/etc/fstab.after_restored", "w") as w:
        for line in r:
            if " /nix " not in line:
                w.write(line)
    os.rename("/etc/fstab", f"/etc/fstab.before_restore")
    os.rename(f"/etc/fstab.after_restored", "/etc/fstab")
    
    if os.path.exists("/etc/synthetic.conf"):
        print ("Restoring /etc/synthetic.conf ...")
        with open("/etc/synthetic.conf", "r") as r, open(f"/etc/synthetic.conf.after_restored", "w") as w:
            for line in r:
                if line != "nix":
                    w.write(line)
        os.rename("/etc/synthetic.conf", f"/etc/synthetic.conf.before_restore")
        os.rename(f"/etc/synthetic.conf.after_restored", "/etc/synthetic.conf")
    else:
        print ("/etc/synthetic.conf is missing ... skipped")
    
def remove_profiles():
    profiles = [
        "/etc/nix",
        "/var/root/.nix-profile",
        "/var/root/.nix-defexpr",
        "/var/root/.nix-channels",
        "~/.nix-profile",
        "~/.nix-defexpr",
        "~/.nix-channels"
    ]
    for profile in profiles:
        print(f"Removing profile {profile} ...")
        try:
            if profile.startswith("~/"):
                home_dir = os.path.expanduser("~")
                profile = os.path.join(home_dir, profile[2:])
                print(f"Home directory is expanded to {profile}")

            if not os.path.exists(profile):
                print(f"Unable to remove directory {profile} ... skipped")
            elif os.path.islink(profile):
                print(f"Profile {profile} is symbolic link. Unlinking ...")
                os.unlink(profile)
            elif os.path.isfile(profile):
                print(f"Profile {profile} is file. Removing ...")
                os.remove(profile)
            elif os.path.isdir(profile):
                print(f"Profile {profile} is directory. Removing entire directory ...")
                shutil.rmtree(profile)
        except FileNotFoundError:
            print(f"Unable to remove directory {profile}. Path not found.")
        except OSError as e:
            print(f"Error removing directory: {e}")

def remove_nix_store():
    print("Removing Nix store ...")
    instance = subprocess.run([ "diskutil", "apfs", "deleteVolume", "/nix" ], capture_output=True, text=True)
    if instance.returncode != 0:
        if instance.stderr.startswith("Could not find APFS Volume /nix"):
            print("Nix store has been removed ... skipped")
        else:
            print(f"Unable to remove nix store.\n{instance.stderr}")

if __name__ == "__main__":
    print ("Uninstalling Nix ...")
    for profile_name in [ "/etc/bashrc", "/etc/zshrc", "/etc/bash.bashrc" ]:
        remove_nix_block_from_profile(profile_name)
    for daemon_file in [ "/Library/LaunchDaemons/org.nixos.nix-daemon.plist", "/Library/LaunchDaemons/org.nixos.darwin-store.plist" ]:
        remove_daemon(daemon_file)
    remove_nix_groups_and_users()
    remove_fstab()
    remove_profiles()
    remove_nix_store()
