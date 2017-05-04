import tkinter, tkinter.constants, tkinter.filedialog
import sys
import time
from os import listdir, getcwd, chdir
from os import path as ospath
from tkinter.ttk import *
from contextlib import redirect_stdout
import tkinter.messagebox

from patcher import patch
from rominfo import common_filenames
from romtools.disk import HARD_DISK_FORMATS

# TODO: Enter to press the "Patch" button.
# TODO: Use a labelframe to clean things up a bit?

class PatcherGUI(tkinter.Frame):

    def __init__(self, root):

        tkinter.Frame.__init__(self, root)

        Label(self, text="Rusty, English Translation by 46 OkuMen")
        # define buttons
        Label(self, text="HDI/System Disk").grid(row=1, column=0, sticky='E')
        Label(self, text="Opening Disk").grid(row=2, column=0, sticky='E')
        Label(self, text="Game Disk A").grid(row=3, column=0, sticky='E')
        Label(self, text="Game Disk B").grid(row=4, column=0, sticky='E')
        Label(self, text="Game Disk C").grid(row=5, column=0, sticky='E')

        sysDisk = tkinter.StringVar()
        opDisk = tkinter.StringVar()
        gameDiskA = tkinter.StringVar()
        gameDiskB = tkinter.StringVar()
        self.PatchStr = tkinter.StringVar()
        self.PatchStr.set('Patch')

        SysEntry = Entry(self, textvariable=sysDisk)
        OpEntry = Entry(self, textvariable=opDisk)
        GameDiskAEntry = Entry(self, textvariable=gameDiskA)
        GameDiskBEntry = Entry(self, textvariable=gameDiskB)

        GameDiskCEntry = Entry(self)
        GameDiskCEntry.insert(0, 'Patch not needed')
        GameDiskCEntry['state'] = 'disabled'

        SysEntry.grid(row=1, column=1, padx=5)
        OpEntry.grid(row=2, column=1, padx=5)
        GameDiskAEntry.grid(row=3, column=1, padx=5)
        GameDiskBEntry.grid(row=4, column=1, padx=5)
        GameDiskCEntry.grid(row=5, column=1, padx=5)

        # TODO: If I set these to attributes, it will probably cut down on all the argument passing I'm doing
        all_entry_text = [sysDisk, opDisk, gameDiskA, gameDiskB]
        secondary_entries = [OpEntry, GameDiskAEntry, GameDiskBEntry]
        self.advanced_active = tkinter.BooleanVar(False)

        SysBrowse = Button(self, text='Browse...', command= lambda: self.askopenfilenamesysDisk(sysDisk, all_entry_text, secondary_entries))
        OpBrowse = Button(self, text='Browse...', command= lambda: self.askopenfilename(opDisk, all_entry_text, secondary_entries))
        GameDiskABrowse = Button(self, text='Browse...', command= lambda: self.askopenfilename(gameDiskA, all_entry_text, secondary_entries))
        GameDiskBBrowse = Button(self, text='Browse...', command= lambda: self.askopenfilename(gameDiskB, all_entry_text, secondary_entries))

        SysBrowse.grid(row=1, column=2, padx=5)
        OpBrowse.grid(row=2, column=2, padx=5)
        GameDiskABrowse.grid(row=3, column=2, padx=5)
        GameDiskBBrowse.grid(row=4, column=2, padx=5)

        self.PatchBtn = Button(self, textvariable=self.PatchStr, command= lambda: self.patchBtnCommand(sysDisk, opDisk, gameDiskA, gameDiskB, pathInDisk, SpeedhackOn))
        self.PatchBtn.grid(row=9, column=5)
        self.PatchBtn['state'] = 'disabled'

        SpeedhackOn = tkinter.IntVar(value=0)
        SpeedhackBox = tkinter.Checkbutton(self, text="Faster text (requires Neko Project II)", variable=SpeedhackOn)
        SpeedhackBox.grid(row=7, column=0, columnspan=2)

        AdvancedBtn = Button(self, text="Advanced...", command= lambda: self.toggleadvanced(AdvancedPath, AdvancedLabel))
        AdvancedBtn.grid(row=9, column=2)

        pathInDisk = tkinter.StringVar('')
        AdvancedPath = Entry(self, textvariable=pathInDisk)
        AdvancedLabel = Label(self, text="Path In Disk")

        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.fdi'
        options['filetypes'] = [('PC-98 images', ('.fdi', 'fdd', '.hdm', '.hdi', 'd88')), ('all files', '.*')]
        options['initialdir'] = exe_dir
        options['initialfile'] = 'myfile.txt'
        options['parent'] = root
        options['title'] = 'Select a disk image'

        # defining options for opening a directory
        self.dir_opt = options = {'initialdir': exe_dir}
        options['initialdir'] = exe_dir
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'Select a disk image'

    def askopenfilenamesysDisk(self, field, all_entry_text, secondary_entries):

        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        """

        # get filename
        filename = tkinter.filedialog.askopenfilename(**self.file_opt)
        field.set(filename)

        self.checkCommonFilenames(all_entry_text)

        self.toggleDiskBFields(filename, secondary_entries, self.PatchBtn)

    def askopenfilename(self, field, all_entry_text, secondary_entries):
        filename = tkinter.filedialog.askopenfilename(**self.file_opt)
        field.set(filename)
        self.checkCommonFilenames(all_entry_text)

        if all([t.get() for t in all_entry_text]):
            self.PatchBtn['state'] = 'normal'
        else:
            self.PatchBtn['state'] = 'disabled'

        print("Calling toggleDiskBFields")
        self.toggleDiskBFields(filename, secondary_entries, self.PatchBtn)

    def checkCommonFilenames(self, all_entry_text):
        if sum([len(t.get()) > 0 for t in all_entry_text]) == 1:
            filepath = [t.get() for t in all_entry_text if len(t.get()) > 0][0]
            file_folder = '/'.join(filepath.split('/')[:-1]) + '/'
            filename = filepath.split('/')[-1]
            for c in common_filenames:
                if filename == c[0]:
                    for i, disk in enumerate(c):
                        if disk in listdir(file_folder):
                            disk_filepath = file_folder + disk
                            all_entry_text[i].set(disk_filepath)
                    return None

    def toggleDiskBFields(self, sysDiskFilename, secondary_entries, patchbtn):
        if sysDiskFilename.split('.')[-1] in HARD_DISK_FORMATS:
            for d in secondary_entries:
                d['state'] = 'disabled'
            self.PatchBtn['state'] = 'normal'
        elif all([d.get() for d in secondary_entries]):
            print([d.get() for d in secondary_entries])
            print("All secondary entries are filled in")
            for d in secondary_entries:
                d['state'] = 'normal'
            self.PatchBtn['state'] = 'normal'
        else:
            print("Setting the secondary entries back to normal")
            for d in secondary_entries:
                d['state'] = 'normal'
            self.PatchBtn['state'] = 'disabled'


    def patchfiles(self, sys, op, gameA, gameB, path=None, speedhack=False):
        backup = ospath.join(exe_dir, 'backup')

        sysDisk = sys.get()
        print("Speedhack value:", speedhack.get())
        if sysDisk.split('.')[-1].lower() in HARD_DISK_FORMATS:
            if self.advanced_active.get():
                result = patch(sysDisk, path_in_disk=path.get(), backup_folder=backup, speedhack=speedhack.get())
            else:
                result = patch(sysDisk, backup_folder=backup, speedhack=speedhack.get())
        else:
            result = patch(sysDisk, op.get(), gameA.get(), gameB.get(), backup_folder=backup, speedhack=speedhack.get())
            
        self.patchBtnIdle()
        if not result:
            print("Patching was successful")
            tkinter.messagebox.showinfo('Patch successful!', 'Go play it now.')
        else:
            try:
                print("Error while patching:", result)
            except UnicodeEncodeError:
                print("Error while patching:", repr(result))
            tkinter.messagebox.showerror('Error', 'Error: ' + result)

        

    def patchBtnCommand(self, sys, op, gameA, gameB, path=None, speedhack=False):
        self.patchBtnPatching()
        self.update_idletasks() # Necessary to get the button text to update
        self.patchfiles(sys, op, gameA, gameB, path, speedhack)


    def patchBtnPatching(self):
        self.PatchStr.set('Patching...')
        self.PatchBtn['state'] = 'disabled'


    def patchBtnIdle(self):
        print("Editing patchstr and patchbtn now")
        self.PatchStr.set('Patch')
        self.PatchBtn['state'] = 'normal'

    def toggleadvanced(self, advpath, advlabel):
        print("advanced_active:", self.advanced_active.get())
        if self.advanced_active.get():
            root.geometry('400x180')
            advpath.grid_forget()
            advlabel.grid_forget()
            self.advanced_active.set(False)
        else:
            root.geometry('400x200')

            advpath.grid(row=8, column=1)
            advlabel.grid(row=8, column=0, sticky='E')
            self.advanced_active.set(True)

if __name__=='__main__':
    exe_dir = getcwd()
    if hasattr(sys, '_MEIPASS'):
        chdir(sys._MEIPASS)

    # TODO: Uncomment these for release.
    # Python 3 version
    logfilename = ospath.join(exe_dir, 'rusty-patch-log.txt')
    #with open(logfilename, 'w') as f:
    #    with redirect_stdout(f):
    #        print("\n", time.ctime(time.time()))

    root = tkinter.Tk()
    root.title('Rusty Patcher')
    root.iconbitmap('46.ico')
    root.geometry('400x180')
    PatcherGUI(root).pack()
    root.mainloop()
