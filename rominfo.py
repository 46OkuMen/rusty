import os

# TODO: I really should just make a "Settings" object for this.

SRC_DISK_DIR = 'original\\'
SRC_DISK_PATH = 'original\\rusty.hdi'

DEST_DISK_DIR = 'patched\\'
DEST_DISK_PATH = 'patched\\rusty.hdi'

FILES = ['JO.EXE', 'OP.COM', 'VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM', 'STORY4.COM',
         'STORY5.COM', 'STORY6.COM', 'STORY7.COM', 'STORY8.COM', 'STORY9.COM',
         'STORY10.COM', 'ENEMY1.COM', 'ENEMY4.COM', 'ENEMY9.COM', 'ENEMY10.COM']

FILE_BLOCKS = {'VISUAL.COM': [(0x6d9, 0x140f),  # vs1
                              (0x14cd, 0x17ef), # vs2
                              (0x1899, 0x1971), # vs3
                              (0x1a7e, 0x1dc2), # vs4
                              (0x1ea4, 0x21ec), # vs5
                              (0x22ad, 0x288d), # vs6
                              (0x2a7f, 0x2d11), # ending1
                              (0x2d52, 0x2ff5),], # ending2]

               'OP.COM': [(0x55b, 0x646),], # not compressed; not sure what it is
               # (joke messages about being really hungry, among others)
               'JO.EXE':     [(0xba5, 0xc01),
                              (0x6c23, 0x6cb8),
                              (0x6cd3, 0x6cee), # main menu, options
               	          (0x6d5a, 0x6d83),
                              (0x6d99, 0x6db5),
               	          (0x6e96, 0x6ebe),
                              (0x6ed4, 0x6ef0),
               	          (0x6f7e, 0x6fa9),
                              (0x6fb3, 0x6fc7),
                              (0x6fea, 0x7022),
                              (0x7aa5, 0x7ab4),],

			'STORY1.COM': [(0x32a2, 0x346f),],
               'STORY2.COM': [(0x3490, 0x35ba),],
               'STORY3.COM': [(0x3584, 0x3789),],
               'STORY4.COM': [(0x28b1, 0x2979),],
               'STORY5.COM': [(0x3640, 0x37bd),],
               'STORY6.COM': [(0x1cd3, 0x1e43),],
               'STORY7.COM': [(0x226c, 0x22f7),],
               'STORY8.COM': [(0x1eb0, 0x1fed),],
               'STORY9.COM': [(0x32aa, 0x3650),],
               'STORY10.COM': [(0x258e, 0x2936),],
               # STORY text shows up after boss fights.

               # ENEMY text shows up before some boss fights.
               'ENEMY1.COM': [(0x4503, 0x4561),],
               # enemy2.com has no text?
               # enemy3.com also has no text?
               'ENEMY4.COM': [(0x41a9, 0x4444),],
               # enemy5.com has no text
               # enemy6.com has no text
               # enemy7 has no text
               # enemy8 has no text
               'ENEMY9.COM': [(0x4129, 0x4206),],
               'ENEMY10.COM': [(0x403f, 0x44ef),],
               }