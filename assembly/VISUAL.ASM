; Hack to support halfwidth text in VISUAL.COM cut scenes.
; I refer to "fake" and "real" halfwidth text hacks because originally,
; I stored all the text as fullwidth latin characters, then translated them
; into the equivalent halfwidth characters when being moved to the screen.
; But I figured out how to get "real" halfwidth text for the final hack.

;VISUAL.COM REAL HALFWIDTH TEXT HACK:
;0x3ac7 20 -> 1b
;0x403c 04 -> 02
;0x3e39 2c 1a -> 2c 00
;And another thing to handle upper/lowercase text correctly

;2c 01, df (should be de) ; wait, what does this mean again?

;HOW I GOT THERE:
;Getting the second byte of a two-byte sequence:

mov ah, cs:[409d] ;(mov ah, 8312:[409d], which holds x82)
;^ 8312:409d is a spot where it keeps the first byte. The first-byte routine has a mov cs:[409d], al instruction.
	;(brackets mean the value at that address)

;Checks to see if al is below 80, then jumps to 401e

;What's going on in the seciton where it moves ax to [di], [di+80], [di+180], [di+4], [di+84], [di+104], and [di+184]?
	;It's not VRAM. Just something that a lot of zeroes get written into...?

;with both bytes (82bd, "ta") in register a:
FUNCTION_8312:3e37
	cmp al, 61
	adc al, de  ;add with carry
	add ah, ah
	sub al, 1f
	;EAX= 049e now
	add ax, 1fa1 ;(now 243f)
	and ax, 7f7f ;(still 243f)
	ret
	sub ax, 2000 ;(now 043f) <---!!
	out a1, al ;(wonder what this does??)  <- system call to FONT.ROM
	mov ah, al ;(now 0404)
	out a3, al

/*
So, do these numbers have anything to do with the coordinates on the font chart?
font.bmp is 2048 * 2048, with 16x16 characters. So, (0x80)x(0x80) characters. (assuming all are fullwidth)
	Kind of like the 7f7f thing, right?
	Yes - "ta" is 04 across, 0x3f down on the font chart!
	This holds for others, too - "ni" is 04 across, 0x4b down on the font chart.

Now, how can I get it to point to column 9?
	Add 500 instead of sub 2000? (no)
	sub 1b00 instead of sub 2000? (write this at 0x86be7)
	ABCDabcd = chi ti tsu TSU, me mo ya YA =  82bf82c082c182c282df82e082e182e2
	Yup, it works.
	Hack: in the string 15 01 e8 72 03 2d 00 20 e6 a1 8a c4 e6 a3, change the 20 to a 1b.

For the second part of the hack: How can I get them to show up adjacent?
	0x8715c  8312:403a   83c704 add di, +04 <- change this to +02? (yep, this squishes the text)

Is there any way to avoid using two bytes per character?

What happens when it processes ascii text?
	when EAX= 0041,
	out a3, al <- not quite the out a1, al that happened once it got the grid

	(out a1 = row, out a3 = column??)
	How can I populate ah before it gets to that point?
	b4 09 = mov ah, 09. Write that at DS:4006
	Whoops, now it seems to be doing the same math it was doing earlier?? I could probably add an 82 instead...
		"A" is column 9, 0x41 down. So hoping for a value of 0941.
			With that 1b00 subtracted at the end, getting 0822 instead. That's no good.
			Subtract 1a00 instead?

			adc al, 61 before: 442, 421
			0x942
			Doesn't seem to write anything... I think it skips a lot of steps, like writing ax to [di], [di+80], [di+180], [di+4], [di+84], [di+104], and [di+184], or writing to all the VRAM planes a few times. Maybe I'm just falling afoul of a particular branch somewhere?

	I never put it in the stack, should I do that? (There's a function at like effe that's, push ax, push si)
		After it puts al in that one byte:
			4099: pop si, pop cx, pop ax, ret

			If cs:[31da] is 00, then jump to 31cc.
				Which moves 003c to ax, and then calls 000e.
					Which does stuff in JO.EXE, like calling int 18 (which checks for keystrokes).
		As it loads the second byte, the "original" first byte (0582) is two words ABOVE the stack pointer.

	Anyway, trying this again. Change DS:4006 to b4 82 (mov ah, 82).
		Coords are 0x0922 this time. Should be a letter "D"
		It gets to the part where it should be writing to the empty block, but it seems to be all zeroes...
		Oh, it does write stuff when it gets to the di, di+80, etc loop.
		Hey this like basically works!! I think I had just put that mov ah, 82 instruction in the wrong place earlier.
		Good thing I understand this thing exhaustively now.

		Just gotta change the math... How about nop-ing the add al, 1f? (DS:3e3a turns from 1a -> 00
			Heh. So, the lowercase text is now ROT25.
				I need to add 1 instead of subtracting 0.
					Change that whole instruction to 04 01, not b4 00.
			3e3d: 3c61 cmp al 61
			3e3f 14de adc al, de (if it's )

*/

