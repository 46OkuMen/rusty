https://rpg.hamsterrepublic.com/ohrrpgce/16-color

## Converting BMP to MAG

### Getting a compatible 16-color BMP
* Open the file in GIMP.
* Right click on your sprite, goto Image -> Mode -> Indexed. Convert your sprite to 16 colours, choosing 'optimised palette'. You should have no more than 16 colours in your sprite, or at least one of them will change.
* Export As -> bmp, and it'll automatically save it as a 4-bit/16-color BMP.
	* In the final "Export image as BMP" options dialog, under 'Compatibility Options', check the box 'Do not write color space information'.

### Conversion to MAG
* A few choices here:
	* JEDAI.HDI
		* Put the BMP in JEDAI.HDI.
		* Click the floppy disk button, then the one with the arrow facing away from the disk. Select the .BMP image.
		* Now click the floppy disk again, and the one with the arrow facing toward the disk. Save it as a 16-bit MAG.
	* abc0234f.rar
		* (Don't remember. Something about AtoB converter with Susie plugins)