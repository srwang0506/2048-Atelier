#!/usr/bin/env python3
"""Check project references, scheme, icon sizes, and native device settings."""
import json
import plistlib
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parent.parent
project = json.loads(subprocess.check_output(['plutil', '-convert', 'json', '-o', '-', str(root / 'Lumina.xcodeproj/project.pbxproj')]))
objects = project['objects']
targets = [item for item in objects.values() if item['isa'] == 'PBXNativeTarget']
assert len(targets) == 1 and targets[0]['productType'] == 'com.apple.product-type.application'
for item in objects.values():
    if item['isa'] == 'PBXBuildFile':
        assert (item.get('fileRef') or item.get('productRef')) in objects
    if item['isa'] == 'PBXFileReference' and item['sourceTree'] == '<group>':
        assert (root / 'App' / item['path']).exists(), item['path']
    if item['isa'] == 'XCBuildConfiguration' and 'TARGETED_DEVICE_FAMILY' in item['buildSettings']:
        assert item['buildSettings']['TARGETED_DEVICE_FAMILY'] == '1,2'
        assert item['buildSettings']['SUPPORTED_PLATFORMS'] == 'iphoneos iphonesimulator'
actual = {path.name for path in (root / 'App').glob('*.swift')}
referenced = {item['path'] for item in objects.values() if item['isa'] == 'PBXFileReference' and item.get('lastKnownFileType') == 'sourcecode.swift'}
assert actual == referenced, (actual, referenced)
info = plistlib.loads((root / 'App/Info.plist').read_bytes())
assert not info.get('UIRequiresFullScreen', False), 'iPad multitasking must remain enabled'
assert len(info['UISupportedInterfaceOrientations~ipad']) == 4
privacy = plistlib.loads((root / 'App/PrivacyInfo.xcprivacy').read_bytes())
assert privacy['NSPrivacyTracking'] is False
scheme = ET.parse(root / 'Lumina.xcodeproj/xcshareddata/xcschemes/Lumina.xcscheme')
for item in scheme.iter('BuildableReference'):
    assert item.attrib['BlueprintIdentifier'] in objects
icons = root / 'App/Assets.xcassets/AppIcon.appiconset'
for image in json.loads((icons / 'Contents.json').read_text())['images']:
    data = (icons / image['filename']).read_bytes()
    width, height = struct.unpack('>II', data[16:24])
    expected = float(image['size'].split('x')[0]) * float(image['scale'].rstrip('x'))
    assert width == height == expected
    assert data[25] == 2, 'App icon must be RGB without alpha'
assert not any('WebView' in path.read_text() or 'WKWeb' in path.read_text() for path in (root / 'App').glob('*.swift'))
print(f'Native project validated: {len(actual)} Swift files, iPhone + iPad, icons, local Swift package, privacy manifest.')
