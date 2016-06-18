#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>

int main() {
    struct stat stat_buf;
    int retval = stat("/tmp/", &stat_buf);
    if (retval) {
        printf("Error in stat! errno=%d\n", errno);
    } else {
        printf("Name      \tSize\tLoc\tValue\n");
        printf("------------------------------------------\n");
        printf("st_dev    \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_dev), &stat_buf.st_dev, stat_buf.st_dev);
        printf("st_ino    \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_ino), &stat_buf.st_ino, stat_buf.st_ino);
        printf("st_mode   \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_mode), &stat_buf.st_mode, stat_buf.st_mode);
        printf("st_nlink  \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_nlink), &stat_buf.st_nlink, stat_buf.st_nlink);
        printf("st_uid    \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_uid), &stat_buf.st_uid, stat_buf.st_uid);
        printf("st_gid    \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_gid), &stat_buf.st_gid, stat_buf.st_gid);
        printf("st_size   \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_size), &stat_buf.st_size, stat_buf.st_size);
        printf("st_rdev   \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_rdev), &stat_buf.st_rdev, stat_buf.st_rdev);
        printf("st_size   \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_size), &stat_buf.st_size, stat_buf.st_size);
        printf("st_blksize\t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_blksize), &stat_buf.st_blksize, stat_buf.st_blksize);
        printf("st_blocks \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_blocks), &stat_buf.st_blocks, stat_buf.st_blocks);
        printf("st_atime  \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_atime), &stat_buf.st_atime, stat_buf.st_atime);
        printf("st_mtime  \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_mtime), &stat_buf.st_mtime, stat_buf.st_mtime);
        printf("st_ctime  \t%d\t%x\t%lx\n",
               sizeof(stat_buf.st_ctime), &stat_buf.st_ctime, stat_buf.st_ctime);
    }
    return 0;
}
