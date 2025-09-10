import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox as messagebox
from ttkbootstrap.tableview import Tableview
from sqlcipher3 import dbapi2 as sqlc
import os
from datetime import datetime, date

class Dashboard(tb.Frame):
    def __init__(self,master,controller):
        super().__init__(master)
        self.controller=controller                 #allow app to control frame
        
        dash_frame=tb.Frame(self,padding=20)
        dash_frame.pack(pady=10,expand=True,fill="both",padx=10)

        
        tb.Label(dash_frame,text="noted.",font=("Arial",30)).pack(pady=10)

        tb.Button(dash_frame,text="view entries",command=lambda:self.controller.show_frame("ViewHistory")).pack(pady=10)  #go to entry  table

        tb.Button(dash_frame,text="create entry",command=lambda:self.controller.show_frame("AddEntry")).pack(pady=10)    #go to adding entry

class ViewHistory(tb.Frame):
    def __init__(self,master,controller):
        super().__init__(master)
        self.controller=controller
        
        coldata=[     
            {"text":"ID","stretch":True},                                                                     #format columns
            {"text":"Title","stretch":True},
            {"text":"Entry","width":100,"stretch":True},
            {"text":"Date","width":100,"stretch":True}
        ]

        tb.Label(self,text="view entries",font=("Helvetica",15)).pack(pady=10)


        self.table=Tableview(                                                              #configure table
            self,
            coldata=coldata,
            searchable=True,
            yscrollbar=True,
            autofit=True
        )
        self.table.hide_selected_column(cid=0)
        self.table.pack(expand=True,fill="both",padx=10,pady=10)
        self.table.view.unbind("<Button-3>")                                        #remove context menu so we can implement proper deletion function

        button_frame1=tb.Frame(self)
        button_frame1.pack(pady=10)
        tb.Button(button_frame1,text="view entry",command=self.show_entry).pack(side=tb.LEFT,padx=10)        
        tb.Button(button_frame1,text="delete",command=self.delete_entry).pack(side=tb.LEFT,padx=10)
        tb.Button(button_frame1,text="refresh",command=self.refresh).pack(side=tb.LEFT,padx=10)
        tb.Button(self,text="back",command=lambda:self.controller.show_frame("Dashboard")).pack(side=tb.RIGHT,pady=10,padx=10)      #action buttons

    def get_history(self):

        if not self.controller.key:
            return
        db=sqlc.connect("notes.db")
        cursor=db.cursor()
        cursor.execute(f"PRAGMA key = '{self.controller.key}'") #decrypt db

        query="SELECT id,title,entry,date FROM entries"       #data query
        
        query+=" ORDER BY date DESC"   
        cursor.execute(query)               #run query
        rows=cursor.fetchall()               #retrieve data
        db.close()
        
        return rows
    
    def refresh(self):                      #update data on showing frame
        rows=self.get_history()             #retrieve data
        self.table.delete_rows()            #clear table
        self.table.insert_rows(0,rows)      #insert new data

    def show_entry(self):
        selected=self.table.view.selection()        #retrieve selected row
        if not selected:
            return
        row=self.table.get_row(iid=selected[0])     #get row data
        id=row.values[0]                            #get id
        db=sqlc.connect("notes.db")
        cursor=db.cursor()
        cursor.execute(f"PRAGMA key = '{self.controller.key}'")         #decrypt db

        query="SELECT id,title,entry,date FROM entries WHERE id=?"      #retrieve entry data
        cursor.execute(query,(id,))
        data=cursor.fetchone()
        db.close()
        self.controller.current_entry=data
        self.controller.show_frame("ViewEntry")             #redirect to ViewEntry frame
    
    def delete_entry(self):
        selected=self.table.view.selection()            #get selected row
        if not selected:
            return
        row=self.table.get_row(iid=selected[0])         #get row data
        id=row.values[0]

        db=sqlc.connect("notes.db")
        cursor=db.cursor()
        cursor.execute(f"PRAGMA key = '{self.controller.key}'")         #decrypt db

        query="DELETE FROM entries WHERE id=?"          #delete entry
        cursor.execute(query,(id,))
        db.commit()
        db.close()
        self.refresh()                                  #refresh table with new data    

class ViewEntry(tb.Frame):
    def __init__(self,master,controller):
        super().__init__(master)
        self.controller=controller
    
    def refresh(self):

        for widget in self.winfo_children():
            widget.destroy()                                                                   #clear prior widgets

        if(not self.controller.current_entry):
            return                                                                             #return if no selected entry
        
        tb.Label(self,text="view entry",font=("Helvetica",15)).pack(pady=10)
        title=tb.Entry(self,width=10)
        title.insert(0,self.controller.current_entry[1])                                  #change title
        title.pack(pady=10)

        tb.Label(self, text="entry:").pack(pady=10)
        text=tb.ScrolledText(self,wrap=tb.WORD,width=40,height=10)                                            #allow for journal entry editing with wrapped words
        text.insert(tb.END,self.controller.current_entry[2])
        text.pack(expand=True,fill="both",padx=10,pady=10)                                                      #change text
        tb.Button(self,text="save changes",command=lambda: self.edit_entry(title,text)).pack(pady=10)
        tb.Button(self,text="back",command=lambda: self.controller.show_frame("ViewHistory")).pack(side=tk.RIGHT,padx=10,pady=10)
        

    def edit_entry(self,title_entry,text_entry):
        title=title_entry.get()
        text=text_entry.get("1.0",tb.END)                   #retrieve text
        id=self.controller.current_entry[0]

        if title and text and date:
            db=sqlc.connect("notes.db")
            cursor=db.cursor()
            cursor.execute(f"PRAGMA key = '{self.controller.key}'")         #decrypt db

            query="UPDATE entries SET title=?,entry=? WHERE id=?"
            cursor.execute(query,(title,text,id))
            db.commit()
            db.close()                                                  #update db
            self.controller.show_frame("ViewHistory")                              




