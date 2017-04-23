from os import path, remove
from shutil import copyfile
from rominfo import DISK_FILES
from romtools.disk import Disk, FileNotFoundError, UnicodePathError, HARD_DISK_FORMATS
from romtools.patch import Patch, PatchChecksumError

def patch(sysDisk, opDisk=None, diskA=None, diskB=None, path_in_disk=None, backup_folder='./backup'):
    # HDIs just have the one disk, received as the arg sysDisk.
    if not opDisk and not diskA and not diskB:
        disks = [sysDisk, sysDisk, sysDisk, sysDisk]
    elif opDisk and diskA and diskB:
        disks = [sysDisk, opDisk, diskA, diskB]
    else:
        raise Exception # TODO: Gotta be something better than this

    print DISK_FILES

    for disk_index, d in enumerate(DISK_FILES):
        RustyDiskOriginal = Disk(disks[disk_index], backup_folder=backup_folder)
        RustyDiskOriginal.backup()

        disk_dir = path.dirname(disks[disk_index])
        if len(disk_dir) == 0:
            disk_dir = '.'

        disk_format = disks[disk_index].split('.')[-1].lower()


        print d
        for f in d:
            print f
            try:
                RustyDiskOriginal.extract(f, path_in_disk)
            except FileNotFoundError:
                RustyDiskOriginal.restore_from_backup()
                return "File %s not found in disk.\nTry setting the path under 'Advanced'." % f
            except UnicodePathError:
                return "Patching in paths containing non-ASCII characters not supported."

            if f in ('GIRL2A.MAG', 'GIRL7A.MAG') and RustyDiskOriginal.extension.lower() in HARD_DISK_FORMATS:
                print "It's an HDI, so using a different %s patch" % f
                patch_filename = f.replace('.', '_HD.') + '.xdelta'
                patch_filepath = path.join('patch', patch_filename)
            else:
                patch_filepath = path.join('patch', f + '.xdelta')

            print disk_dir
            extracted_file_path = disk_dir + '\\' + f

            copyfile(extracted_file_path, extracted_file_path + '_edited')
            patchfile = Patch(extracted_file_path, patch_filepath, edited=extracted_file_path + '_edited')

            try:
                patchfile.apply()
            except PatchChecksumError:
                RustyDiskOriginal.restore_from_backup()
                remove(extracted_file_path)
                remove(extracted_file_path + '_edited')
                return "Checksum error in file %s." % f
        
            copyfile(extracted_file_path + '_edited', extracted_file_path)

            RustyDiskOriginal.insert(extracted_file_path, path_in_disk)
            remove(extracted_file_path)
            remove(extracted_file_path + '_edited')

    return None

if __name__ == '__main__':
    #print patch('rusty.hdi', path_in_disk='RUSTY\\')
    print patch('Rusty.hdi')
    #print patch('Rusty (System disk).hdm', 'Rusty (Opening disk).hdm', 'Rusty (Game disk A).hdm', 'Rusty (Game disk B).hdm')
    # The patcher GUI should try the other path_in_disk if the first one doesn't work.

    # TODO: Not enough room in the Opening FDI, so need to expand it.
    # Include a 2MB floppy image, then copy all the files into it if it's needed.
        # So, how do I create this 2MB floppy? HDMs max out at 1,232 KB...