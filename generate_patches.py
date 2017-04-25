import os
import shutil
from rominfo import FILES, IMAGES, SRC_DISK_PATH, DEST_DISK_PATH
from romtools.disk import Disk
from romtools.patch import Patch

RustyDiskOriginal = Disk(SRC_DISK_PATH)
RustyDiskEdited = Disk(DEST_DISK_PATH)

for f in FILES:
    RustyDiskEdited.extract('RUSTY\\' + f, dest_path=os.curdir)
    shutil.copyfile(f, 'edited_' + f)
    RustyDiskOriginal.extract('RUSTY\\' + f, dest_path=os.curdir)

    patch_filename = f + '.xdelta'
    patch_destination = os.path.join('patch', patch_filename)
    filepatch = Patch(f, patch_destination, edited='edited_' + f)
    filepatch.create()

    if f == 'VISUAL.COM':
        # (Just floating free in the root directory, not a great look.)
        speedhack_edited_file ='VISUAL_speedhack.COM'
        patch_filename = 'VISUAL_speedhack.COM.xdelta'
        patch_destination = os.path.join('patch', patch_filename)
        filepatch = Patch(f, patch_filename, edited=speedhack_edited_file)
        filepatch.create()

    os.remove(f)
    os.remove('edited_' + f)

# Get the VISUAL speedhack version as well.

# Separate patches for the FD and HD images.
# FD intro images are all smaller, and lack roles for the credits.
# 
for img in IMAGES:
    RustyDiskOriginal.extract('RUSTY\\' + img, dest_path=os.curdir)
    for version in ('FD', 'HD'):
        version_img_path = os.path.join('patched', version + '_images', img)
        patch_filename = img.replace('.', '_%s.' % version) + '.xdelta'    # STAFF1.MAG -> STAFF1_FD.MAG.xdelta
        patch_destination = os.path.join('patch', patch_filename)
        filepatch = Patch(img, patch_destination, edited=version_img_path)
        filepatch.create()
    os.remove(img)


"""
disk_enum = ['46 Okunen Monogatari - The Sinkaron (J) A user.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 2.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 3.FDI',
                '46 Okunen Monogatari - The Sinkaron (J) B 4.FDI']
for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
    ImgDisk = Disk(disk_enum[i])
    print ImgDisk
    for img in disk:
        original_file = os.path.join('original_roms', 'gdt', img)
        edited_file = os.path.join('typeset_roms', 'gdt', img)
        patch_filename = os.path.join('patch', img + '.xdelta')
        imagepatch = Patch(original_file, patch_filename, edited=edited_file)
        imagepatch.create()

"""

"""

# sets: FDI, d88, NK HDM, NK HDI
set_dirs = ['', 'd88', 'NeoKobe', 'NeoKobe']

sets = (['46 Okunen Monogatari - The Sinkaron (J) A user.FDI', '46 Okunen Monogatari - The Sinkaron (J) B 2.FDI',
         '46 Okunen Monogatari - The Sinkaron (J) B 3.FDI', '46 Okunen Monogatari - The Sinkaron (J) B 4.FDI'],
        ['46okumus.D88', '46okumd1.D88', '46okumd2.D88', '46okumd3.D88'],
        ['46 Okunen Monogatari - The Shinkaron (Disk 1 - User disk).hdm', '46 Okunen Monogatari - The Shinkaron (Disk 2).hdm',
        '46 Okunen Monogatari - The Shinkaron (Disk 3).hdm', '46 Okunen Monogatari - The Shinkaron (Disk 4).hdm'],
        ['46 Okunen Monogatari - The Shinkaron.hdi',],
       )

for i, s in enumerate(sets):
    set_original_dir = os.path.join(ORIGINAL_PATH, set_dirs[i])
    set_patched_dir = os.path.join(TYPESET_PATH, set_dirs[i])
    for disk in s:
        original = os.path.join(set_original_dir, disk)
        patched = os.path.join(set_patched_dir, disk)
        print original
        print patched

        patch_filename = os.path.join('patch', disk + '.xdelta')
        FullDiskPatch = Patch(original, patch_filename, edited=patched)
        FullDiskPatch.create()

floppy_46_path = os.path.join(ORIGINAL_PATH, '46.EXE')
hacked_and_patched_46_path = os.path.join(TYPESET_PATH, 'HDI_patched_46', '46.EXE')
print floppy_46_path
print hacked_and_patched_46_path
FtoH_46_patch_path = os.path.join('patch', 'FtoH_46.EXE' + '.xdelta')
FtoH46Patch = Patch(floppy_46_path, FtoH_46_patch_path, edited=hacked_and_patched_46_path)
FtoH46Patch.create()

"""