from os import path, remove
from shutil import copyfile
from rominfo import DISK_FILES, IMAGES
from romtools.disk import Disk, FileNotFoundError, FileFormatNotSupportedError, ReadOnlyDiskError, HARD_DISK_FORMATS
from romtools.patch import Patch, PatchChecksumError

def patch(sysDisk, opDisk=None, diskA=None, diskB=None, path_in_disk=None, backup_folder='./backup', speedhack=False):
    # HDIs just have the one disk, received as the arg sysDisk.
    if not opDisk and not diskA and not diskB:
        disks = [sysDisk, sysDisk, sysDisk, sysDisk]
    elif opDisk and diskA and diskB:
        disks = [sysDisk, opDisk, diskA, diskB]
    else:
        raise Exception # TODO: Gotta be something better than this

    for disk_index, d in enumerate(DISK_FILES):
        try:
            RustyDiskOriginal = Disk(disks[disk_index], backup_folder=backup_folder)
        except FileFormatNotSupportedError as e:
            return "File format not supported"


        disk_dir = path.dirname(disks[disk_index])
        if len(disk_dir) == 0:
            disk_dir = '.'

        #disk_format = disks[disk_index].split('.')[-1].lower()

        # Don't want to backup the HDI multiple times, but do want to backup all floppies.
        if RustyDiskOriginal.extension not in HARD_DISK_FORMATS or disk_index == 0:
            RustyDiskOriginal.backup()

        print(d)

        # Opening disk in FDI presents some unique issues.
        # Need to do all the patching in a batch so there's enough room in the disk.
        if disk_index == 1 and RustyDiskOriginal.extension not in HARD_DISK_FORMATS: 
            for f in d:
                try:
                    RustyDiskOriginal.extract(f, path_in_disk, fallback_path='RUSTY')
                except FileNotFoundError:
                    RustyDiskOriginal.restore_from_backup()
                    return "File %s not found in disk.\nTry setting the path under 'Advanced'." % f

                patch_filename = f.replace('.', '_FD.') + '.xdelta'
                patch_filepath = path.join('patch', patch_filename)

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


            print("Entering delete loop")
            for f in d:
                print("Deleting %s from disk", f)
                extracted_file_path = disk_dir + '\\' + f
                RustyDiskOriginal.delete(extracted_file_path, path_in_disk, fallback_path='RUSTY')

            print("Entering insert loop")
            for f in d:
                print("Inserting %s into disk", f)
                extracted_file_path = disk_dir + '\\' + f
                RustyDiskOriginal.insert(extracted_file_path, path_in_disk, delete_original=False, fallback_path='RUSTY')
                remove(extracted_file_path)
                remove(extracted_file_path + '_edited')

            continue

        # All other cases
        for f in d:
            print(f)
            try:
                fallback_necessary = RustyDiskOriginal.check_fallback(f, path_in_disk, fallback_path='RUSTY')
                RustyDiskOriginal.extract(f, path_in_disk, fallback_path='RUSTY')
            except FileNotFoundError:
                RustyDiskOriginal.restore_from_backup()
                return "File %s not found in disk.\nTry setting the path under 'Advanced'." % f

            if f in IMAGES and RustyDiskOriginal.extension in HARD_DISK_FORMATS:
                print("It's an HDI, so using a different %s patch" % f)
                patch_filename = f.replace('.', '_HD.') + '.xdelta'
                patch_filepath = path.join('patch', patch_filename)
            elif f in IMAGES:
                print("It's a floppy, so using the floppy patch for %s" % f)
                patch_filename = f.replace('.', '_FD.') + '.xdelta'
                patch_filepath = path.join('patch', patch_filename)
            elif f == 'VISUAL.COM' and speedhack:
                patch_filename = f.replace('.', '_speedhack.') + '.xdelta'
                patch_filepath = path.join('patch', patch_filename)
            else:
                patch_filepath = path.join('patch', f + '.xdelta')

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

            try:
                if fallback_necessary:
                    RustyDiskOriginal.insert(extracted_file_path, path_in_disk='RUSTY', fallback_path='.')
                else:
                    RustyDiskOriginal.insert(extracted_file_path, path_in_disk, fallback_path='RUSTY')
            except ReadOnlyDiskError:
                remove(extracted_file_path)
                remove(extracted_file_path + '_edited')
                return "Can't write to disk %s. Make sure it's not read-only." % disks[disk_index]
            remove(extracted_file_path)
            remove(extracted_file_path + '_edited')

    return None

if __name__ == '__main__':
    #print patch('rusty.hdi', path_in_disk='RUSTY\\')
    print(patch('Rusty.hdi', speedhack=False))
    #print patch('Rusty (System disk).hdm', 'Rusty (Opening disk).hdm', 'Rusty (Game disk A).hdm', 'Rusty (Game disk B).hdm')
    # The patcher GUI should try the other path_in_disk if the first one doesn't work.
