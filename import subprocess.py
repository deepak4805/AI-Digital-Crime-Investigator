import subprocess
import re

def get_saved_wifi_passwords():
    output = subprocess.check_output(
        ["netsh", "wlan", "show", "profiles"],
        text=True, encoding="utf-8", errors="ignore"
    )

    profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)

    for profile in profiles:
        profile = profile.strip()

        details = subprocess.check_output(
            ["netsh", "wlan", "show", "profile", profile, "key=clear"],
            text=True, encoding="utf-8", errors="ignore"
        )

        password_match = re.search(r"Key Content\s*:\s*(.*)", details)
        password = password_match.group(1).strip() if password_match else "No password"

        print(f"Wi-Fi: {profile}")
        print(f"Password: {password}")
        print("-" * 40)

if __name__ == "__main__":
    get_saved_wifi_passwords()
    