// Native macOS application lifecycle. All gameplay and search remain Python.
#import <Cocoa/Cocoa.h>
@interface LuminaLauncher : NSObject <NSApplicationDelegate>
@property(strong) NSTask *game;
@end
@implementation LuminaLauncher
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    NSString *root = [[[NSBundle mainBundle] bundlePath] stringByDeletingLastPathComponent];
    self.game = [NSTask new];
    self.game.executableURL = [NSURL fileURLWithPath:[root stringByAppendingPathComponent:@".venv/bin/python"]];
    self.game.arguments = @[[root stringByAppendingPathComponent:@"game.py"]];
    self.game.currentDirectoryURL = [NSURL fileURLWithPath:root];
    self.game.standardOutput = [NSFileHandle fileHandleWithNullDevice];
    self.game.standardError = [NSFileHandle fileHandleWithNullDevice];
    self.game.terminationHandler = ^(NSTask *task) {
        dispatch_async(dispatch_get_main_queue(), ^{ [NSApp terminate:nil]; });
    };
    NSError *error = nil;
    if (![self.game launchAndReturnError:&error]) {
        NSAlert *alert = [NSAlert new];
        alert.messageText = @"LUMINA 暂时无法启动";
        alert.informativeText = @"请运行同一文件夹中的“启动游戏.command”修复 Python 运行环境。";
        [alert runModal];
        [NSApp terminate:nil];
    }
}
@end
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSApplication *application = [NSApplication sharedApplication];
        __attribute__((objc_precise_lifetime)) LuminaLauncher *delegate = [LuminaLauncher new];
        application.delegate = delegate;
        [application setActivationPolicy:NSApplicationActivationPolicyAccessory];
        [application run];
    }
    return 0;
}
