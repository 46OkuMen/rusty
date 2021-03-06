; This hack was no longer necessary - the halfwidth text
; ended up being supported after the GAMEOVER and JO hacks
; interacted in a really convenient way.

;8312:4604 2e8a269d40 mov ah, cs:[409d] -> b428909090
;8312:462b 2d0020 sub ax, 2000 -> 2d001b

or ah, ah

;Try: put  b482909090 instead of that mov instruction. (mov ah, 82; nop nop nop etc)

;Does some of its own math, but also does some of the math elsewhere in VISUAL.COM that I've changed. If I change that, I'll break this too!!

8312:462b 2d0020 sub ax, 2000
;Change this to 2d001b, see what happens.

;So it does some math to a text byte, (result: 0843) then
xchg al, ah ;(now 4308)
stosw
or al, 80 ;(now 4388)
stosw

;It's storing them at a000, which is the text VRAM segment.
;a000:0fea

;08 41 88 41 08 42 88 42 08 43 etc

;What happens if I get rid of one of the stores, or make it a stosb instead?
8312:4630 ab stosw ;(ater xchg)
8312:4633 ab stosw ;(after or)

;Correct values for SJIS characters:

;05 62 85 62 - mo
;05 73 85 73 - -n

;The first two bytes are the normal "char coordinates" bytes we've been using.
;The second two? Just 80 added to the first byte??