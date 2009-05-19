# Copyright (c) 2008 Giorgos Verigakis <verigak@gmail.com>
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import division

from ctypes import *
from ctypes.util import find_library
from errno import EFAULT
from functools import partial
from platform import machine, system
from traceback import print_exc


class c_timespec(Structure):
    _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]

class c_utimbuf(Structure):
    _fields_ = [('actime', c_timespec), ('modtime', c_timespec)]

class c_stat(Structure):
    pass    # Platform dependent

_system = system()
if _system == 'Darwin':
    _libiconv = CDLL(find_library("iconv"), RTLD_GLOBAL)     # libfuse dependency
    ENOTSUP = 45
    c_dev_t = c_int32
    c_fsblkcnt_t = c_ulong
    c_fsfilcnt_t = c_ulong
    c_gid_t = c_uint32
    c_mode_t = c_uint16
    c_off_t = c_int64
    c_pid_t = c_int32
    c_uid_t = c_uint32
    setxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte),
        c_size_t, c_int, c_uint32)
    getxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte),
        c_size_t, c_uint32)
    c_stat._fields_ = [
        ('st_dev', c_dev_t),
        ('st_ino', c_uint32),
        ('st_mode', c_mode_t),
        ('st_nlink', c_uint16),
        ('st_uid', c_uid_t),
        ('st_gid', c_gid_t),
        ('st_rdev', c_dev_t),
        ('st_atimespec', c_timespec),
        ('st_mtimespec', c_timespec),
        ('st_ctimespec', c_timespec),
        ('st_size', c_off_t),
        ('st_blocks', c_int64),
        ('st_blksize', c_int32)]
elif _system == 'Linux':
    ENOTSUP = 95
    c_dev_t = c_ulonglong
    c_fsblkcnt_t = c_ulonglong
    c_fsfilcnt_t = c_ulonglong
    c_gid_t = c_uint
    c_mode_t = c_uint
    c_off_t = c_longlong
    c_pid_t = c_int
    c_uid_t = c_uint
    setxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte), c_size_t, c_int)
    getxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte), c_size_t)
    
    _machine = machine()
    if _machine == 'i686':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('__pad1', c_ushort),
            ('__st_ino', c_ulong),
            ('st_mode', c_mode_t),
            ('st_nlink', c_uint),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2', c_ushort),
            ('st_size', c_off_t),
            ('st_blksize', c_long),
            ('st_blocks', c_longlong),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec),
            ('st_ino', c_ulonglong)]
    elif machine() == 'x86_64':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', c_ulong),
            ('st_nlink', c_ulong),
            ('st_mode', c_mode_t),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('__pad0', c_int),
            ('st_rdev', c_dev_t),
            ('st_size', c_off_t),
            ('st_blksize', c_long),
            ('st_blocks', c_long),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
    else:
        raise NotImplementedError('Linux %s is not supported.' % _machine)
else:
    raise NotImplementedError('%s is not supported.' % _system)


class c_statvfs(Structure):
    _fields_ = [
        ('f_bsize', c_ulong),
        ('f_frsize', c_ulong),
        ('f_blocks', c_fsblkcnt_t),
        ('f_bfree', c_fsblkcnt_t),
        ('f_bavail', c_fsblkcnt_t),
        ('f_files', c_fsfilcnt_t),
        ('f_ffree', c_fsfilcnt_t),
        ('f_favail', c_fsfilcnt_t)]

class fuse_file_info(Structure):
    _fields_ = [
        ('flags', c_int),
        ('fh_old', c_ulong),
        ('writepage', c_int),
        ('direct_io', c_uint, 1),
        ('keep_cache', c_uint, 1),
        ('flush', c_uint, 1),
        ('padding', c_uint, 29),
        ('fh', c_uint64),
        ('lock_owner', c_uint64)]

class fuse_context(Structure):
    _fields_ = [
        ('fuse', c_voidp),
        ('uid', c_uid_t),
        ('gid', c_gid_t),
        ('pid', c_pid_t),
        ('private_data', c_voidp)]

