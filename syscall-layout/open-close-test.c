#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

int main() {
    char *filename = "hello.txt";
    char buffer[1024];
    int fd = open(filename, O_RDONLY);
    int size = 0;
    if (fd == -1) {
        printf("Error in open: errno=%d.\n", errno);
    } else {
        printf("open() successful.\n");
        do {
            size = read(fd, buffer, 1024);
            printf("Read: %d bytes.\n", size);
            if (size == -1) {
                printf("Error in read: errno=%d.\n", errno);
                break;
            }
            buffer[size] = '\0';
            printf("%s", buffer);
          } while(size > 0);
      if (close(fd))
          printf("Error in close: errno=%d.\n", errno);
      else
          printf("close() successful.\n");
    }
    return 0;
}
