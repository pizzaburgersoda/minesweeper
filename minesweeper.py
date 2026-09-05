import tkinter as tk
import random
import time
from tkinter import messagebox

# ------------------ Minesweeper Class ------------------
class Minesweeper:
    def __init__(self, master, nrows=9, ncols=9, nmines=10, variant=None, arrangement="Random"):
        self.master = master
        self.nrows, self.ncols, self.nmines = nrows, ncols, nmines
        self.variant = variant
        self.arrangement = arrangement
        self.buttons = []
        self.colors = ["white","blue","green","red","dark blue","brown","cyan","black","gray"]
        self.flags = 0
        self.start_time = None
        self.timer_id = None

        self.flag_label = tk.Label(master, text=f"Flags: 0/{self.nmines}")
        self.flag_label.grid(row=0, column=0, columnspan=ncols//2)
        self.timer_label = tk.Label(master, text="Time: 0s")
        self.timer_label.grid(row=0, column=ncols//2, columnspan=ncols//2)

        self.setup_field()
        self.create_buttons()

        restart_btn = tk.Button(master, text="Restart (Settings)", command=self.back_to_settings)
        restart_btn.grid(row=self.nrows+1, column=0, columnspan=self.ncols//2)

        restart_same_btn = tk.Button(master, text="Restart (Same)", command=self.restart_same)
        restart_same_btn.grid(row=self.nrows+1, column=self.ncols//2, columnspan=self.ncols//2)


    def setup_field(self):
        self.field = [[0 for _ in range(self.ncols)] for _ in range(self.nrows)]

        # --- Mine arrangement logic ---
        if self.arrangement == "Balanced":
            locations = []
            for r in range(self.nrows):
                c = random.randint(0, self.ncols-1)
                locations.append(r*self.ncols+c)
        elif self.arrangement == "Clustered":
            center_r = random.randint(1, self.nrows-2)
            center_c = random.randint(1, self.ncols-2)
            cluster = []
            while len(cluster) < self.nmines:
                r = random.randint(center_r-1, center_r+1)
                c = random.randint(center_c-1, center_c+1)
                loc = r*self.ncols+c
                if loc not in cluster:
                    cluster.append(loc)
            locations = cluster
        else:  # Random
            locations_all = [x for x in range(self.ncols*self.nrows)]
            locations = random.sample(locations_all, self.nmines)

        # place mines
        for location in locations:
            r,c = divmod(location,self.ncols)
            self.field[r][c]=9
            for nr,nc in self.find_neighbors(r,c):
                if self.field[nr][nc]!=9:
                    self.field[nr][nc]+=1

        # --- Variants ---
        if self.variant == "LIAR":
            for r in range(self.nrows):
                for c in range(self.ncols):
                    if self.field[r][c]!=9:
                        self.field[r][c]=random.randint(0,8)
        elif self.variant == "MULTIPLE":
            for r in range(self.nrows):
                for c in range(self.ncols):
                    if self.field[r][c]!=9 and random.random()<0.2:
                        self.field[r][c]+=random.randint(1,3)

    def create_buttons(self):
        for r in range(self.nrows):
            row=[]
            for c in range(self.ncols):
                b=tk.Button(self.master, width=2, font=("Arial",12),
                            command=lambda r=r,c=c:self.clickon(r,c))
                b.grid(row=r+1,column=c)  # offset row by 1 for labels
                b.bind("<Button-3>", lambda e,r=r,c=c:self.flag(r,c))
                row.append(b)
            self.buttons.append(row)
        self.start_time = time.time()
        self.update_timer()

    def find_neighbors(self,r0,c0):
        nn=[]
        for r in range(max(0,r0-1),min(self.nrows,r0+2)):
            for c in range(max(0,c0-1),min(self.ncols,c0+2)):
                if (r,c)!=(r0,c0):
                    nn.append((r,c))
        return nn

    def openup(self,r,c):
        if self.buttons[r][c]["state"]=="disabled": return
        self.buttons[r][c]["state"]="disabled"
        self.buttons[r][c].config(relief=tk.SUNKEN)
        if self.field[r][c]==0:
            for nr,nc in self.find_neighbors(r,c):
                self.openup(nr,nc)
        else:
            self.buttons[r][c]["text"]=str(self.field[r][c])
            self.buttons[r][c].config(disabledforeground=self.colors[self.field[r][c]])

    def clickon(self,r,c):
        if self.field[r][c]==9:
            self.game_over()
        elif self.field[r][c]!=0:
            self.buttons[r][c]["state"]="disabled"
            self.buttons[r][c].config(relief=tk.SUNKEN)
            self.buttons[r][c]["text"]=str(self.field[r][c])
            self.buttons[r][c].config(disabledforeground=self.colors[self.field[r][c]])
        else:
            self.openup(r,c)
        if self.checkwinner():
            self.win()

    def flag(self,r,c):
        if self.buttons[r][c]["state"]=="disabled": return
        current=self.buttons[r][c]["text"]
        if current=="F":
            self.buttons[r][c]["text"]=" "
            self.flags-=1
        else:
            self.buttons[r][c]["text"]="F"
            self.buttons[r][c].config(fg="orange")
            self.flags+=1
        self.flag_label.config(text=f"Flags: {self.flags}/{self.nmines}")

    def checkwinner(self):
        count=0
        for r in range(self.nrows):
            for c in range(self.ncols):
                if self.buttons[r][c]["state"]=="disabled":
                    count+=1
        return count==self.nrows*self.ncols-self.nmines

    def game_over(self):
        for r in range(self.nrows):
            for c in range(self.ncols):
                self.buttons[r][c]["state"]="disabled"
                self.buttons[r][c].config(relief=tk.SUNKEN)
                if self.field[r][c]==9:
                    self.buttons[r][c]["text"]="*"
                    self.buttons[r][c].config(background="red",disabledforeground="black")
        self.stop_timer()
        print("Game Over!")

    def win(self):
        for r in range(self.nrows):
            for c in range(self.ncols):
                if self.field[r][c]==9:
                    self.buttons[r][c]["text"]="*"
                    self.buttons[r][c].config(background="green",disabledforeground="black")
        self.stop_timer()
        print("Player Won!")

    def back_to_settings(self):
        self.stop_timer()
        self.master.destroy()
        open_setup_window()

    def update_timer(self):
        elapsed=int(time.time()-self.start_time)
        self.timer_label.config(text=f"Time: {elapsed}s")
        self.timer_id=self.master.after(1000,self.update_timer)

    def stop_timer(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id=None
    def restart_same(self):
        """Restart game with current settings without returning to setup"""
        self.stop_timer()
        for r in range(self.nrows):
            for c in range(self.ncols):
                self.buttons[r][c].destroy()
        self.buttons = []
        self.flags = 0
        self.flag_label.config(text=f"Flags: 0/{self.nmines}")
        self.setup_field()
        self.create_buttons()

# ------------------ Setup Window ------------------
def start_game(rows, cols, mines, variant, arrangement):
    game_window = tk.Tk()
    game_window.title("Minesweeper")
    Minesweeper(game_window, nrows=rows, ncols=cols, nmines=mines,
                variant=variant, arrangement=arrangement)
    game_window.mainloop()

def open_setup_window():
    setup = tk.Tk()
    setup.title("Minesweeper Setup")

    tk.Label(setup,text="Rows (5-20):").grid(row=0,column=0)
    rows_entry=tk.Entry(setup); rows_entry.insert(0,"9"); rows_entry.grid(row=0,column=1)

    tk.Label(setup,text="Columns (5-20):").grid(row=1,column=0)
    cols_entry=tk.Entry(setup); cols_entry.insert(0,"9"); cols_entry.grid(row=1,column=1)

    tk.Label(setup,text="Mines (1 to rows*cols-1):").grid(row=2,column=0)
    mines_entry=tk.Entry(setup); mines_entry.insert(0,"10"); mines_entry.grid(row=2,column=1)

    tk.Label(setup,text="Variant:").grid(row=3,column=0)
    variant_var=tk.StringVar(value="None")
    variants=["None","LIAR","MULTIPLE"]
    tk.OptionMenu(setup,variant_var,*variants).grid(row=3,column=1)

    tk.Label(setup,text="Mine Arrangement:").grid(row=4,column=0)
    arrangement_var=tk.StringVar(value="Random")
    arrangements=["Random","Balanced","Clustered"]
    tk.OptionMenu(setup,arrangement_var,*arrangements).grid(row=4,column=1)

    # --- Difficulty Presets ---
    def set_easy():
        rows_entry.delete(0,tk.END); rows_entry.insert(0,"9")
        cols_entry.delete(0,tk.END); cols_entry.insert(0,"9")
        mines_entry.delete(0,tk.END); mines_entry.insert(0,"10")

    def set_medium():
        rows_entry.delete(0,tk.END); rows_entry.insert(0,"16")
        cols_entry.delete(0,tk.END); cols_entry.insert(0,"16")
        mines_entry.delete(0,tk.END); mines_entry.insert(0,"40")

    def set_hard():
        rows_entry.delete(0,tk.END); rows_entry.insert(0,"30")
        cols_entry.delete(0,tk.END); cols_entry.insert(0,"16")
        mines_entry.delete(0,tk.END); mines_entry.insert(0,"99")

    tk.Label(setup,text="Difficulty Presets:").grid(row=5,column=0)
    tk.Button(setup,text="Easy",command=set_easy).grid(row=5,column=1)
    tk.Button(setup,text="Medium",command=set_medium).grid(row=6,column=1)
    tk.Button(setup,text="Hard",command=set_hard).grid(row=7,column=1)

    def validate_and_start():
        try:
            rows=int(rows_entry.get()); cols=int(cols_entry.get()); mines=int(mines_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input","Rows, Columns, and Mines must be integers.")
            return
        if not (5 <= rows <= 20):
            messagebox.showerror("Invalid Rows","Rows must be between 5 and 20."); return
        if not (5 <= cols <= 20):
            messagebox.showerror("Invalid Columns","Columns must be between 5 and 20."); return
        if not (1 <= mines < rows*cols):
            messagebox.showerror("Invalid Mines",f"Mines must be between 1 and {rows*cols-1}."); return

        setup.destroy()
        start_game(rows, cols, mines, variant_var.get(), arrangement_var.get())

    tk.Button(setup,text="Start Game",command=validate_and_start).grid(row=8,columnspan=2)
    setup.mainloop()

# ------------------ Launch ------------------
open_setup_window()
