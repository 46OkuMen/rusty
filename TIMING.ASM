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