class fuse_operations(Structure):
    _fields_ = [
        ('getattr', CFUNCTYPE(c_int, c_char_p, POINTER(c_stat))),
        ('readlink', CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t)),
        ('getdir', c_voidp),    # Deprecated, use readdir
        ('mknod', CFUNCTYPE(c_int, c_char_p, c_mode_t, c_dev_t)),
        ('mkdir', CFUNCTYPE(c_int, c_char_p, c_mode_t)),
        ('unlink', CFUNCTYPE(c_int, c_char_p)),
        ('rmdir', CFUNCTYPE(c_int, c_char_p)),
        ('symlink', CFUNCTYPE(c_int, c_char_p, c_char_p)),
        ('rename', CFUNCTYPE(c_int, c_char_p, c_char_p)),
        ('link', CFUNCTYPE(c_int, c_char_p, c_char_p)),
        ('chmod', CFUNCTYPE(c_int, c_char_p, c_mode_t)),
        ('chown', CFUNCTYPE(c_int, c_char_p, c_uid_t, c_gid_t)),
        ('truncate', CFUNCTYPE(c_int, c_char_p, c_off_t)),
        ('utime', c_voidp),     # Deprecated, use utimens
        ('open', CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))),
        ('read', CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t, c_off_t,
            POINTER(fuse_file_info))),
        ('write', CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t, c_off_t,
            POINTER(fuse_file_info))),
        ('statfs', CFUNCTYPE(c_int, c_char_p, POINTER(c_statvfs))),
        ('flush', CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))),
        ('release', CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))),
        ('fsync', CFUNCTYPE(c_int, c_char_p, c_int, POINTER(fuse_file_info))),
        ('setxattr', setxattr_t),
        ('getxattr', getxattr_t),
        ('listxattr', CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t)),
        ('removexattr', CFUNCTYPE(c_int, c_char_p, c_char_p)),
        ('opendir', CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))),
        ('readdir', CFUNCTYPE(c_int, c_char_p, c_voidp, CFUNCTYPE(c_int, c_voidp,
            c_char_p, POINTER(c_stat), c_off_t), c_off_t, POINTER(fuse_file_info))),
        ('releasedir', CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))),
        ('fsyncdir', CFUNCTYPE(c_int, c_char_p, c_int, POINTER(fuse_file_info))),
        ('init', c_voidp),      # Use __init__
        ('destroy', c_voidp),   # Use __del__
        ('access', CFUNCTYPE(c_int, c_char_p, c_int)),
        ('create', CFUNCTYPE(c_int, c_char_p, c_mode_t, POINTER(fuse_file_info))),
        ('ftruncate', CFUNCTYPE(c_int, c_char_p, c_off_t, POINTER(fuse_file_info))),
        ('fgetattr', CFUNCTYPE(c_int, c_char_p, POINTER(c_stat),
            POINTER(fuse_file_info))),
        ('lock', CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info), c_int, c_voidp)),
        ('utimens', CFUNCTYPE(c_int, c_char_p, POINTER(c_utimbuf))),
        ('bmap', CFUNCTYPE(c_int, c_char_p, c_size_t, POINTER(c_ulonglong)))]


_libfuse = CDLL(find_library("fuse"))

def fuse_get_context():
    """Returns a (uid, gid, pid) tuple"""
    p = _libfuse.fuse_get_context()
    ctx = cast(p, POINTER(fuse_context)).contents
    return ctx.uid, ctx.gid, ctx.pid


def time_of_timespec(ts):
    return ts.tv_sec + 1.0 * ts.tv_nsec / 10 ** 9

def _operation_wrapper(func, *args, **kwargs):
    """Decorator for the methods of class FUSE"""
    try:
        return func(*args, **kwargs) or 0
    except OSError, e:
        return -(e.errno or e.message or EFAULT)
    except:
        print_exc()
        return -EFAULT

