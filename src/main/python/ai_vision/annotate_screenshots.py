"""
Screenshot Element Annotation Tool
Interactive tool to annotate screenshots for training AI vision model
"""

import cv2
import json
import os
import numpy as np
from typing import List, Dict, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

class ElementAnnotator:
    """Interactive annotation tool for training data collection."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Vision Training - Element Annotator")
        self.root.geometry("1400x900")
        
        self.image = None
        self.image_path = None
        self.photo = None
        self.annotations = []
        self.current_box = None
        self.start_x = None
        self.start_y = None
        
        # Element types
        self.element_types = ['input', 'button', 'checkbox', 'link', 'select', 'textarea']
        self.current_type = tk.StringVar(value='input')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Top control panel
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Button(control_frame, text="Load Screenshot", 
                 command=self.load_screenshot, bg='green', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Save Annotations", 
                 command=self.save_annotations, bg='blue', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Clear Last", 
                 command=self.clear_last, bg='orange', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Clear All", 
                 command=self.clear_all, bg='red', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Element Type:").pack(side=tk.LEFT, padx=10)
        
        for elem_type in self.element_types:
            tk.Radiobutton(control_frame, text=elem_type.title(), 
                          variable=self.current_type, value=elem_type).pack(side=tk.LEFT)
        
        # Canvas for image display
        self.canvas = tk.Canvas(self.root, bg='gray', cursor='cross')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Load a screenshot to begin", 
                                     bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Instructions
        instructions = """
        INSTRUCTIONS:
        1. Click 'Load Screenshot' to open an image
        2. Select element type (input, button, etc.)
        3. Click and drag to draw box around element
        4. Enter label/text for the element
        5. Repeat for all elements
        6. Click 'Save Annotations' when done
        
        TIP: Be precise! Draw tight boxes around each element.
        """
        tk.Label(self.root, text=instructions, justify=tk.LEFT, 
                bg='lightyellow', font=('Arial', 9)).pack(side=tk.RIGHT, fill=tk.Y, padx=5)
    
    def load_screenshot(self):
        """Load a screenshot for annotation."""
        file_path = filedialog.askopenfilename(
            title="Select Screenshot",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if not file_path:
            return
        
        self.image_path = file_path
        self.image = cv2.imread(file_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.annotations = []
        
        self.display_image()
        self.status_label.config(text=f"Loaded: {os.path.basename(file_path)} | Annotations: 0")
    
    def display_image(self):
        """Display the image on canvas."""
        if self.image is None:
            return
        
        # Convert to PIL Image
        pil_image = Image.fromarray(self.image)
        
        # Resize to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate scaling
            img_width, img_height = pil_image.size
            scale = min(canvas_width / img_width, canvas_height / img_height) * 0.95
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(pil_image)
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Draw existing annotations
        self.draw_annotations()
    
    def draw_annotations(self):
        """Draw all annotations on canvas."""
        for ann in self.annotations:
            x, y, w, h = ann['bbox']
            elem_type = ann['type']
            label = ann['label']
            
            # Color by type
            colors = {
                'input': 'blue',
                'button': 'green',
                'checkbox': 'orange',
                'link': 'purple',
                'select': 'cyan',
                'textarea': 'magenta'
            }
            color = colors.get(elem_type, 'red')
            
            # Draw rectangle
            self.canvas.create_rectangle(x, y, x+w, y+h, outline=color, width=2)
            
            # Draw label
            self.canvas.create_text(x, y-10, text=f"{elem_type}: {label}", 
                                   anchor=tk.SW, fill=color, font=('Arial', 10, 'bold'))
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        self.start_x = event.x
        self.start_y = event.y
        self.current_box = None
    
    def on_mouse_drag(self, event):
        """Handle mouse drag."""
        if self.start_x is None:
            return
        
        # Delete previous temporary box
        if self.current_box:
            self.canvas.delete(self.current_box)
        
        # Draw new temporary box
        self.current_box = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='yellow', width=2, dash=(5, 5)
        )
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if self.start_x is None:
            return
        
        # Calculate box dimensions
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        
        # Ensure x1 < x2 and y1 < y2
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        
        # Ignore very small boxes (accidental clicks)
        if w < 10 or h < 10:
            if self.current_box:
                self.canvas.delete(self.current_box)
            self.start_x = None
            self.start_y = None
            return
        
        # Ask for label
        label = simpledialog.askstring("Element Label", 
                                       f"Enter label/text for this {self.current_type.get()}:",
                                       parent=self.root)
        
        if label:
            # Add annotation
            annotation = {
                'type': self.current_type.get(),
                'label': label,
                'bbox': [x, y, w, h]
            }
            self.annotations.append(annotation)
            
            # Update display
            if self.current_box:
                self.canvas.delete(self.current_box)
            self.draw_annotations()
            
            self.status_label.config(
                text=f"Loaded: {os.path.basename(self.image_path)} | Annotations: {len(self.annotations)}"
            )
        else:
            # User cancelled
            if self.current_box:
                self.canvas.delete(self.current_box)
        
        self.start_x = None
        self.start_y = None
        self.current_box = None
    
    def clear_last(self):
        """Remove the last annotation."""
        if self.annotations:
            self.annotations.pop()
            self.display_image()
            self.status_label.config(
                text=f"Loaded: {os.path.basename(self.image_path)} | Annotations: {len(self.annotations)}"
            )
    
    def clear_all(self):
        """Clear all annotations."""
        if messagebox.askyesno("Confirm", "Clear all annotations?"):
            self.annotations = []
            self.display_image()
            self.status_label.config(
                text=f"Loaded: {os.path.basename(self.image_path)} | Annotations: 0"
            )
    
    def save_annotations(self):
        """Save annotations to JSON file."""
        if not self.annotations:
            messagebox.showwarning("Warning", "No annotations to save!")
            return
        
        # Default save path
        default_name = os.path.splitext(os.path.basename(self.image_path))[0] + '_annotations.json'
        
        save_path = filedialog.asksaveasfilename(
            title="Save Annotations",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json")]
        )
        
        if not save_path:
            return
        
        # Prepare data
        data = {
            'image_path': self.image_path,
            'image_filename': os.path.basename(self.image_path),
            'image_size': {
                'width': self.image.shape[1],
                'height': self.image.shape[0]
            },
            'annotations': self.annotations
        }
        
        # Save to file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        messagebox.showinfo("Success", f"Saved {len(self.annotations)} annotations to:\n{save_path}")
        self.status_label.config(text=f"Saved annotations to {os.path.basename(save_path)}")
    
    def run(self):
        """Run the annotation tool."""
        self.root.mainloop()


def main():
    """Main entry point."""
    print("=" * 60)
    print("AI VISION TRAINING - ELEMENT ANNOTATOR")
    print("=" * 60)
    print("\nThis tool helps you create training data for your AI vision model.")
    print("Annotate 50-100 screenshots to train an accurate model.\n")
    
    annotator = ElementAnnotator()
    annotator.run()


if __name__ == '__main__':
    main()
