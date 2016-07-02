#include <stddef.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>

int main() {
    struct stat stat_buf;
    int retval = fstat(1, &stat_buf);
    if (retval) {
        printf("Error in fstat! errno=%d\n", errno);
    } else {
        printf("Name\t\tSize\tLoc\tOffset\tValue\n");
        printf("----------------------------------------------------\n");
        printf("st_dev    \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_dev), &stat_buf.st_dev,
               offsetof(struct stat, st_dev),
               (unsigned short)stat_buf.st_dev);
        printf("st_ino    \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_ino), &stat_buf.st_ino,
               offsetof(struct stat, st_ino),
               (unsigned short)stat_buf.st_ino);
        printf("st_mode   \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_mode), &stat_buf.st_mode,
               offsetof(struct stat, st_mode),
               (unsigned int)stat_buf.st_mode);
        printf("st_nlink  \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_nlink), &stat_buf.st_nlink,
               offsetof(struct stat, st_nlink),
               (unsigned short)stat_buf.st_nlink);
        printf("st_uid    \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_uid), &stat_buf.st_uid,
               offsetof(struct stat, st_uid),
               (unsigned short)stat_buf.st_uid);
        printf("st_gid    \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_gid), &stat_buf.st_gid,
               offsetof(struct stat, st_gid),
               (unsigned short)stat_buf.st_gid);
        printf("st_rdev   \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_rdev), &stat_buf.st_rdev,
               offsetof(struct stat, st_rdev),
               (unsigned short)stat_buf.st_rdev);
        printf("st_size   \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_size), &stat_buf.st_size,
               offsetof(struct stat, st_size),
               (unsigned int)stat_buf.st_size);
        printf("st_atime  \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_atime), &stat_buf.st_atime,
               offsetof(struct stat, st_atime),
               (unsigned int)stat_buf.st_atime);
        printf("st_mtime  \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_mtime), &stat_buf.st_mtime,
               offsetof(struct stat, st_mtime),
               (unsigned int)stat_buf.st_mtime);
        printf("st_ctime  \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_ctime), &stat_buf.st_ctime,
               offsetof(struct stat, st_ctime),
               (unsigned int)stat_buf.st_ctime);
        printf("st_blksize\t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_blksize), &stat_buf.st_blksize,
               offsetof(struct stat, st_blksize),
               (unsigned int)stat_buf.st_blksize);
        printf("st_blocks \t%d\t%p\t%p\t\t%04x\n",
               sizeof(stat_buf.st_blocks), &stat_buf.st_blocks,
               offsetof(struct stat, st_blocks),
               (unsigned int)stat_buf.st_blocks);
      }
    return 0;
}