class AddEntry(tb.Frame):
    def __init__(self,master,controller):
        super().__init__(master)
        self.controller=controller

    def refresh(self):

        for widget in self.winfo_children():
            widget.destroy()                                                                   #clear prior widgets

        tb.Label(self,text="create entry",font=("Helvetica",15)).pack(pady=10)

        title_entry=tb.Entry(self,width=10)
        title_entry.insert(0,"title")
        title_entry.pack(pady=10)
        text_entry=tb.ScrolledText(self,wrap=tb.WORD,width=40,height=10)                                            #allow for journal entry editing with wrapped words
        text_entry.pack(expand=True,fill="both",padx=10,pady=10)                                


        button_frame=tb.Frame(self)
        button_frame.pack(fill="x",pady=10)
        tb.Button(button_frame,text="save",command=lambda:self.save_entry(title_entry,text_entry)).pack(padx=10)
        tb.Button(button_frame,text="cancel",command=lambda:self.controller.show_frame("Dashboard")).pack(side=tb.RIGHT,padx=10,pady=10)

    def save_entry(self,title_entry,text_entry):

        title=title_entry.get()
        text=text_entry.get("1.0",tb.END)                       #retrieve text
        date = datetime.now().strftime("%Y-%m-%d")

        if title and text:
            db=sqlc.connect("notes.db")
            cursor=db.cursor()
            cursor.execute(f"PRAGMA key = '{self.controller.key}'")                    #decrypt db
            query="INSERT INTO entries (title,entry,date) VALUES (?,?,?)"
            cursor.execute(query,(title,text,date))                                         #update db
            db.commit()
            db.close()
            self.controller.show_frame("Dashboard")


    


class SetupPage(tb.Frame):
    def __init__(self,master,controller):
        super().__init__(master)
        self.controller=controller

        if not os.path.exists("notes.db"):                                                   #setup not completed

            setup_frame=tb.Frame(self)
            setup_frame.pack(pady=10,expand=True,fill="both")

            tb.Label(setup_frame,text="setup",font=("Helvetica",25)).pack(pady=10)

            tb.Label(setup_frame,text="please set a decryption key",font=("Helvetica",10)).pack(pady=10)
            key_entry=tb.Entry(setup_frame,width=10,show="*")        #key entry with hidden characters
            key_entry.pack(pady=10)

            tb.Button(setup_frame,text="complete setup",command=lambda:self.setup(key_entry)).pack(pady=10)

        else:                                                           #key exists
            
            decrypt_frame=tb.Frame(self)
            decrypt_frame.pack(pady=10,expand=True,fill="both")

            tb.Label(decrypt_frame,text="noted.",font=("Helvetica",25)).pack(pady=10)
            tb.Label(decrypt_frame,text="welcome back",font=("Helvetica",15)).pack(pady=10)

            tb.Label(decrypt_frame,text="enter key",font=("Helvetica",10)).pack(padx=10,pady=5)
            key_entry=tb.Entry(decrypt_frame,width=10,show="*")        #key entry with hidden characters
            key_entry.pack(padx=10,pady=5)

            tb.Button(decrypt_frame,text="unlock",command=lambda:self.decrypt(key_entry)).pack(pady=10)
    
    def decrypt(self,key_entry):
        key=key_entry.get()

        try:
            db=sqlc.connect("notes.db")
            cursor=db.cursor()  
            cursor.execute(f"PRAGMA key = '{key}'")                 #decrypt db
            cursor.execute("SELECT * FROM canary")                  #test for correct decryption
            cursor.fetchone()
            db.close()
            self.controller.key=key                                 #track key
            self.controller.show_frame("Dashboard")
        except sqlc.DatabaseError:                                  #if incorrect value
            messagebox.show_error("Invalid key","Error")

    
    def setup(self,key_entry):
        key=key_entry.get()
        db=sqlc.connect("notes.db")                                 #create new db
        cursor=db.cursor()
        cursor.execute(f"PRAGMA key = '{key}'")                     #set encryption key
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            entry TEXT NOT NULL,
            date INTEGER NOT NULL
        )           
        """)                                    #create db for entries
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS canary(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cval TEXT NOT NULL
        )
        """
        )                                       #create canary value for testing key
        cursor.execute("INSERT INTO canary (id,cval) VALUES (?,?)",(1,"canary"))
        db.commit()
        db.close()
        self.controller.key=key                  #track key
        self.controller.show_frame("Dashboard")



class AppClass(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("noted.")
        self.geometry("800x600")

        #create window
        pages=tb.Frame(self)
        pages.pack(fill="both",expand=True)                 #allow widgets to fit page accordingly
        
        self.frames={}                                      #create frame container

        for Page in (Dashboard,ViewHistory,AddEntry,ViewEntry,SetupPage):
            page_name=Page.__name__
            frame=Page(master=pages,controller=self)
            self.frames[page_name]=frame
            frame.grid(row=0,column=0,sticky="nsew")        #allow for expansion to fill container

        #make pages resize
        pages.grid_rowconfigure(0,weight=1)
        pages.grid_columnconfigure(0,weight=1)

        self.show_frame("SetupPage")                        #launch app on setup
    
    def show_frame(self,page_name):
        frame=self.frames[page_name]
        frame.tkraise()                                     #raise page to front
        if hasattr(frame,"refresh"):        
            frame.refresh()                                 #ensure page has latest data      
    
    key=None
    current_entry=None

if(__name__=="__main__"):
    app=AppClass()
    app.mainloop()