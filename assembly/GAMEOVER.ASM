18b8:08d5 8ae0 mov ah, al
18b8:08d7 ac lodsb

;Change to:
mov ah, 82 ; b4 82
nop        ; 90

18b8:08e9 83c104 add cx, +04 ;is this the char cursor?
;Change to:
add cx, +02