; Hack to support halfwidth text in the main menu.

;GRPEGC.COM
;48d9 20 -> 1a: font table column shift
;4ad7: 1f -> 00; font table row shift

;(Original bytes for these two: 04 2c 5e eb 02 fe cc 2c 1f 80 ec 20)

;JO.EXE
;8c4 04 -> 02: halfwidth cursor
;aae 8a e0 ac  -> b4 82 90: read every char


;"Gemu Sotato" = 83 51 etc

;8351

;Second-byte loading:
mov ah, al
lodsb

;Proposed replacement:
mov ah, 82
nop

;Yep! It works.

;At 8790:4857, it does "out a1, al"

mov al, 0b
out 68, al
mov ax, [bp+04]
mov di, [bp+06]
cmp ah, 00
jz 4883
call 48ae

	48ae cmp ah, 80
	48b1 jz 48d9
	48b3 cmp ah, a0
	48b6 jnb 48bd
	48b8 sub ah, 70
	jmp 48c5

		or al, al
		jns 48cb
			add ah, ah
			;...
			dec ah
			48d7 sub al, 1f
			48d9 sub ah, 20


