import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class OptionAnalyticsUI:
    """
    View class for the Option Analytics Application.
    Handles all Tkinter widget creation and layout.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Option Analytics")
        self.root.geometry("1100x750")
        
        # Apply Theme
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Main Tab Control
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: Pricing Dashboard
        self.tab_pricing = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pricing, text='Pricing Dashboard')
        
        # Tab 2: Sensitivity Analysis
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text='Sensitivity Analysis')
        
        # Initialize Widgets
        self.entries = {} # Store input widgets
        self.labels = {}  # Store output label widgets
        
        self.setup_dashboard()
        self.setup_analysis()

    def setup_dashboard(self):
        """Builds the Pricing Dashboard (Tab 1)"""
        # Split into Left (Inputs) and Right (Outputs)
        paned = ttk.PanedWindow(self.tab_pricing, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        frame_inputs = ttk.Frame(paned, width=400)
        frame_outputs = ttk.Frame(paned)
        paned.add(frame_inputs, weight=1)
        paned.add(frame_outputs, weight=2)
        
        # --- Input Section ---
        # Market Data Group
        lf_market = ttk.LabelFrame(frame_inputs, text="Market Data", padding=10)
        lf_market.pack(fill='x', padx=5, pady=5)
        
        self._create_input(lf_market, "Spot Price ($):", "S", 0)
        self._create_input(lf_market, "Volatility (%):", "sigma", 1)
        self._create_input(lf_market, "Risk-Free Rate (%):", "r", 2)
        self._create_input(lf_market, "Div Yield / Foreign Rate (%):", "q", 3)
        
        # Contract Specs Group
        lf_contract = ttk.LabelFrame(frame_inputs, text="Contract Specifications", padding=10)
        lf_contract.pack(fill='x', padx=5, pady=5)
        
        self._create_input(lf_contract, "Strike Price ($):", "K", 0)
        self._create_input(lf_contract, "Time to Expiration (Days):", "T", 1, suffix="/ 365 years")
        
        # Calculate Button
        self.btn_calc = ttk.Button(frame_inputs, text="Calculate Prices & Greeks")
        self.btn_calc.pack(fill='x', padx=5, pady=20)
        
        # --- Output Section ---
        # Grid Layout for Results
        frame_results = ttk.Frame(frame_outputs, padding=20)
        frame_results.pack(fill='both', expand=True)
        
        # Headers
        ttk.Label(frame_results, text="Metric", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Label(frame_results, text="Call Option", font=('Arial', 10, 'bold'), foreground='green').grid(row=0, column=1, sticky='e', padx=20, pady=5)
        ttk.Label(frame_results, text="Put Option", font=('Arial', 10, 'bold'), foreground='red').grid(row=0, column=2, sticky='e', padx=20, pady=5)
        
        # Rows
        metrics = [
            ("Theoretical Price", "price", True),
            ("Delta (Δ)", "delta", False),
            ("Gamma (Γ)", "gamma", False),
            ("Vega (ν) [1%]", "vega", False),
            ("Theta (Θ) [Daily]", "theta", False),
            ("Rho (ρ) [1%]", "rho", False)
        ]
        
        for i, (name, key, is_bold) in enumerate(metrics, start=1):
            font_style = ('Arial', 12, 'bold') if is_bold else ('Arial', 10)
            
            ttk.Label(frame_results, text=name, font=font_style).grid(row=i, column=0, sticky='w', pady=5)
            
            lbl_call = ttk.Label(frame_results, text="-", font=font_style)
            lbl_call.grid(row=i, column=1, sticky='e', padx=20)
            self.labels[f"call_{key}"] = lbl_call
            
            lbl_put = ttk.Label(frame_results, text="-", font=font_style)
            lbl_put.grid(row=i, column=2, sticky='e', padx=20)
            self.labels[f"put_{key}"] = lbl_put

            # Gamma and Vega are same for both, but we keep structure
            if key in ['gamma', 'vega']:
                # Optional: Merge cells or keep distinct. Keeping distinct for simplicity.
                pass

    def _create_input(self, parent, label_text, var_name, row, suffix=None):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky='w', pady=5)
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky='ew', padx=5)
        self.entries[var_name] = entry
        if suffix:
            ttk.Label(parent, text=suffix, font=('Arial', 8, 'italic')).grid(row=row, column=2, sticky='w')

    def setup_analysis(self):
        """Builds the Sensitivity Analysis Tab (Tab 2)"""
        # Top Control Bar
        frame_controls = ttk.Frame(self.tab_analysis, padding=10)
        frame_controls.pack(fill='x')
        
        # Target Variable (Y-Axis)
        lf_y = ttk.LabelFrame(frame_controls, text="Y-Axis (Target)", padding=5)
        lf_y.pack(side='left', padx=5, fill='y')
        self.combo_y = ttk.Combobox(lf_y, values=[
            "Call Price", "Put Price", 
            "Call Delta", "Put Delta", 
            "Gamma", "Vega", "Theta", "Rho"
        ], state="readonly")
        self.combo_y.set("Call Price")
        self.combo_y.pack()

        # Independent Variable (X-Axis)
        lf_x = ttk.LabelFrame(frame_controls, text="X-Axis (Varying)", padding=5)
        lf_x.pack(side='left', padx=5, fill='y')
        
        self.combo_x = ttk.Combobox(lf_x, values=["Spot Price", "Volatility", "Time (Days)"], state="readonly", width=15)
        self.combo_x.set("Spot Price")
        self.combo_x.pack(side='left', padx=5)
        
        ttk.Label(lf_x, text="Range:").pack(side='left')
        self.entry_x_start = ttk.Entry(lf_x, width=8); self.entry_x_start.pack(side='left', padx=2)
        ttk.Label(lf_x, text="to").pack(side='left')
        self.entry_x_end = ttk.Entry(lf_x, width=8); self.entry_x_end.pack(side='left', padx=2)
        ttk.Label(lf_x, text="Steps:").pack(side='left')
        self.entry_x_steps = ttk.Entry(lf_x, width=5); self.entry_x_steps.pack(side='left', padx=2)
        self.entry_x_steps.insert(0, "50")

        # Series Variable (Z-Axis)
        lf_z = ttk.LabelFrame(frame_controls, text="Z-Axis (Series)", padding=5)
        lf_z.pack(side='left', padx=5, fill='y')
        
        self.combo_z = ttk.Combobox(lf_z, values=["Volatility", "Time (Days)", "Risk-Free Rate"], state="readonly", width=15)
        self.combo_z.set("Volatility")
        self.combo_z.pack(side='left', padx=5)
        
        ttk.Label(lf_z, text="Start:").pack(side='left')
        self.entry_z_start = ttk.Entry(lf_z, width=6); self.entry_z_start.pack(side='left', padx=2)
        ttk.Label(lf_z, text="Inc:").pack(side='left')
        self.entry_z_inc = ttk.Entry(lf_z, width=6); self.entry_z_inc.pack(side='left', padx=2)

        # Generate Button
        self.btn_graph = ttk.Button(frame_controls, text="Generate Graph")
        self.btn_graph.pack(side='left', padx=20, fill='y')

        # Matplotlib Canvas
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_analysis)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.tab_analysis)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def get_dashboard_inputs(self):
        """Retrieves and validates inputs from Tab 1."""
        try:
            data = {}
            for key, entry in self.entries.items():
                val = entry.get()
                if not val: raise ValueError(f"Missing value for {key}")
                data[key] = float(val)
            return data
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}\nPlease enter numeric values.")
            return None

    def update_dashboard_results(self, results):
        """Updates the results grid in Tab 1."""
        for key, val in results.items():
            # Format based on metric type
            if 'price' in key: fmt = f"{val:.4f}"
            elif 'delta' in key: fmt = f"{val:.4f}"
            else: fmt = f"{val:.4f}"
            
            if key in self.labels:
                self.labels[key].config(text=fmt)
            
            # Handle shared metrics (Gamma/Vega)
            if key == 'gamma':
                self.labels['call_gamma'].config(text=fmt)
                self.labels['put_gamma'].config(text=fmt)
            if key == 'vega':
                self.labels['call_vega'].config(text=fmt)
                self.labels['put_vega'].config(text=fmt)

    def get_analysis_inputs(self):
        """Retrieves inputs for the Graphing Engine."""
        try:
            # Basic Inputs (reuse dashboard inputs for base case)
            base_inputs = self.get_dashboard_inputs()
            if not base_inputs: return None

            # Graph Settings
            params = {
                'y_var': self.combo_y.get(),
                'x_var': self.combo_x.get(),
                'x_start': float(self.entry_x_start.get()),
                'x_end': float(self.entry_x_end.get()),
                'x_steps': int(self.entry_x_steps.get()),
                'z_var': self.combo_z.get(),
                'z_start': float(self.entry_z_start.get()),
                'z_inc': float(self.entry_z_inc.get())
            }
            
            if params['x_steps'] <= 1: raise ValueError("Steps must be > 1")
            
            return base_inputs, params
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid graph settings: {e}")
            return None

    def plot_data(self, x_values, z_values, y_matrix, x_label, y_label, z_label):
        """Renders the chart."""
        self.ax.clear()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, z_val in enumerate(z_values):
            color = colors[i % len(colors)]
            self.ax.plot(x_values, y_matrix[i], label=f"{z_label}={z_val:.2f}", color=color)
            
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(f"{y_label} vs. {x_label}")
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.canvas.draw()
