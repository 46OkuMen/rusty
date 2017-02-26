import os

# TODO: I really should just make a "Settings" object for this.

SRC_DISK_DIR = 'original\\'
SRC_DISK_PATH = 'original\\rusty.hdi'

DEST_DISK_DIR = 'patched\\'
DEST_DISK_PATH = 'patched\\rusty.hdi'

FILES = ['JO.EXE', 'OP.COM', 'VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM', 'STORY4.COM',
         'STORY5.COM', 'STORY6.COM', 'STORY7.COM', 'STORY8.COM', 'STORY9.COM',
         'STORY10.COM', 'ENEMY1.COM', 'ENEMY4.COM', 'ENEMY9.COM', 'ENEMY10.COM']

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
                 '[01d21d]': '\x01\xd2\x01',
                 '[5f4501]': '\x04\xf4\x01',
                 '[01e71d]': '\x01\xe7\x1d',
                 '[012b1e]': '\x01\x2b\x1e',
                 '[01161e]': '\x01\x16\x1e',
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
                 '[TXT11-71]': '\x15\x11\x71',
                 '[TXT1a-71]': '\x15\x1a\x71',
                 '[TXT1d-71]': '\x15\x1d\x71',
                 '[TXT1e-71]': '\x15\x1e\x71',
                 '[TXT26-71]': '\x15\x26\x71',
                 '[TXT28-54]': '\x15\x28\x54',
                 '[TXT29-38]': '\x15\x29\x38',
                 '[TXT2a-71]': '\x15\x2a\x71',
                 '[TXT2f-54]': '\x15\x2f\x54',
                 '[TXT30-71]': '\x15\x30\x71',
                 '[TXT36-71]': '\x15\x36\x71',
                 }


# Scene 4 crash
# Check the control code counts.
# 017b19 (6 in JP, only 4 of 013a1a in EN) One thing remains 017b19, right after "Let's go eat."
# 7d 19
# 019019
# 9f 19
# a1 19
# 01bc19
# be 19
# 01d119
# d6 19
# d8 19
# 01f319
# f5 19
# 01081a
# 1a0d

# Check the animation loops, something is accidentally going to the Mayor's blinking animation and crashing stuff.
# 01901a -> 1a90, loops to 1a97

# Mina animations
# 01b21a -> 1ab2, loops to 1ab4.
# 01c71a -> 1ac7, loops to 1a08!? that seems bad.
  # Original ctrl code: 01081a. That one loops to 1a08. So it never got changed...
  # Location of the pointer is 1a0b.

# 015e1a -> 1a5e, loops to 1a60.
  # Before "She's beating up the bad guys"
# 01951a -> 1a95, loops to 1a97.
  # Also before "She's beating up the bad guys"

# Nett animations
# 017b1a -> 1a7b, loops to 1a7d.
  # Before "She's beating up the bad guys"

# Santos' animations
# 014f1a -> 1a4f, loops to 1a4f. (5 in patched)
  # Original: 019019 (6 in original)
    # 1. Before "It's that young traveler"
    # 2. Before "I wonder what she's up to?"
    # 3. Before "She did at that"
    # 4. Before "She looked very strong"
    # 5. (missing in patched) Before "Now then, Nett, Mina."
# 013a1a -> 1a3a, loops to 1a3c. (5 in patched)
  # Original: 017b19 (6 in original)

# What's up with this thing at 1a90? It seems to loop back to 19d1, which won't do...

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
# ...