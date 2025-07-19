import psutil
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter.font as tkFont
import threading

class ModernTaskManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager Base")
        self.geometry("1400x900")
        self.configure(bg='#f5f6f7')
        self.sort_changed = False
        self.pause_refresh = False
        self.current_theme = "light"
               
        # Custom fonts
        self.title_font = tkFont.Font(family='DejaVu Sans', size=14, weight='bold')
        self.text_font = tkFont.Font(family='DejaVu Sans', size=10)
        self.button_font = tkFont.Font(family='DejaVu Sans', size=10, weight='bold')
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # System info
        self.current_user = psutil.Process().username()
        self.cpu_count = psutil.cpu_count()
        self.mem_total = round(psutil.virtual_memory().total / (1024**3), 1)
        
        # Data structures
        self.columns = ("PID", "Name", "User", "CPU%", "Memory", "Status")
        self.process_cache = []
        self.graph_data = {'cpu': [], 'mem': [], 'disk': [], 'network': []}
        self.update_interval = 100        
        # UI Elements
        self.create_main_frame()
        self.create_header()
        self.create_control_panel()
        self.create_process_table()
        self.create_graph_panel()
        self.create_status_bar()
        self.apply_theme()
        
        # Initial data load
        self.update_data()
        
        # Window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_styles(self):
        """Configure modern ttk styles"""
        self.style.configure('TFrame', background='#f5f6f7')
        self.style.configure('Header.TFrame', background='#2c3e50')
        self.style.configure('Title.TLabel', 
                          font=self.title_font, 
                          foreground='white',
                          background='#2c3e50')
        self.style.configure('Card.TFrame', 
                           background='white',
                           relief=tk.RAISED,
                           borderwidth=1)
        self.style.configure('Treeview', 
                           font=self.text_font,
                           rowheight=25,
                           fieldbackground='white',
                           background='white')
        self.style.configure('Treeview.Heading', 
                           font=self.button_font,
                           background='#34495e',
                           foreground='white',
                           relief=tk.FLAT)
        self.style.map('Treeview', 
                     background=[('selected', '#3498db')],
                     foreground=[('selected', 'white')])
        self.style.configure('TButton', 
                           font=self.button_font,
                           padding=6,
                           background='#3498db',
                           foreground='white')
        self.style.map('TButton',
                     background=[('active', '#2980b9')])
        self.style.configure('Accent.TButton',
                           background='#e74c3c')
        self.style.map('Accent.TButton',
                     background=[('active', '#c0392b')])

    def apply_theme(self):
        if self.current_theme == "light":
            # Light mode
            self.configure(bg='#f5f6f7')
            self.style.configure('TFrame', background='#f5f6f7')
            self.style.configure('Header.TFrame', background='#2c3e50')
            self.style.configure('Title.TLabel', background='#2c3e50', foreground='white')
            self.style.configure('Card.TFrame', background='white')
            self.style.configure('Treeview', background='white', fieldbackground='white', foreground='black')
            self.style.configure('Treeview.Heading', background='#34495e', foreground='white')
            self.fig.set_facecolor('#f5f6f7')
            self.plot_bg_color = '#ffffff'
        else:
            # Dark mode
            self.configure(bg='#1e1e1e')
            self.style.configure('TFrame', background='#1e1e1e')
            self.style.configure('Header.TFrame', background='#111111')
            self.style.configure('Title.TLabel', background='#111111', foreground='white')
            self.style.configure('Card.TFrame', background='#2a2a2a')
            self.style.configure('Treeview', background='#2e2e2e', fieldbackground='#2e2e2e', foreground='white')
            self.style.configure('Treeview.Heading', background='#555555', foreground='white')
            self.fig.set_facecolor('#1e1e1e')
            self.plot_bg_color = '#2e2e2e'

        # Cập nhật biểu đồ
        self.configure_all_plots()
        self.canvas.draw()

    def configure_all_plots(self):
        for ax in [self.ax_cpu, self.ax_mem, self.ax_disk, self.ax_network]:
            ax.set_facecolor(self.plot_bg_color)
            ax.grid(True, linestyle=':', alpha=0.7)
            ax.tick_params(labelsize=8, colors='white' if self.current_theme == "dark" else 'black')
            for spine in ax.spines.values():
                spine.set_color('white' if self.current_theme == "dark" else 'black')

    def create_main_frame(self):
        """Create main container with modern card layout"""
        self.main_frame = ttk.Frame(self, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_header(self):
        """Create modern header with system info"""
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame', height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # App title
        title_label = ttk.Label(header_frame, 
                              text="Task Manager", 
                              style='Title.TLabel')
        title_label.pack(side=tk.LEFT, padx=20)
        
        # System info
        sys_info = ttk.Frame(header_frame, style='Header.TFrame')
        sys_info.pack(side=tk.RIGHT, padx=20)
        
        ttk.Label(sys_info, 
                 text=f"CPU: {self.cpu_count} | Memory: {self.mem_total}GB",
                 style='Title.TLabel').pack()

    def create_control_panel(self):
        """Create modern control panel with search and actions"""
        control_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 10), ipady=5)
        
        # Search panel
        search_frame = ttk.Frame(control_frame, style='TFrame')
        search_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:", font=self.text_font).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var, 
                               width=30,
                               font=self.text_font)
        search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace_add("write", lambda *_: self.update_processes())
        
        # Filter panel
        filter_frame = ttk.Frame(control_frame, style='TFrame')
        filter_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filter:", font=self.text_font).pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, 
                                   textvariable=self.filter_var,
                                   values=["All", "Your", "Non-root", "Running"],
                                   width=12,
                                   state="readonly",
                                   font=self.text_font)
        filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_var.trace_add("write", lambda *_: self.update_processes())
        
        # Sort panel
        sort_frame = ttk.Frame(control_frame, style='TFrame')
        sort_frame.pack(side=tk.LEFT, padx=10, pady=5)

        ttk.Label(sort_frame, text="Sort by:", font=self.text_font).pack(side=tk.LEFT)

        self.sort_var = tk.StringVar(value="Default")
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=["Default", "Name A-Z", "Name Z-A", "Memory Min-Max", "Memory Max-Min", "CPU Min-Max", "CPU Max-Min"],
            width=18,
            state="readonly",
            font=self.text_font
        )
        sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_var.trace_add("write", self.on_sort_changed)

        # Action buttons
        button_frame = ttk.Frame(control_frame, style='TFrame')
        button_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(button_frame, 
                  text="Kill Process", 
                  command=self.kill_process,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, 
                  text="Refresh", 
                  command=self.refresh_process_data_async).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, 
                  text="Details", 
                  command=self.show_process_details).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, 
                  text="Theme", 
                  command=self.toggle_theme).pack(side=tk.LEFT, padx=2)


    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def format_cpu(self, cpu_val):
        if cpu_val > 30:
            return f"🔥 {cpu_val:.1f}%"
        elif cpu_val > 20:
            return f"⚠️ {cpu_val:.1f}%"
        elif cpu_val > 10:
            return f"🟡 {cpu_val:.1f}%"
        else:
            return f"{cpu_val:.1f}%"

    def on_sort_changed(self, *args):
        self.sort_changed = True
        self.update_processes()

    def create_process_table(self):
        """Create modern process table with better styling"""
        table_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.notebook = ttk.Notebook(table_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        #Tab
        self.apps_frame = ttk.Frame(self.notebook)
        self.background_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.apps_frame, text="Apps")
        self.notebook.add(self.background_frame, text="Background Processes")

        #Treeview cho mỗi tab
        self.tree_apps = self.create_treeview(self.apps_frame)
        self.tree_bg = self.create_treeview(self.background_frame)
        
    def create_treeview(self, parent):
        tree = ttk.Treeview(parent, columns=self.columns, show="headings", style='Treeview')
        tree.bind("<<TreeviewSelect>>", self.on_row_selected)


        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        col_widths = {"PID": 80, "Name": 180, "User": 120, "CPU%": 80, "Memory": 100, "Status": 100}
        for col in self.columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 100), anchor=tk.W)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        return tree


    def on_row_selected(self, event):
        """Tạm dừng auto-refresh khi người dùng chọn dòng"""
        self.pause_refresh = True
        self.status_var.set("Đã tạm dừng refresh trong 5 giây để thao tác")
        self.after(5000, self.resume_refresh)  # Resume sau 5 giây

    def resume_refresh(self):
        """Tiếp tục auto-refresh sau khi pause"""
        self.pause_refresh = False
        self.status_var.set("Auto refresh được bật lại")

    def create_graph_panel(self):
        """Create modern graph panel with matplotlib"""
        graph_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create figure with dark theme
        plt.style.use('seaborn-v0_8')
        self.fig = Figure(figsize=(12, 4), dpi=100, facecolor='#f5f6f7')
        
        # Create subplots
        self.ax_cpu = self.fig.add_subplot(141)
        self.ax_mem = self.fig.add_subplot(142)
        self.ax_disk = self.fig.add_subplot(143)
        self.ax_network = self.fig.add_subplot(144)
        
        # Configure plots
        self.configure_plot(self.ax_cpu, "CPU Usage", "%", '#3498db')
        self.configure_plot(self.ax_mem, "Memory Usage", "%", '#2ecc71')
        self.configure_plot(self.ax_disk, "Disk Usage", "%", '#e74c3c')
        self.configure_plot(self.ax_network, "Network", "MB/s", '#9b59b6')
        
        # Create lines
        self.cpu_line, = self.ax_cpu.plot([], [], lw=2)
        self.mem_line, = self.ax_mem.plot([], [], lw=2)
        self.disk_line, = self.ax_disk.plot([], [], lw=2)
        self.network_line, = self.ax_network.plot([], [], lw=2)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def configure_plot(self, ax, title, ylabel, color):
        """Configure individual plot appearance"""
        ax.set_title(title, fontsize=10, pad=10)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_facecolor('#ffffff')
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.tick_params(labelsize=8)
        
        # Set colors
        for spine in ax.spines.values():
            spine.set_color(color)
        ax.title.set_color(color)
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis='y', colors=color)

    def create_status_bar(self):
        """Create modern status bar"""
        status_frame = ttk.Frame(self.main_frame, style='Header.TFrame', height=30)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, 
                 textvariable=self.status_var,
                 style='Title.TLabel').pack(side=tk.LEFT, padx=10)
        
        self.clock_var = tk.StringVar()
        ttk.Label(status_frame, 
                 textvariable=self.clock_var,
                 style='Title.TLabel').pack(side=tk.RIGHT, padx=10)
        
        self.update_clock()

    def update_clock(self):
        """Update clock in status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_var.set(current_time)
        self.after(1000, self.update_clock)

    def update_data(self):
        def worker():
            if not self.pause_refresh:
                try:
                    self.update_processes()
                    self.update_graphs()
                except Exception as e:
                    self.status_var.set(f"Error: {str(e)}")
            self.after(self.update_interval, self.update_data)

        threading.Thread(target=worker, daemon=True).start()


    def refresh_process_data_async(self):
        """Chạy refresh từ background thread và cập nhật trạng thái"""
        self.status_var.set("Refreshing...")
        threading.Thread(target=self.safe_update_processes, daemon=True).start()

    def safe_update_processes(self):
        """Thực thi update_processes() và cập nhật trạng thái khi xong"""
        try:
            self.update_processes()
        except Exception as e:
            self.status_var.set(f"Error during refresh: {e}")
        else:
            self.status_var.set("Refreshed at " + datetime.now().strftime("%H:%M:%S"))

    def update_processes(self):
        self.process_apps = []
        self.process_background = []
        self.app_rows_cache = {}
        self.bg_rows_cache = {}
        self.access_denied_count = 0


        cpu_count = psutil.cpu_count(logical=True)

        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info', 'status']):
            try:
                info = proc.info
                if info['pid'] == 0 or not self.should_show(info):
                    continue

                mem_mb = info['memory_info'].rss // (1024 ** 2)
                cpu_percent_normalized = min(info['cpu_percent'] / cpu_count, 100.0)

                proc_data = {
                    'pid': info['pid'],
                    'name': info['name'],
                    'user': info['username'],
                    'cpu%': cpu_percent_normalized,
                    'memory': f"{mem_mb} MB",
                    'status': info['status']
                }

                if (
                    info['username'] == self.current_user and
                    info['status'] == psutil.STATUS_RUNNING and
                    not info['name'].lower().startswith(("system", "idle", "svchost"))
                ):
                    self.process_apps.append(proc_data)
                else:
                    self.process_background.append(proc_data)

            except psutil.AccessDenied:
                self.access_denied_count += 1
                continue
            except psutil.NoSuchProcess:
                continue


        # Sắp xếp theo yêu cầu
        def mem_to_int(mem_str):
            return int(mem_str.split()[0]) if mem_str else 0

        sort_mode = self.sort_var.get()

        if sort_mode == "Name A-Z":
            self.process_apps.sort(key=lambda x: x['name'].lower())
            self.process_background.sort(key=lambda x: x['name'].lower())
        elif sort_mode == "Name Z-A":
            self.process_apps.sort(key=lambda x: x['name'].lower(), reverse=True)
            self.process_background.sort(key=lambda x: x['name'].lower(), reverse=True)
        elif sort_mode == "Memory Min-Max":
            self.process_apps.sort(key=lambda x: mem_to_int(x['memory']))
            self.process_background.sort(key=lambda x: mem_to_int(x['memory']))
        elif sort_mode == "Memory Max-Min":
            self.process_apps.sort(key=lambda x: mem_to_int(x['memory']), reverse=True)
            self.process_background.sort(key=lambda x: mem_to_int(x['memory']), reverse=True)
        elif sort_mode == "CPU Min-Max":
            self.process_apps.sort(key=lambda x: x['cpu%'])
            self.process_background.sort(key=lambda x: x['cpu%'])
        elif sort_mode == "CPU Max-Min":
            self.process_apps.sort(key=lambda x: x['cpu%'], reverse=True)
            self.process_background.sort(key=lambda x: x['cpu%'], reverse=True)


        # Cập nhật Treeview
        if self.sort_changed:
            self.refresh_treeview(full_refresh=True)
            self.sort_changed = False
        else:
            self.refresh_treeview(full_refresh=False)

        total = len(self.process_apps) + len(self.process_background)
        status = (
            f"Apps: {len(self.process_apps)} | Background: {len(self.process_background)} | "
            f"Total: {total} | Access Denied: {self.access_denied_count} | "
            f"Last update: {datetime.now().strftime('%H:%M:%S')}"
        )

        if self.access_denied_count > 10:
            status += " | Tip: Chạy bằng sudo để xem tất cả tiến trình."

        self.status_var.set(status)





    def should_show(self, proc_info):
        """Filter processes based on current settings"""
        filter_mode = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        if search_text and search_text not in proc_info['name'].lower():
            return False
        
        filter_conditions = {
            "All": True,
            "Your": proc_info['username'] == self.current_user,
            "Non-root": proc_info['username'] != "root",
            "Running": proc_info['status'] == psutil.STATUS_RUNNING
        }
        
        return filter_conditions.get(filter_mode, True)

    def refresh_treeview(self, full_refresh=False):
        if full_refresh:
            self.full_refresh_treeview(self.tree_apps, self.process_apps)
            self.full_refresh_treeview(self.tree_bg, self.process_background)
        else:
            self.smart_refresh_treeview(self.tree_apps, self.process_apps, self.app_rows_cache)
            self.smart_refresh_treeview(self.tree_bg, self.process_background, self.bg_rows_cache)


    def full_refresh_treeview(self, tree, data_list):
        yview = tree.yview()
        tree.delete(*tree.get_children())
        for proc in data_list:
            row_values = (
                proc['pid'], proc['name'], proc['user'],
                self.format_cpu(proc['cpu%']), proc['memory'], proc['status']
            )
            tree.insert("", "end", values=row_values)
        tree.yview_moveto(yview[0])

    def smart_refresh_treeview(self, tree, data_list, cache_dict):
        yview = tree.yview()  # Giữ lại vị trí cuộn

        # Xóa toàn bộ nội dung cũ
        tree.delete(*tree.get_children())
        cache_dict.clear()

        # Thêm lại theo đúng thứ tự đã sắp xếp
        for proc in data_list:
            row_values = (
                proc['pid'], proc['name'], proc['user'],
                self.format_cpu(proc['cpu%']), proc['memory'], proc['status']
            )
            tree.insert("", "end", values=row_values)
            cache_dict[proc['pid']] = row_values

        tree.yview_moveto(yview[0])



    def update_graphs(self):
            """Cập nhật biểu đồ giống Task Manager"""
            try:
                # CPU: % sử dụng toàn bộ
                cpu = psutil.cpu_percent()

                # RAM: % sử dụng
                mem = psutil.virtual_memory().percent

                # Disk: tổng I/O MB/s
                disk_io = psutil.disk_io_counters()
                if hasattr(self, 'last_disk_io'):
                    delta_read = disk_io.read_bytes - self.last_disk_io.read_bytes
                    delta_write = disk_io.write_bytes - self.last_disk_io.write_bytes
                    disk_rate = (delta_read + delta_write) / (1024 ** 2)  # MB/s
                else:
                    disk_rate = 0
                self.last_disk_io = disk_io

                # Network: tải về (recv) MB/s
                current_net = psutil.net_io_counters()
                if hasattr(self, 'last_network'):
                    net_speed = (current_net.bytes_recv - self.last_network.bytes_recv) / (1024 ** 2)
                else:
                    net_speed = 0
                self.last_network = current_net

                # Cập nhật dữ liệu
                for key, val in zip(['cpu', 'mem', 'disk', 'network'], [cpu, mem, disk_rate, net_speed]):
                    self.graph_data[key].append(val)
                    if len(self.graph_data[key]) > 60:
                        self.graph_data[key] = self.graph_data[key][-60:]

                # Vẽ biểu đồ
                for ax, line, data, color in [
                    (self.ax_cpu, self.cpu_line, self.graph_data['cpu'], '#3498db'),
                    (self.ax_mem, self.mem_line, self.graph_data['mem'], '#2ecc71'),
                    (self.ax_disk, self.disk_line, self.graph_data['disk'], '#e74c3c'),
                    (self.ax_network, self.network_line, self.graph_data['network'], '#9b59b6')
                ]:
                    line.set_data(range(len(data)), data)
                    line.set_color(color)
                    ax.relim()
                    ax.autoscale_view()

                self.canvas.draw()

            except Exception as e:
                print(f"Graph error: {e}")



    def kill_process(self):
        """Kill selected process từ tab hiện tại"""
        current_tab = self.notebook.index(self.notebook.select())
        tree = self.tree_apps if current_tab == 0 else self.tree_bg

        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a process first")
            return

        item = tree.item(selected[0], 'values')
        pid = int(item[0])
        name = item[1]

        if messagebox.askyesno("Confirm", f"Bạn có muốn kết thúc tiến trình \"{name}\" (PID {pid})?"):
            try:
                proc = psutil.Process(pid)
                proc.terminate()

                # Đợi tiến trình kết thúc tối đa 3 giây
                gone, alive = psutil.wait_procs([proc], timeout=3)

                if alive:
                    self.status_var.set(f"Tiến trình {name} không phản hồi, thử kill mạnh...")
                    try:
                        proc.kill()
                        gone, alive = psutil.wait_procs([proc], timeout=2)
                        if alive:
                            messagebox.showerror("Error", f"Không thể kết thúc tiến trình {name} (PID {pid})")
                        else:
                            self.status_var.set(f"Đã kill mạnh tiến trình {name} (PID {pid})")
                    except Exception as kill_err:
                        messagebox.showerror("Error", f"Kill thất bại: {kill_err}")
                else:
                    self.status_var.set(f"Đã kết thúc tiến trình {name} (PID {pid})")

            except psutil.NoSuchProcess:
                messagebox.showinfo("Info", "Tiến trình đã không còn tồn tại.")
            except psutil.AccessDenied:
                messagebox.showerror("Permission Denied", "Bạn không có quyền kết thúc tiến trình này.\n"
                                                        "Hãy thử chạy chương trình với quyền sudo nếu cần.")
            except Exception as e:
                messagebox.showerror("Error", f"Lỗi khi kết thúc tiến trình: {e}")

            # Cập nhật lại danh sách tiến trình
            self.refresh_process_data_async()




    def show_process_details(self, event=None):
        """Show details for selected process từ tab hiện tại"""
        current_tab = self.notebook.index(self.notebook.select())
        tree = self.tree_apps if current_tab == 0 else self.tree_bg

        selected = tree.selection()
        if selected:
            pid = int(tree.item(selected[0], 'values')[0])
            ProcessDetailWindow(self, pid)


    def on_close(self):
        """Handle window close event"""
        plt.close('all')
        self.destroy()

class ProcessDetailWindow(tk.Toplevel):
    def __init__(self, master, pid):
        super().__init__(master)
        self.title(f"Process Details - PID: {pid}")
        self.geometry("1000x700")
        
        try:
            self.proc = psutil.Process(pid)
            self.create_widgets()
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "Process no longer exists")
            self.destroy()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # General Info Tab
        gen_frame = ttk.Frame(notebook)
        self.create_general_info(gen_frame)
        notebook.add(gen_frame, text="General")
        
        # Memory Info Tab
        mem_frame = ttk.Frame(notebook)
        self.create_memory_info(mem_frame)
        notebook.add(mem_frame, text="Memory")
        
        # Connections Tab
        conn_frame = ttk.Frame(notebook)
        self.create_connections(conn_frame)
        notebook.add(conn_frame, text="Connections")

    def create_general_info(self, parent):
        tree = ttk.Treeview(parent, columns=("Property", "Value"), show="headings")
        tree.heading("Property", text="Property")
        tree.heading("Value", text="Value")
        
        try:
            info = self.proc.as_dict()
            for key, value in info.items():
                if isinstance(value, (list, dict)):
                    value = str(value)
                tree.insert("", "end", values=(key, value))
        except psutil.AccessDenied:
            tree.insert("", "end", values=("Error", "Access denied"))
            
        tree.pack(fill=tk.BOTH, expand=True)

    def create_memory_info(self, parent):
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        
        try:
            mem_info = self.proc.memory_full_info()
            for attr in dir(mem_info):
                if not attr.startswith('_'):
                    value = getattr(mem_info, attr)
                    text.insert(tk.END, f"{attr}: {value}\n\n")
        except psutil.AccessDenied:
            text.insert(tk.END, "Access denied to memory information")
        
        text.config(state=tk.DISABLED)

    def create_connections(self, parent):
        tree = ttk.Treeview(parent, columns=("FD", "Family", "Type", "Local", "Remote", "Status"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        
        try:
            conns = self.proc.connections()
            for conn in conns:
                tree.insert("", "end", values=(
                    conn.fd,
                    conn.family,
                    conn.type,
                    f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                    f"{conn.raddr.ip}:{conn.raddr.port}" if hasattr(conn, 'raddr') and conn.raddr else "",
                    conn.status
                ))
        except psutil.AccessDenied:
            tree.insert("", "end", values=("Access denied", "", "", "", "", ""))
            
        tree.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = ModernTaskManager()
    app.mainloop()
