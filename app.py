"""Launch: python3 app.py | Headless report: python3 app.py --report"""
import argparse
from pathlib import Path
from core import START, END, analyze, connect, export_csv, money, seed


def launch():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root=tk.Tk()
    root.title('Campus Stock | Sales & inventory')
    root.geometry('1100x820')
    root.minsize(780,650)
    root.configure(bg='#102234')
    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame',background='#102234')
    style.configure('TLabel',background='#102234',foreground='#eef5fb',font=('Helvetica',14))
    style.configure('Title.TLabel',font=('Helvetica',28,'bold'))
    style.configure('Metric.TLabel',font=('Helvetica',24,'bold'),foreground='#63dec6')
    style.configure('TButton',font=('Helvetica',13),padding=8)
    style.configure('Treeview',font=('Helvetica',13),rowheight=30,background='#ffffff',fieldbackground='#ffffff',foreground='#102234')
    style.configure('Treeview.Heading',font=('Helvetica',13,'bold'),padding=7)
    style.map('Treeview',background=[('selected','#135d72')],foreground=[('selected','white')])
    main=ttk.Frame(root,padding=22)
    main.pack(fill='both',expand=True)
    ttk.Label(main,text='Campus Stock',style='Title.TLabel').pack(anchor='w')
    ttk.Label(main,text='Sales & inventory  /  SIMULATED DATA · Jan–Jun 2026').pack(anchor='w',pady=(3,16))
    filters=ttk.Frame(main)
    filters.pack(fill='x')
    start=tk.StringVar(value=START); end=tk.StringVar(value=END)
    category=tk.StringVar(value='All categories')
    for col,(label,var) in enumerate([('From (YYYY-MM-DD)',start),('To (YYYY-MM-DD)',end)]):
        ttk.Label(filters,text=label).grid(row=0,column=col,sticky='w',padx=(0,12))
        ttk.Entry(filters,textvariable=var,width=19,font=('Helvetica',14)).grid(row=1,column=col,sticky='w',padx=(0,12),pady=6)
    ttk.Label(filters,text='Category').grid(row=0,column=2,sticky='w')
    ttk.Combobox(filters,textvariable=category,state='readonly',width=18,font=('Helvetica',14),
                 values=['All categories','Stationery','Technology','Essentials']).grid(row=1,column=2,padx=(0,12))
    metrics=ttk.Frame(main,padding=(0,18))
    metrics.pack(fill='x')
    metric_labels=[]
    for i,title in enumerate(['Revenue','Gross profit','Units sold','Reorder alerts']):
        metrics.columnconfigure(i,weight=1)
        box=ttk.Frame(metrics)
        box.grid(row=0,column=i,sticky='w')
        ttk.Label(box,text=title).pack(anchor='w')
        value=ttk.Label(box,text='—',style='Metric.TLabel')
        value.pack(anchor='w',pady=5)
        metric_labels.append(value)
    ttk.Label(main,text='Monthly revenue').pack(anchor='w')
    chart=tk.Canvas(main,height=135,bg='#172f43',highlightthickness=0)
    chart.pack(fill='x',pady=(8,16))
    notebook=ttk.Notebook(main)
    notebook.pack(fill='both',expand=True)

    def table(title,columns):
        frame=ttk.Frame(notebook,padding=8)
        notebook.add(frame,text=title)
        tree=ttk.Treeview(frame,columns=[c[0] for c in columns],show='headings',height=7)
        for key,label,width in columns:
            tree.heading(key,text=label)
            tree.column(key,width=width,minwidth=70,anchor='w' if key in ('name','supplier') else 'center')
        scrollbar=ttk.Scrollbar(frame,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right',fill='y')
        tree.pack(fill='both',expand=True)
        return tree

    products=table(' Product performance ',[('name','Product',210),('category','Category',120),('units','Units',80),('revenue','Revenue',120),('profit','Gross profit',120)])
    inventory=table(' Inventory & reorder ',[('name','Product',200),('on_hand','On hand',85),('point','Reorder at',90),('status','Status',110),('supplier','Supplier',180)])
    ttk.Label(main,text='Inventory reflects all demo sales through June 30, regardless of date filter.',font=('Helvetica',12)).pack(anchor='w',pady=(12,0))
    state={}

    def draw(event=None):
        chart.delete('all')
        rows=state.get('trend',[])
        width=max(chart.winfo_width(),300)
        if not rows:
            chart.create_text(width/2,65,text='No sales in this period',fill='white',font=('Helvetica',14))
            return
        peak=max(r['revenue_cents'] for r in rows) or 1
        step=(width-32)/len(rows)
        for i,r in enumerate(rows):
            x=16+i*step
            h=70*r['revenue_cents']/peak
            chart.create_rectangle(x+8,100-h,x+step-8,100,fill='#63dec6',outline='')
            chart.create_text(x+step/2,112,text=r['month'],fill='#eef5fb',font=('Helvetica',12))
            chart.create_text(x+step/2,90-h,text=money(r['revenue_cents']),fill='#eef5fb',font=('Helvetica',12))

    def refresh():
        try:
            with connect() as db:
                result=analyze(db,start.get(),end.get(),category.get())
        except ValueError as exc:
            messagebox.showerror('Check dates',str(exc))
            return
        state.clear(); state.update(result)
        alerts=sum(r['on_hand']<=r['reorder_point'] for r in result['inventory'])
        for label,value in zip(metric_labels,[money(result['revenue']),money(result['profit']),f"{result['units']:,}",str(alerts)]):
            label.configure(text=value)
        for tree in (products,inventory):
            tree.delete(*tree.get_children())
        for p in result['products']:
            products.insert('','end',values=(p['name'],p['category'],p['units'],money(p['revenue_cents']),money(p['profit_cents'])))
        for p in result['inventory']:
            status='Out of stock' if p['on_hand']==0 else 'Reorder' if p['on_hand']<=p['reorder_point'] else 'In stock'
            inventory.insert('','end',values=(p['name'],p['on_hand'],p['reorder_point'],status,p['supplier']))
        draw()

    def export():
        path=filedialog.asksaveasfilename(title='Export displayed product results',defaultextension='.csv',initialfile='product_performance.csv',filetypes=[('CSV','*.csv')])
        if path:
            try:
                export_csv(state['products'],path)
            except OSError as exc:
                messagebox.showerror('Export failed',str(exc))
                return
            messagebox.showinfo('Export complete','Saved product results. Money columns are integer cents.')
    ttk.Button(filters,text='Apply',command=refresh).grid(row=1,column=3,padx=(0,8))
    ttk.Button(filters,text='Export CSV',command=export).grid(row=1,column=4)
    chart.bind('<Configure>',draw)
    refresh()
    root.mainloop()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Campus Stock: simulated retail analytics')
    parser.add_argument('--report',action='store_true',help='Print a report without opening a window')
    args=parser.parse_args()
    seed()
    if args.report:
        with connect() as db:
            r=analyze(db)
        print('CAMPUS STOCK — SIMULATED DATA | '+START+' to '+END)
        print('Revenue:',money(r['revenue']),'| Gross profit:',money(r['profit']),'| Units:',r['units'])
        print('\nPRODUCT PERFORMANCE')
        for p in r['products']:
            print(f"{p['name']:22} {p['units']:4} units  {money(p['revenue_cents']):>12}")
        print('\nREORDER ALERTS (ending inventory)')
        for p in r['inventory']:
            if p['on_hand']<=p['reorder_point']:
                print(f"{p['name']:22} {p['on_hand']:4} left; reorder point {p['reorder_point']}")
    else:
        launch()
