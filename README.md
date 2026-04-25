# PvZ Fusion Translation Tool

A utility designed to help manage and compare,translation files for **Plants vs. Zombies Fusion** mods.  
This tool provides automated comparison, validation, and GitHub sync features to streamline localization workflows.

## Features
- **String & Regex Comparison**: Detect differences between dumps and translation files.
- **Almanac Tools**:
  - Compare missing entries for plants and zombies.
  - Validate symbols and formatting in translation files.
- **Travel Buffs Comparison**: Check consistency between dumps and localization.
- **String Checker**: Scan all translation files for issues.
- **Blacklist Management**: Exclude specific files from GitHub sync.
- **GitHub Sync**: Copy updated localization files into your repository while respecting blacklist rules.
- **Update Checker**: Detect new `.pyz` releases and show changelog highlights.

## Requirements
- **Recommended**: Python 3.12 or newer  
- Dependencies:
  - `requests`
  - `packaging` (or use built-in version parser fallback)
- Works on Windows, Linux, and macOS.

## Installation
1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or
   ```bash
   py -m pip install -r requirements.txt
   ```
3. Place .pyz file in Game Files => Util (make a new folder)

Made with **100% Python**
