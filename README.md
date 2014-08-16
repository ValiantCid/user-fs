# user-fs
A file system for getting user information

## Usage
`user-fs.py mountpoint`  
This will mount the filesystem to `mountpoint`.

## Requirements
This requires that you have FUSE installed and that you're running on a unix-based system. User-FS relies heavily on the `pwd` and `grp` python libraries which are unix dependant.
