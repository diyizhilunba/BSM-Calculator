import tkinter as tk
import numpy as np
from bsm_model import BlackScholes
from gui_view import OptionAnalyticsUI

class OptionAnalyticsApp:
    """
    Controller class.
    Mediates between the View (OptionAnalyticsUI) and the Model (BlackScholes).
    """
    def __init__(self):
        self.root = tk.Tk()
        self.view = OptionAnalyticsUI(self.root)
        
        # Bind Buttons
        self.view.btn_calc.config(command=self.run_dashboard_calc)
        self.view.btn_graph.config(command=self.run_analysis)
        
        # Mapping for Dropdowns to Model Variable Names
        self.var_map = {
            "Spot Price": "S",
            "Volatility": "sigma",
            "Time (Days)": "T",
            "Risk-Free Rate": "r"
        }
        
        # Mapping for Output Keys
        self.metric_map = {
            "Call Price": "call_price",
            "Put Price": "put_price",
            "Call Delta": "call_delta",
            "Put Delta": "put_delta",
            "Gamma": "gamma",
            "Vega": "vega",
            "Theta": "call_theta", # Default to call theta for generic label, or handle specific
            "Rho": "call_rho"
        }

    def run(self):
        self.root.mainloop()

    def run_dashboard_calc(self):
        """
        Handles the 'Calculate' button on Tab 1.
        """
        inputs = self.view.get_dashboard_inputs()
        if not inputs: return

        # Instantiate Model
        model = BlackScholes(
            S=inputs['S'],
            K=inputs['K'],
            T_days=inputs['T'],
            r_pct=inputs['r'],
            sigma_pct=inputs['sigma'],
            q_pct=inputs['q']
        )
        
        # Compute
        results = model.calculate_all()
        
        # Update View
        self.view.update_dashboard_results(results)

    def run_analysis(self):
        """
        Handles the 'Generate Graph' button on Tab 2.
        """
        data = self.view.get_analysis_inputs()
        if not data: return
        
        base_inputs, params = data
        
        # Unpack Graph Settings
        x_var_name = self.var_map.get(params['x_var'])
        z_var_name = self.var_map.get(params['z_var'])
        y_metric_key = self.metric_map.get(params['y_var'])
        
        # Validation: X and Z cannot be the same
        if x_var_name == z_var_name:
            tk.messagebox.showwarning("Configuration Error", "X-Axis and Z-Axis variables must be different.")
            return

        # Generate Vectors
        x_values = np.linspace(params['x_start'], params['x_end'], params['x_steps'])
        z_values = [params['z_start'] + i * params['z_inc'] for i in range(5)]
        
        # Result Matrix (5 curves x N steps)
        y_matrix = []

        # Simulation Loop
        for z_val in z_values:
            row_results = []
            for x_val in x_values:
                # Copy base inputs to avoid mutating original
                current_inputs = base_inputs.copy()
                
                # Override with current X and Z
                current_inputs[x_var_name] = x_val
                current_inputs[z_var_name] = z_val
                
                # Calculate
                model = BlackScholes(
                    S=current_inputs['S'],
                    K=current_inputs['K'],
                    T_days=current_inputs['T'],
                    r_pct=current_inputs['r'],
                    sigma_pct=current_inputs['sigma'],
                    q_pct=current_inputs['q']
                )
                res = model.calculate_all()
                
                # Extract specific metric
                # Special handling for Theta/Rho if user wants Put specific? 
                # The prompt asks for generic "Theta", usually Call Theta or they are close/same structure.
                # Let's refine the metric map lookup if needed.
                val = res.get(y_metric_key, 0.0)
                
                # If user selected "Theta" but we mapped to "call_theta", that's fine.
                # If user selected "Put Price", we mapped to "put_price".
                
                row_results.append(val)
            y_matrix.append(row_results)

        # Plot
        self.view.plot_data(
            x_values, 
            z_values, 
            y_matrix, 
            x_label=params['x_var'], 
            y_label=params['y_var'], 
            z_label=params['z_var']
        )

if __name__ == "__main__":
    app = OptionAnalyticsApp()
    app.run()
