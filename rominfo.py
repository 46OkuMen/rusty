import os

# TODO: I really should just make a "Settings" object for this.

SRC_DISK_DIR = 'original\\'
SRC_DISK_PATH = 'original\\rusty.hdi'

DEST_DISK_DIR = 'patched\\'
DEST_DISK_PATH = 'patched\\rusty.hdi'

FILES = ['JO.EXE', 'OP.COM', 'VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM', 'STORY4.COM',
         'STORY5.COM', 'STORY6.COM', 'STORY7.COM', 'STORY8.COM', 'STORY9.COM',
         'STORY10.COM', 'ENEMY1.COM', 'ENEMY4.COM', 'ENEMY9.COM', 'ENEMY10.COM']

EDITED_FILES = ['VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM', 'STORY4.COM', 'STORY5.COM', 'STORY6.COM',
                'STORY7.COM', 'STORY8.COM', 'STORY9.COM', 'STORY10.COM', 'ENEMY1.COM', 'ENEMY4.COM',
                'ENEMY9.COM', 'ENEMY10.COM', 'JO.EXE', 'OP.COM', 'GRPEGC.COM', 'GIRL2A.MAG', 'GIRL5A.MAG',
                'GIRL7A.MAG', 'R_A23.MGX', 'R_A31.MGX', 'R_A36.MGX', 'STAFF1.MGX', 'STAFF2.MGX', 'STAFF3.MGX',
                'STAFF4.MGX', 'STAFF5.MGX', 'STAFF6.MGX', 'STAFF7.MGX']

UNCOMPRESSED_FILES = ['JO.EXE', 'OP.COM']

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

CONTROL_CODES = {'[LN]': '\x04\x00\x73',
                 '[SLN]': '\x0d',
                 '[START]': '\x04\x00\x69',
                 '[SCRL]': '\x05\x1e\x0d',
                 '[PAUSE]': '\x05\x1e',
                 '[0514]': '\x05\x14',
                 '[052d]': '\x05\x2d',
                 '[053c]': '\x05\x3c',
                 '[0578]': '\x05\x78',
                 '[050f]': '\x05\x0f',
                 '[1416]': '\x14\x16',
                 '[0308]': '\x03\x08',
                 '[160578]': '\x16\x05\x78',
                 '[012d06]': '\x01\x2d\x06',
                 '[012006]': '\x01\x20\x06',
                 '[012a14]': '\x01\x2a\x14',
                 '[013914]': '\x01\x39\x14',
                 '[01f517]': '\x01\xf5\x17',
                 '[01f017]': '\x01\xf0\x17',
                 '[017b19]': '\x01\x7b\x19',
                 '[019019]': '\x01\x90\x19',
                 '[01bc19]': '\x01\xbc\x19',
                 '[01d119]': '\x01\xd1\x19',
                 '[01f319]': '\x01\xf3\x19',
                 '[01081a]': '\x01\x08\x1a',
                 '[01fc1d]': '\x01\xfc\x1d',
                 '[01d21d]': '\x01\xd2\x01',
                 '[5f4501]': '\x04\xf4\x01',
                 '[01e71d]': '\x01\xe7\x1d',
                 '[012b1e]': '\x01\x2b\x1e',
                 '[01161e]': '\x01\x16\x1e',
                 '[013b29]': '\x01\x3b\x29',
                 '[01db28]': '\x01\xdb\x28',
                 '[019228]': '\x01\x92\x28',
                 '[01c128]': '\x01\xc1\x28',
                 '[1-1d]': '\x01\x1d\x05',
                 '[1-2c]': '\x01\x2c\x05',
                 '[1-77]': '\x01\x77\x05',
                 '[1-86]': '\x01\x86\x05',
                 '[1-9e]': '\x01\x9e\x05',
                 '[1-af]': '\x01\xaf\x05',
                 '[1-c5]': '\x01\xc5\x05',
                 '[1-da]': '\x01\xda\x05',
                 '[F-5f]': '\x0f\x5f\x45',
                 '[F-63]': '\x0f\x63\x45',
                 '[F-6b]': '\x0f\x6b\x45',
                 '[F-67]': '\x0f\x67\x45',
                 '[TXT11-71]': '\x15\x11\x71',
                 '[TXT1a-71]': '\x15\x1a\x71',
                 '[TXT1d-71]': '\x15\x1d\x71',
                 '[TXT1e-71]': '\x15\x1e\x71',
                 '[TXT26-71]': '\x15\x26\x71',
                 '[TXT27-71]': '\x15\x27\x71',
                 '[TXT28-54]': '\x15\x28\x54',
                 '[TXT29-38]': '\x15\x29\x38',
                 '[TXT2a-71]': '\x15\x2a\x71',
                 '[TXT2f-54]': '\x15\x2f\x54',
                 '[TXT30-71]': '\x15\x30\x71',
                 '[TXT36-71]': '\x15\x36\x71',
                 }

SCENE_POINTERS = [0x632, # scene 1
                  0x1462, # scene 2
                  0x1800, # scene 3
                  0x1a0d, # scene 4
                  0x1e30, # scene 5
                  0x2230, # scene 6
                  ]

WINDOW_EXPANSIONS = [
                ('STORY6.COM', 0xac0, 0x5), # "You okay?"
                ('STORY6.COM', 0xb40, 0x2), # "Yes?"
                ('STORY9.COM', 0xa7a, 0xd), # "A voice boomed from above."
                ('STORY9.COM', 0xafa, 0x3), # "Cur!!" (shrink)
                ('STORY9.COM', 0xb3a, 0x3), # "Goal?" (shrink)
                ('STORY10.COM', 0x701, 0x0), # "A grave voice booms from somewhere..." x0 position
                ('STORY10.COM', 0x707, 0x13), # "A grave voice booms from somewhere..." x width
                ('ENEMY10.COM', 0x37b3, 0x1), # "!?" (srhink)
]


SHORT_STORY_MAX_WIDTH = 27
STORY_MAX_WIDTH = 34
VISUAL_MAX_WIDTH = 40

# Order of text display in the game:
# Intro cinematic
# JO.EXE (main menu)
# VISUAL.COM scene 1 (Rusty, villagers, Santos, kids)
# Level 1 (castle town)
# STORY1.COM
# Level 2 (graveyard/crypt)
# STORY2.COM
# GIRL2A.MAG (Disk B)

# VISUAL.COM scene 2 (Gateau & Rusty)
# Level 3 (Chapel)
# STORY3.COM
# Level 4 (Chapel tower)
# STORY4.COM
# ENEMY4.COM
# STORY4.COM again ("Khh... the floor!!")
# VISUAL.COM scene 3 (Floor falls, then cave)
# Level 5 (Cavern)
# STORY5.COM
# GIRL5A.MAG (Halfway done)

# Level 6 (Hydrocity Zone)
# STORY6.COM
# VISUAL.COM scene 4 (Santos, kids in inn)
# Level 7 (Sunset parallax)
# STORY7.COM
# GIRL7A.MAG (Disk C)

# VISUAL.COM scene 4 (Mary, Gateau, Ryoko)
# Level 8 (Clock tower)
# STORY8.COM
# Level 9 (Giant castle)
# STORY9.COM (Gateau)
# Gateau fight
# ENEMY9.COM (Gateau)
# VISUAL.COM
# ...