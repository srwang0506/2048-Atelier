#!/usr/bin/env python3
"""Reproducible Xcode project; no third-party generator dependency."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
objects = {}
def ident(key):
    return hashlib.sha1(key.encode()).hexdigest()[:24].upper()
def obj(key, isa, **attrs):
    ref = ident(key)
    objects[ref] = dict(isa=isa, **attrs)
    return ref

sources, apprefs = [], []
for path in sorted((root / 'App').glob('*.swift')):
    ref = obj('ref-' + path.name, 'PBXFileReference', lastKnownFileType='sourcecode.swift', path=path.name, sourceTree='<group>')
    apprefs.append(ref)
    sources.append(obj('build-' + path.name, 'PBXBuildFile', fileRef=ref))
for name, kind in [('Assets.xcassets', 'folder.assetcatalog'), ('PrivacyInfo.xcprivacy', 'text.xml'), ('Info.plist', 'text.plist.xml')]:
    apprefs.append(obj('ref-' + name, 'PBXFileReference', lastKnownFileType=kind, path=name, sourceTree='<group>'))
resources = [obj('build-' + name, 'PBXBuildFile', fileRef=ident('ref-' + name)) for name in ['Assets.xcassets', 'PrivacyInfo.xcprivacy']]
appgroup = obj('app-group', 'PBXGroup', children=apprefs, path='App', sourceTree='<group>')
product = obj('app-product', 'PBXFileReference', explicitFileType='wrapper.application', includeInIndex='0', path='Lumina.app', sourceTree='BUILT_PRODUCTS_DIR')
products = obj('products-group', 'PBXGroup', children=[product], name='Products', sourceTree='<group>')
main = obj('main-group', 'PBXGroup', children=[appgroup, products], sourceTree='<group>')
package = obj('core-package', 'XCLocalSwiftPackageReference', relativePath='.')
dep = obj('core-product', 'XCSwiftPackageProductDependency', package=package, productName='LuminaCore')
framework = obj('build-core', 'PBXBuildFile', productRef=dep)
phases = [obj('sources-phase', 'PBXSourcesBuildPhase', buildActionMask='2147483647', files=sources, runOnlyForDeploymentPostprocessing='0'),
          obj('frameworks-phase', 'PBXFrameworksBuildPhase', buildActionMask='2147483647', files=[framework], runOnlyForDeploymentPostprocessing='0'),
          obj('resources-phase', 'PBXResourcesBuildPhase', buildActionMask='2147483647', files=resources, runOnlyForDeploymentPostprocessing='0')]
configlists = {}
for level in ['project', 'target']:
    configs = []
    for mode in ['Debug', 'Release']:
        settings = dict(SDKROOT='iphoneos', IPHONEOS_DEPLOYMENT_TARGET='16.4', SWIFT_VERSION='5.0', CLANG_ENABLE_MODULES='YES', CLANG_ENABLE_OBJC_ARC='YES', ENABLE_USER_SCRIPT_SANDBOXING='YES', SWIFT_OPTIMIZATION_LEVEL='-Onone' if mode == 'Debug' else '-O', DEBUG_INFORMATION_FORMAT='dwarf' if mode == 'Debug' else 'dwarf-with-dsym', SWIFT_ACTIVE_COMPILATION_CONDITIONS='DEBUG' if mode == 'Debug' else '') if level == 'project' else dict(ASSETCATALOG_COMPILER_APPICON_NAME='AppIcon', ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME='AccentColor', CODE_SIGN_STYLE='Automatic', DEVELOPMENT_TEAM='', CURRENT_PROJECT_VERSION='2', MARKETING_VERSION='1.0.1', GENERATE_INFOPLIST_FILE='NO', INFOPLIST_FILE='App/Info.plist', PRODUCT_BUNDLE_IDENTIFIER='com.sirui.lumina2048', PRODUCT_NAME='$(TARGET_NAME)', TARGETED_DEVICE_FAMILY='1,2', SUPPORTED_PLATFORMS='iphoneos iphonesimulator', SUPPORTS_MACCATALYST='NO', SWIFT_EMIT_LOC_STRINGS='YES', LD_RUNPATH_SEARCH_PATHS=['$(inherited)', '@executable_path/Frameworks'])
        if mode == 'Release':
            settings['SWIFT_COMPILATION_MODE'] = 'wholemodule'
        configs.append(obj(level + '-' + mode, 'XCBuildConfiguration', buildSettings=settings, name=mode))
    configlists[level] = obj(level + '-configs', 'XCConfigurationList', buildConfigurations=configs, defaultConfigurationIsVisible='0', defaultConfigurationName='Release')
target = obj('app-target', 'PBXNativeTarget', buildConfigurationList=configlists['target'], buildPhases=phases, buildRules=[], dependencies=[], name='Lumina', packageProductDependencies=[dep], productName='Lumina', productReference=product, productType='com.apple.product-type.application')
project = obj('project', 'PBXProject', attributes={'BuildIndependentTargetsInParallel': 'YES', 'LastSwiftUpdateCheck': '1640', 'LastUpgradeCheck': '1640', 'TargetAttributes': {target: {'CreatedOnToolsVersion': '16.4', 'ProvisioningStyle': 'Automatic'}}}, buildConfigurationList=configlists['project'], compatibilityVersion='Xcode 14.0', developmentRegion='zh_CN', hasScannedForEncodings='0', knownRegions=['zh_CN', 'en', 'Base'], mainGroup=main, packageReferences=[package], productRefGroup=products, projectDirPath='', projectRoot='', targets=[target])
def encode(value, depth=0):
    if isinstance(value, dict):
        return '{\n' + ''.join('\t' * (depth + 1) + json.dumps(key) + ' = ' + encode(item, depth + 1) + ';\n' for key, item in value.items()) + '\t' * depth + '}'
    if isinstance(value, list):
        return '(' + ', '.join(encode(item, depth + 1) for item in value) + ')'
    return json.dumps(value)
directory = root / 'Lumina.xcodeproj'
(directory / 'xcshareddata/xcschemes').mkdir(parents=True, exist_ok=True)
(directory / 'project.pbxproj').write_text('// !$*UTF8*$!\n' + encode(dict(archiveVersion='1', classes={}, objectVersion='56', objects=objects, rootObject=project)) + '\n')
buildable = f'<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="Lumina.app" BlueprintName="Lumina" ReferencedContainer="container:Lumina.xcodeproj"/>'
(directory / 'xcshareddata/xcschemes/Lumina.xcscheme').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1640" version="1.3">
<BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">{buildable}</BuildActionEntry></BuildActionEntries></BuildAction>
<TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES"><Testables/></TestAction>
<LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0">{buildable}</BuildableProductRunnable></LaunchAction>
<ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"><BuildableProductRunnable runnableDebuggingMode="0">{buildable}</BuildableProductRunnable></ProfileAction>
<AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>''')
print(f'Generated iPhone + iPad project with {len(sources)} Swift files.')