class FUSE(object):
    """Assumes API version 2.6 or later.
       Should not be subclassed under normal use."""
    
    def __init__(self, operations, mountpoint, **kwargs):
        self.operations = operations
        args = ['fuse']
        if kwargs.pop('foreground', False):
            args.append('-f')
        if kwargs.pop('debug', False):
            args.append('-d')
        if kwargs.pop('nothreads', False):
            args.append('-s')
        kwargs.setdefault('fsname', operations.__class__.__name__)
        args.append('-o')
        args.append(','.join(key if val == True else '%s=%s' % (key, val)
            for key, val in kwargs.items()))
        args.append(mountpoint)
        argv = (c_char_p * len(args))(*args)
        
        fuse_ops = fuse_operations()
        for name, prototype in fuse_operations._fields_:
            if prototype != c_voidp and getattr(operations, name, None):
                op = partial(_operation_wrapper, getattr(self, name))
                setattr(fuse_ops, name, prototype(op))
        _libfuse.fuse_main_real(len(args), argv, pointer(fuse_ops),
            sizeof(fuse_ops), None)
        del self.operations     # Invoke the destructor
        
    def getattr(self, path, buf):
        return self.fgetattr(path, buf, None)
    
    def readlink(self, path, buf, bufsize):
        ret = self.operations('readlink', path)
        memmove(buf, create_string_buffer(ret), bufsize)
        return 0
    
    def mknod(self, path, mode, dev):
        return self.operations('mknod', path, mode, dev)
    
    def mkdir(self, path, mode):
        return self.operations('mkdir', path, mode)
    
    def unlink(self, path):
        return self.operations('unlink', path)
    
    def rmdir(self, path):
        return self.operations('rmdir', path)
    
    def symlink(self, source, target):
        return self.operations('symlink', target, source)
    
    def rename(self, old, new):
        return self.operations('rename', old, new)
    
    def link(self, source, target):
        return self.operations('link', target, source)
    
    def chmod(self, path, mode):
        return self.operations('chmod', path, mode)
    
    def chown(self, path, uid, gid):
        return self.operations('chown', path, uid, gid)
    
    def truncate(self, path, length):
        return self.operations('truncate', path, length)
    
    def open(self, path, fi):
        fi.contents.fh = self.operations('open', path, fi.contents.flags)
        return 0
    
    def read(self, path, buf, size, offset, fi):
        ret = self.operations('read', path, size, offset, fi.contents.fh)
        if ret:
            memmove(buf, create_string_buffer(ret), size)
        return len(ret)
    
    def write(self, path, buf, size, offset, fi):
        data = string_at(buf, size)
        return self.operations('write', path, data, offset, fi.contents.fh)
    
    def statfs(self, path, buf):
        stv = buf.contents
        attrs = self.operations('statfs', path)
        for key, val in attrs.items():
            if hasattr(stv, key):
                setattr(stv, key, val)
        return 0
    
    def flush(self, path, fi):
        return self.operations('flush', path, fi.contents.fh)
    
    def release(self, path, fi):
        return self.operations('release', path, fi.contents.fh)
    
    def fsync(self, path, datasync, fi):
        return self.operations('fsync', path, datasync, fi.contents.fh)
    
    def setxattr(self, path, name, value, size, options, *args):
        s = string_at(value, size)
        return self.operations('setxattr', path, name, s, options, *args)
    
    def getxattr(self, path, name, value, size, *args):
        ret = self.operations('getxattr', path, name, *args)
        buf = create_string_buffer(ret)
        if bool(value):
            memmove(value, buf, size)
        return len(ret)
    
    def listxattr(self, path, namebuf, size):
        ret = self.operations('listxattr', path)
        if not ret:
            return 0
        buf = create_string_buffer('\x00'.join(ret))
        if bool(namebuf):
            memmove(namebuf, buf, size)
        return len(buf)
    
    def removexattr(self, path, name):
        return self.operations('removexattr', path, name)
    
    def opendir(self, path, fi):
        fi.contents.fh = self.operations('opendir', path)
        return 0
    
    def readdir(self, path, buf, filler, offset, fi):
        for name in self.operations('readdir', path, fi.contents.fh):
            filler(buf, name, None, 0)
        return 0
    
    def releasedir(self, path, fi):
        return self.operations('releasedir', path, fi.contents.fh)
    
    def fsyncdir(self, path, datasync, fi):
        return self.operations('fsyncdir', path, datasync, fi.contents.fh)
        
    def access(self, path, amode):
        return self.operations('access', path, amode)
    
    def create(self, path, mode, fi):
        fi.contents.fh = self.operations('create', path, mode)
        return 0
    
    def ftruncate(self, path, length, fi):
        return self.operations('truncate', path, length, fi.contents.fh)
    
    def fgetattr(self, path, buf, fi):
        memset(buf, 0, sizeof(c_stat))
        st = buf.contents
        fh = fi.contents.fh if fi else None
        attrs = self.operations('getattr', path, fh)
        for key, val in attrs.items():
            if key in ('st_atime', 'st_mtime', 'st_ctime'):
                timespec = getattr(st, key + 'spec')
                timespec.tv_sec = int(val)
                timespec.tv_nsec = int((val - timespec.tv_sec) * 10 ** 9)
            elif hasattr(st, key):
                setattr(st, key, val)
        return 0
    
    def lock(self, path, fi, cmd, lock):
        return self.operations('lock', path, fi.contents.fh, cmd, lock)
    
    def utimens(self, path, buf):
        if buf:
            atime = time_of_timespec(buf.contents.actime)
            mtime = time_of_timespec(buf.contents.modtime)
            times = (atime, mtime)
        else:
            times = None
        return self.operations('utimens', path, times)
    
    def bmap(self, path, blocksize, idx):
        return self.operations('bmap', path, blocksize, idx)


