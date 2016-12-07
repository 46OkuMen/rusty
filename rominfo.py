FILES = ['VISUAL.COM', 'STORY.COM']

FILE_BLOCKS = {'VISUAL.COM': [(0x6d9, 0x17ef), # vs1-2
                              (0x1899, 0x1971), # vs3
                              (0x1a7e, 0x1dc2), # vs4
                              (0x1ea4, 0x21ec), # vs5
                              (0x22ad, 0x288d), # vs6
                              (0x2a7f, 0x2d11), # ending1
                              (0x2d52, 0x2ff5),], # ending2]

               'OP.COM': [(0x55b, 0x646),], # not compressed; not sure what it is
               'JO.EXE': [(0x6c23, 0x6cd8), # main menu, options
               	          (0x6cd3, 0x6cee),
               	          (0x6d5a, 0x6db5),
               	          (0x6e96, 0x6ef0),
               	          (0x6f7e, 0x7022),]

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

# Stuff I know I'm still looking for:
# opening cinematic (likely in images, in R_***.MGX files)