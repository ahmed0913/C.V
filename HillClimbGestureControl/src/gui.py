"""
Settings GUI using Tkinter.

Provides a simple interface for configuring gesture recognition and camera settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.config_manager import ConfigManager
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class SettingsGUI:
    """
    Tkinter-based settings GUI.
    
    Allows users to configure:
    - Camera settings
    - Detection thresholds
    - Gesture recognition sensitivity
    - Keyboard delays
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize settings GUI.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.window = None
        self.notebook = None
        self.is_open = False
    
    def open(self) -> None:
        """Create and display the settings window."""
        if self.is_open:
            self.window.lift()
            return
        
        self.window = tk.Tk()
        self.window.title("Hill Climb Gesture Control - Settings")
        self.window.geometry("600x500")
        self.is_open = True
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_camera_tab()
        self._create_detection_tab()
        self._create_control_tab()
        self._create_ui_tab()
        
        # Buttons frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Save", command=self._save_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset", command=self._reset_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=2)
        
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.mainloop()
    
    def _create_camera_tab(self) -> None:
        """Create camera settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Camera")
        
        # Resolution
        ttk.Label(frame, text="Resolution", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=10)
        
        res_frame = ttk.Frame(frame)
        res_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(res_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value=str(self.config.get('camera.width')))
        ttk.Spinbox(res_frame, from_=320, to=1920, textvariable=self.width_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(res_frame, text="Height:").pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value=str(self.config.get('camera.height')))
        ttk.Spinbox(res_frame, from_=240, to=1080, textvariable=self.height_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # FPS
        ttk.Label(frame, text="FPS Target", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(20, 10))
        
        fps_frame = ttk.Frame(frame)
        fps_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.fps_var = tk.StringVar(value=str(self.config.get('camera.fps')))
        fps_scale = ttk.Scale(fps_frame, from_=5, to=60, orient=tk.HORIZONTAL, 
                             variable=self.fps_var, command=lambda x: self.fps_label.config(text=f"{float(x):.0f} FPS"))
        fps_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.fps_label = ttk.Label(fps_frame, text=f"{float(self.fps_var.get()):.0f} FPS", width=10)
        self.fps_label.pack(side=tk.LEFT, padx=10)
    
    def _create_detection_tab(self) -> None:
        """Create hand detection settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Detection")
        
        # Max hands
        ttk.Label(frame, text="Max Hands", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=10)
        
        hands_frame = ttk.Frame(frame)
        hands_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(hands_frame, text="Maximum:").pack(side=tk.LEFT)
        self.max_hands_var = tk.StringVar(value=str(self.config.get('detection.max_hands')))
        ttk.Spinbox(hands_frame, from_=1, to=2, textvariable=self.max_hands_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Detection confidence
        ttk.Label(frame, text="Detection Confidence", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(20, 10))
        
        det_frame = ttk.Frame(frame)
        det_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.det_conf_var = tk.DoubleVar(value=self.config.get('detection.min_detection_confidence'))
        det_scale = ttk.Scale(det_frame, from_=0.3, to=1.0, orient=tk.HORIZONTAL,
                             variable=self.det_conf_var, 
                             command=lambda x: self.det_conf_label.config(text=f"{float(x):.2f}"))
        det_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.det_conf_label = ttk.Label(det_frame, text=f"{self.det_conf_var.get():.2f}", width=6)
        self.det_conf_label.pack(side=tk.LEFT, padx=10)
        
        # Tracking confidence
        ttk.Label(frame, text="Tracking Confidence", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(20, 10))
        
        track_frame = ttk.Frame(frame)
        track_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.track_conf_var = tk.DoubleVar(value=self.config.get('detection.min_tracking_confidence'))
        track_scale = ttk.Scale(track_frame, from_=0.3, to=1.0, orient=tk.HORIZONTAL,
                               variable=self.track_conf_var,
                               command=lambda x: self.track_conf_label.config(text=f"{float(x):.2f}"))
        track_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.track_conf_label = ttk.Label(track_frame, text=f"{self.track_conf_var.get():.2f}", width=6)
        self.track_conf_label.pack(side=tk.LEFT, padx=10)
    
    def _create_control_tab(self) -> None:
        """Create control settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Control")
        
        # Key delay
        ttk.Label(frame, text="Key Press Delay", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=10)
        
        delay_frame = ttk.Frame(frame)
        delay_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(delay_frame, text="Delay (seconds):").pack(side=tk.LEFT)
        self.key_delay_var = tk.DoubleVar(value=self.config.get('control.key_delay'))
        ttk.Spinbox(delay_frame, from_=0.01, to=0.5, increment=0.01, 
                   textvariable=self.key_delay_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Frame flip
        self.flip_var = tk.BooleanVar(value=self.config.get('control.flip_frame'))
        ttk.Checkbutton(frame, text="Flip Frame (Mirror Mode)", variable=self.flip_var).pack(anchor="w", padx=20, pady=10)
    
    def _create_ui_tab(self) -> None:
        """Create UI settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="UI")
        
        # Debug info
        self.debug_var = tk.BooleanVar(value=self.config.get('ui.show_debug_info'))
        ttk.Checkbutton(frame, text="Show Debug Info", variable=self.debug_var).pack(anchor="w", padx=20, pady=5)
        
        # Landmarks
        self.landmarks_var = tk.BooleanVar(value=self.config.get('ui.show_landmarks'))
        ttk.Checkbutton(frame, text="Show Hand Landmarks", variable=self.landmarks_var).pack(anchor="w", padx=20, pady=5)
        
        # FPS display
        self.fps_display_var = tk.BooleanVar(value=self.config.get('ui.show_fps'))
        ttk.Checkbutton(frame, text="Show FPS Counter", variable=self.fps_display_var).pack(anchor="w", padx=20, pady=5)
        
        # Font size
        ttk.Label(frame, text="Font Size", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        font_frame = ttk.Frame(frame)
        font_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.font_size_var = tk.DoubleVar(value=self.config.get('ui.font_size'))
        font_scale = ttk.Scale(font_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
                              variable=self.font_size_var,
                              command=lambda x: self.font_label.config(text=f"{float(x):.1f}x"))
        font_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.font_label = ttk.Label(font_frame, text=f"{self.font_size_var.get():.1f}x", width=6)
        self.font_label.pack(side=tk.LEFT, padx=10)
    
    def _save_config(self) -> None:
        """Save current settings."""
        try:
            # Camera
            self.config.set('camera.width', int(self.width_var.get()))
            self.config.set('camera.height', int(self.height_var.get()))
            self.config.set('camera.fps', int(float(self.fps_var.get())))
            
            # Detection
            self.config.set('detection.max_hands', int(self.max_hands_var.get()))
            self.config.set('detection.min_detection_confidence', self.det_conf_var.get())
            self.config.set('detection.min_tracking_confidence', self.track_conf_var.get())
            
            # Control
            self.config.set('control.key_delay', self.key_delay_var.get())
            self.config.set('control.flip_frame', self.flip_var.get())
            
            # UI
            self.config.set('ui.show_debug_info', self.debug_var.get())
            self.config.set('ui.show_landmarks', self.landmarks_var.get())
            self.config.set('ui.show_fps', self.fps_display_var.get())
            self.config.set('ui.font_size', self.font_size_var.get())
            
            # Save to file
            self.config.save_config()
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            logger.error(f"Save config error: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _reset_config(self) -> None:
        """Reset to default settings."""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.config.reset_to_defaults()
            self.config.save_config()
            messagebox.showinfo("Success", "Settings reset to defaults!")
            
            # Refresh GUI
            self.window.destroy()
            self.is_open = False
            self.open()
    
    def _on_close(self) -> None:
        """Handle window close."""
        self.is_open = False
        self.window.destroy()
