import os.path
import glob
import gzip
import json
# Change Log:
#   Nov 23, 2016    Catherine Wei   Add retrieveJsonFileByName()
#   Sep 09, 2016    Catherine Wei   Change path_factory to not append * and add retrieveJsonFiles
#   Jul 05, 2016    Dean Chan       Added check for .gz and decompressing before streaming to client

_temp_storage_path = "/data/ngs-upload/"
_storage_path = "/mnt/ng_sequences/brave-ngs-storage"
#_temp_storage_path = "/Users/dchan/Programming/Brave/ngs_api/ngs-temp"
#_storage_path = "/Users/dchan/Programming/Brave/ngs_api/ngs-uploader"
TOKEN_STORE = {}

def retrieveChunkURLs(storageID):
    storageID = storageID.replace(".", "/")
    searchPath = os.path.join(_storage_path, storageID, "chunk.*")
    paths = glob.glob(searchPath)
    chunkCount = len(paths)
    return [chunkCount, paths]

def retrieveJsonFileByName(storageID, fileName):
    """
    Retrieve content of a single file specified by its full filename

    @param  fileName    full filename
    """
    storageID = storageID.replace(".", "/")
    filepath = os.path.join(_storage_path, storageID, fileName)
    print filepath

    data = False
    if os.path.isfile(filepath):
        print "Trying to open file "+filepath
        with open(filepath, 'r') as filePointer:
            data = json.load(filePointer)

    return data


def retrieveJsonFiles(storageID, filePrefix):
    """
    This function retrieves json files and the chunk file counts, which can be
    used to derive the processing progress of a run.

    @param filePrefix '.' will be added to the end if not already there for the search
    """
    #print "NGS_DAO 29 --"

    ## retrieve chunk count
    storageID = storageID.replace(".", "/")
    searchPath = os.path.join(_storage_path, storageID, "chunk.*")
    #print "NGS_DAO 33 --", searchPath
    paths = [i[len(_storage_path) + 1:] for i in glob.glob(searchPath)]
    #print "NGS_DAO 35 --",  paths
    chunkCount = len(paths)

    ## retrieve target file data
    if not filePrefix.endswith('.'):
        filePrefix += "."
    searchPath = os.path.join(_storage_path, storageID, filePrefix + "*")
    #print "NGS_DAO 42 --", searchPath
    paths = [i[len(_storage_path) + 1:] for i in glob.glob(searchPath)]
    paths.sort()
    #print "NGS_DAO 45 --", paths

    data = []
    for filepath in paths:
        filepath = os.path.join (_storage_path, filepath)
        with open(filepath, 'r') as filePointer:
            data.append (json.load(filePointer))

    return [chunkCount, data]


def path_factory(rel):
    path = "{}".format(os.path.join(_storage_path, rel))
    print path
    # Strip down to rel path
    paths = [i[len(_storage_path) + 1:] for i in glob.glob(path)]
    paths.sort()

    return paths


def is_safe_path(basedir, path, follow_symlinks=False):
    """
    Prevent traversal of arbitrary folders by malicious user input
    https://security.openstack.org/guidelines/dg_using-file-paths.html

    :param basedir:
    :param path:
    :param follow_symlinks:
    :return:
    """
    return os.path.abspath(path).startswith(basedir)


def filename_sanitize(path):
    """Returns a sanitized path or filename that can be written to disk"""
    parts = os.path.split(path)

    # TODO: insert sanitize

    return os.path.join(parts)


def get_storage_path():
    return _storage_path


def get_temp_storage_path():
    return _temp_storage_path


def unsplit(paths):
    """Generator function that reassembles a file from n byte chunks generated by the split command.
    Accept a list of file names."""
    stub = ''
    for f in paths:
        # is f gzip'd?
        if f.endswith('.gz'):
            func = gzip.open
        else:
            func = open

        for line in func(f, 'r'):
            # fastq lines end with a new line, except at the end of a file
            if line[-1] == '\n':
                line = "".join((stub, line, ))
                stub = ''
                yield line
            else:
                # This is a partial line, continue to the next file
                stub = line


class Combine(object):

    def __init__(self, paths):
        self.index = 0
        absp = os.path.join(_storage_path, paths.replace('.', '/'), '*')
        print absp
        self.paths = glob.glob(absp)
        self.paths.sort()
        self.files = len(self.paths)
        print self.paths
        if self.paths[self.index][-3:] == ".gz":
            self.current = gzip.open(self.paths[self.index], 'rb')
        else:
            self.current = open(self.paths[self.index], 'r')
        self.eof = False

    @staticmethod
    def open(paths):
        return Combine(paths)

    def read(self, size=1024**2):
        buf = self.current.read(size)
        if len(buf) < size and self.index < self.files - 1:
            self.index += 1
            self.current.close()
            if self.paths[self.index][-3:] == ".gz":
                self.current = gzip.open(self.paths[self.index], 'rb')
            else:
                self.current = open(self.paths[self.index], 'r')

            buf += self.current.read(size - len(buf))
        else:
            self.eof = True

        return buf

    def next(self):
        buf = self.read()
        if buf == "":
            raise StopIteration

        return buf

    def __iter__(self):
        return self

    def close(self):
        self.current.close()


