/* Native macOS entry point. The game and AI remain entirely Python. */
#include <mach-o/dyld.h>
#include <libgen.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
int main(void) {
    char exe[PATH_MAX], base[PATH_MAX], python[PATH_MAX], game[PATH_MAX], log[PATH_MAX];
    uint32_t n = sizeof(exe);
    if (_NSGetExecutablePath(exe, &n) != 0) return 1;
    char *directory = dirname(exe);
    snprintf(base, sizeof(base), "%s/../../..", directory);
    if (chdir(base) != 0 || !getcwd(base, sizeof(base))) return 2;
    snprintf(python, sizeof(python), "%s/.venv/bin/python", base);
    snprintf(game, sizeof(game), "%s/game.py", base);
    mkdir("data", 0755);
    snprintf(log, sizeof(log), "%s/data/launch.log", base);
    int fd = open(log, O_CREAT | O_WRONLY | O_APPEND, 0644);
    if (fd >= 0) { dup2(fd, STDOUT_FILENO); dup2(fd, STDERR_FILENO); close(fd); }
    execl(python, python, game, (char *)NULL);
    perror("Cannot start the Python runtime; please use 启动游戏.command");
    return 3;
}
