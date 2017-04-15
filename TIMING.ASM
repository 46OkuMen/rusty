; So, when it's a punctuation character:
mov cx, cs:[40a2] ; yes, the value at cs:40a2, which is 0x14
jcxz 4099 ; which it doesn't, since cx was just set
; 4099 is the pop si, pop cx, pop ax, ret thing.
call 31c0 ; only if punctuation!

; ...

mov ax, 003c
call 000e

; ...
call far cs:[30c6]

; Timing stuff is generally done with the IO ports in the 0x70s.

; Can crash facial animations, but doesn't seem to affect text.
; 90ff:3e57 b0c0 mov al, c0
; 90ff:3e59 e67c out 7c, al

; Changing this can crash facial animations, but doesn't seem to affect text.
; 90ff:3ef6 b000 mov al, 00
; 90ff:3ef8 e67c out 7c, al

; Something that loops a long time increments the ptr cs:[166d] a lot. Would it speed it up to increment it by more than 1???
; This appears to be unrelated - replacing it with nop's has no effect on anything.

; So, what if I rewrite that loop to use the timer controller instead?

in al, a0    ; GDC controller, or maybe the font ROM - usually 84 or c4, 22 not very often (breaks loop)
jmp 4555
jmp 4557
test al, 20  ; 0100 0000

in al, 71 ; change a0 to 71; read timer #0
jmp 4555
jmp 4557
test al, ff  ; change 74 to 75

; So how fast does this timer go?
; 8b, 34, 8d, 11, 90, f7, 91, d4, 94, ba, 96, 99, 7d, 
; It alternates between low byte and high byte. 8b-99 are the high byte


; Try it with the real world clock? port x26

e475a82075fa90909090

; set the control word: counter #2, high byte only
mov al, a0
out 77, al
= b0a0e677

; load ff into counter #2
mov al, ff
out 75, al
= b0ffe675

; loop to read counter #2
in al, 75 ; change a0 to 71; read timer #0
jmp 4555
jmp 4557
test al, ff  ; change 74 to 75

= e475eb00eb00a8ff

Stuff that happens in punctuation but not other things:
mov cx, cs:[40a2] ; values is 0x14
jmp 408a

jcxz 4099
call 31c0

pusha
cmp cs:[31da], 00
jnz 31cc

mov ax, 003c
call 000e

; So what is this ax value in a normal letter?
; Looks like it's 0016...
; What if I change it to 0008?
; Bad things/crashes.

; So, in 000e, which calls a function far away, uses the ax value to call a function....

push bp
mov bp, 6360
shl ax, 1 ; shift it left by 1. 16 -> 2c
add bp, ax ; bp = 638c
call cs:[bp+00]

; So letters call cs:69ac. (?)
; Punctuation has the bp value 63d8, which calls cs:6ce3.

; After it does a letter specific thing, it calls the 3c version later...