from errno import EACCES, ENOENT
from stat import S_IFDIR

class Operations:
    """This class should be subclassed and passed as an argument to FUSE on
       initialization. All operations should raise an OSError exception on
       error.
       
       When in doubt of what an operation should do, check the FUSE header
       file or the corresponding system call man page."""
    
    def __call__(self, op, *args):
        if not hasattr(self, op):
            raise OSError(EFAULT)
        return getattr(self, op)(*args)
        
    def access(self, path, amode):
        return 0
    
    bmap = None
    
    def chmod(self, path, mode):
        raise OSError(EACCES)
    
    def chown(self, path, uid, gid):
        raise OSError(EACCES)
    
    def create(self, path, mode):
        """Returns a numerical file handle."""
        raise OSError(EACCES)
        
    def flush(self, path, fh):
        return 0
    
    def fsync(self, path, datasync, fh):
        return 0
    
    def fsyncdir(self, path, datasync, fh):
        return 0
    
    def getattr(self, path, fh=None):
        """Returns a dictionary with keys identical to the stat C structure
           of stat(2).
           st_atime, st_mtime and st_ctime should be floats."""
        if path != '/':
            raise OSError(ENOENT)
        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
    
    def getxattr(self, path, name, position=0):
        raise OSError(ENOTSUP)
    
    def link(self, target, source):
        raise OSError(EACCES)
    
    def listxattr(self, path):
        return []
        
    lock = None
    
    def mkdir(self, path, mode):
        raise OSError(EACCES)
    
    def mknod(self, path, mode, dev):
        raise OSError(EACCES)
    
    def open(self, path, flags):
        """Returns a numerical file handle."""
        return 0
    
    def opendir(self, path):
        """Returns a numerical file handle."""
        return 0
    
    def read(self, path, size, offset, fh):
        """Returns a string containing the data requested."""
        raise OSError(EACCES)
    
    def readdir(self, path, fh):
        return ['.', '..']
    
    def readlink(self, path):
        raise OSError(EACCES)
    
    def release(self, path, fh):
        return 0
    
    def releasedir(self, path, fh):
        return 0
    
    def removexattr(self, path, name):
        raise OSError(ENOTSUP)
    
    def rename(self, old, new):
        raise OSError(EACCES)
    
    def rmdir(self, path):
        raise OSError(EACCES)
    
    def setxattr(self, path, name, value, options, position=0):
        raise OSError(ENOTSUP)
    
    def statfs(self, path):
        """Returns a dictionary with keys identical to the statvfs C structure
           of statvfs(3). The f_frsize, f_favail, f_fsid and f_flag fields are
           ignored by FUSE though."""
        return {}
    
    def symlink(self, target, source):
        raise OSError(EACCES)
    
    def truncate(self, path, length, fh=None):
        raise OSError(EACCES)
    
    def unlink(self, path):
        raise OSError(EACCES)
    
    def utimens(self, path, times=None):
        """Times is a (atime, mtime) tuple. If None use current time."""
        return 0
    
    def write(self, path, data, offset, fh):
        raise OSError(EACCES)


class LoggingMixIn:
    def __call__(self, op, path, *args):
        print '->', op, path, repr(args)
        ret = '[Unknown Error]'
        try:
            ret = getattr(self, op)(path, *args)
            return ret
        except OSError, e:
            ret = '[Errno %s]' % (e.errno or e.message)
            raise
        finally:
            print '<-', op, repr(ret)