from stat import S_IFDIR, S_IFREG
from errno import ENOENT
from sys import argv
from time import time
from fuse import FUSE, Operations, FuseOSError
import re
import pwd
import grp


class UserFUSE(Operations):
    def read(self, path, size, offset, fh):
        encoded = lambda x: ('%s\n' % x).encode('utf-8')

        if path.split('/')[2] == 'uid':
            ret = self._get_uid(path)
        elif path.split('/')[2] == 'grp_name':
            ret = self._get_grp_name(path)
        elif path.split('/')[2] == 'grp_gid':
            ret = self._get_grp_gid(path)
        elif path.split('/')[2] == 'shell':
            ret = self._get_shell(path)
        elif path.split('/')[2] == 'home_dir':
            ret = self._get_homedir(path)
        else:
            raise FuseOSError(ENOENT)

        return encoded(ret)

    def getattr(self, path, fh=None):
        if path == "/":
            st = dict(st_mode=(S_IFDIR | 0555), st_nlink=2)
        elif re.match("^/[a-zA-Z0-9\-]+/[a-zA-Z0-9\-]+", path):
            size = self._get_size_of_file(path)
            st = dict(st_mode=(S_IFREG | 0444),
                      st_size=size)
        elif re.match("^/[a-zA-Z0-9\-]+", path):
            if re.match("^/([a-zA-Z0-9\-]+)", path).group(1) \
                    not in [x[0] for x in pwd.getpwall()]:
                raise FuseOSError(ENOENT)
            st = dict(st_mode=(S_IFDIR | 0555), st_nlink=2)
        else:
            raise FuseOSError(ENOENT)

        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        return st

    def readdir(self, path, fh):
        self._get_users()
        if path == "/":
            ret_readdir = ['.', '..']
            for user in self._get_users():
                ret_readdir.append(user[0])
            return ret_readdir
        elif re.match("^/[a-zA-Z0-9\-]+$", path).group(0):
            return ['.', '..',
                    'uid', 'grp_name', 'grp_gid',
                    'shell', 'home_dir']
        else:
            raise FuseOSError(ENOENT)

    def _get_users(self):
        return pwd.getpwall()

    def _get_uid(self, path):
        return str(pwd.getpwnam(path.split('/')[1])[2])

    def _get_grp_name(self, path):
        return " ".join([g.gr_name for g in grp.getgrall()
                         if path.split('/')[1] in g.gr_mem])

    def _get_grp_gid(self, path):
        return " ".join([str(g.gr_gid) for g in grp.getgrall()
                         if path.split('/')[1] in g.gr_mem])

    def _get_shell(self, path):
        return pwd.getpwnam(path.split('/')[1])[6]

    def _get_homedir(self, path):
        return pwd.getpwnam(path.split('/')[1])[5]

    def _get_size_of_file(self, path):
        if path.split('/')[2] == 'uid':
            size = len(self._get_uid(path))
        elif path.split('/')[2] == 'grp_name':
            size = len(self._get_grp_name(path))
        elif path.split('/')[2] == 'grp_gid':
            size = len(self._get_grp_gid(path))
        elif path.split('/')[2] == 'shell':
            size = len(self._get_shell(path))
        elif path.split('/')[2] == 'home_dir':
            size = len(self._get_homedir(path))
        else:
            raise FuseOSError(ENOENT)

        return size + 1

if __name__ == '__main__':
    if len(argv) < 2:
        print "usage: %s <mountpoint>" % argv[0]
        exit(1)

    fuse = FUSE(UserFUSE(), argv[1], foreground=True, ro=True)