IMPORTANT FUNCTIONS/LOCATIONS:
40b1 lodsb (loads a byte to consider)
31cc mov ax, 003c (then it jumps to JO.EXE and tests for keystrokes)
3ffe push ax, push cx, push si, mov cs:[409d]
3e37 add ah, ah (font table coordinates, part 1)
3ac5 sub ax, 2000 (font table coordinates, part 2)
3ad4 mov al, dl (does some looping IO and stores results in that empty block starting at 3c04)
	This section is 0x222 bytes long. Any ideas on what that might be?
		32x32 = 0x400. (But a char )
			Only the numbers 0, 3, f, and c appear, and they appear only in two adjacent columns, the next two columns being empty... Would this change for a different color?
3af3 (the di, di+80, di+100, di+180, etc)
3f1e mov si, 3c26, mov ax a800, call 3f3a, mov ax b000, call 3f3a, etc (write to VRAM)
	This gets called twice - call 3f1e, call 33c6, call ef1e. Wonder why?

33c6 pushf - the thing that happens between two VRAM writes.
403a: add di +02, cmp 8141, 8143, 8145, 8149 (punctuation jump to 4056)
(Lots of branches here, come back later)

43f3 mov dx, 0050 (mov ax a800, call 4414, mov ax, b000, call 4414, etc) <- back to VRAM again??

cs:[409d]: where the first byte is stored for later recall, then later set back to 0 (at 402e)
[327b] - gets loaded to al in the inter-VRAM writing thing??
[327c] - same
	Both appear to be 00 or 01, then xor'd with al. Then that gets outed to the font data...? Odd or even font thing?
	Is this to print the shadows????????
[40a2] - currently 14, gets moved to cx if it's punctuation.
[40a4] - currently 28, gets moved to cx if it's ...

I might just try to take the hack as it is and see how far I can get. (Reassigning it to legible fullwidth Roman characters though.)
			That probably means it should be 1a and not 1b...?


Different approach: What are the pointers for VISUAL.COM?
	Reading the data for the first scene: I think the first thing that gets pointed to is 0x632, which is 0x10 0x00 _visual1.m etc. This is right after a bunch of add/subtract type instructions, and after this it just does a bunch of lodsb instructions, which increases the ESI register, just reading through the thing one byte at a time.

	The bytes 32 06 are found early - at 0x77. Surroundings:
		ff 60 1e 06 be_32 06_eb 6d e8 a8
		ff 60 1e 06 be_62 14_eb 62 e8 9d <- points to the beginning of VISUAL2.COM.
		The string "ff 60 1e 06 be" appears 6 times in the file, which is the number of scenes.

		Could I rewrite these pointers to point below the code??


	Issue: at 0x8312:47e0, some other file is getting loaded. (seg 8790)

	Before VISUAL.COM is written, it knows it is getting written at seg 8312 (in ES), for 47e0 bytes (in ECX). Where does it get this 47e0 figure?

	Looks like it gets it from JO.EXE in two places.
		0x1704 - no effect?
		0x1981 - allocation for VISUAL.COM

	Set it to 47f0 in both places. Now the file just below it, MAGLOAD.COM, won't work since it's getting overlapped, and it crashes before displaying anything.

	MAGLOAD.COM's allocated space/ECX/EBP value, 5a30, shows up in two places in JO.EXE as well.
	And the file that shows up before it, GRPEGC.COM, appears to have 5a30 allocated to it too.
		These two files begin at seg 8790.

;69 and 73 refer to places * 0x1000 in VRAM. Hence the control codes.

;UPPERCASE/LOWERCASE THING

;Need to add de to lowercase letters (al >= 61), but df to uppercase letters (else).
;old versions:
	3e39 2c00 sub al, 00
	3e3b 7804 js 3e41
	3e3d 3c61 cmp al, 61
	3e3f 14de adc al, de

;	If I overwrite 4 instructions, that's space for 8 bytes
	3e39 3c61 cmp al, 61
	3e3b 7202 jb   3e3f   ;               ----->
	3e3d 0401 add al, 0   ;                     |
	3e3f 04de add al, de  ;                  <---

;3c617202040104de
;3c617202040004df <- works!

;Uh, turns out I really just need to add de to any character. So mostly I can just nop these things.

;04df909090909090