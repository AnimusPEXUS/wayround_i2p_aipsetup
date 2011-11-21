import re

res_to_id = {
    r'http://.*': 'http',
    r'https://.*': 'https',
    r'ftp://.*': 'ftp',
    r'sftp://.*': 'sftp',
    r'sshfs://.*': 'sshfs',
    r'': 'fs',
    }

class AipSetupRepository:
    
    def __init__(self):
        self.scheme = 'error'
        pass

    def connect(self, resource):
        'returns 0 on Ok or 1 on not ok :-) '
        self.scheme = 'error'

        for i in res_to_id.keys():
            if re.match(i, resource) != None:
                self.scheme = res_to_id[i]

        if self.scheme != 'fs':
            print 'not implimented'
            return 1
        return 0
                

    def ls(self):
        pass

    def mkdir(self, name):
        pass

    def rmdir(self, name):
        pass

    def mv(self, name, newname):
        pass

    def cp(self, name, newname):
        pass

    def rm(self, name):
        pass

    def touch(self, name):
        pass

    def cat(self, name):
        pass

    def dd(self, name, newname, bs, count, seek, skip):
        pass

