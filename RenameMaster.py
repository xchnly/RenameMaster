import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from datetime import datetime
import json

class BatchRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("RenameMaster By Hendry黄恒利")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Settings
        self.settings_file = "renamer_settings.json"
        self.backup_folder = "rename_backups"
        self.current_folder = ""
        self.last_rename_log = []
        
        # Create UI
        self.create_widgets()
        self.load_settings()
        
        # Apply theme
        self.apply_theme("light")
    
    def create_widgets(self):
        # Notebook for multiple tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Main Tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Basic Rename")
        
        # Advanced Tab
        self.advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="Advanced Options")
        
        # Preview Tab
        self.preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="Preview")
        
        # Settings Tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Build each tab
        self.build_main_tab()
        self.build_advanced_tab()
        self.build_preview_tab()
        self.build_settings_tab()
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(fill="x", side="bottom")
    
    def build_main_tab(self):
        # Folder Selection
        ttk.Label(self.main_tab, text="Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.folder_entry = ttk.Entry(self.main_tab, width=50)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.main_tab, text="Browse...", command=self.select_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # Basic Options Frame
        basic_frame = ttk.LabelFrame(self.main_tab, text="Basic Options", padding=10)
        basic_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # Add/Remove Prefix/Suffix
        ttk.Label(basic_frame, text="Add Prefix:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.add_prefix_entry = ttk.Entry(basic_frame)
        self.add_prefix_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(basic_frame, text="Add Suffix:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.add_suffix_entry = ttk.Entry(basic_frame)
        self.add_suffix_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(basic_frame, text="Remove Prefix:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.remove_prefix_entry = ttk.Entry(basic_frame)
        self.remove_prefix_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(basic_frame, text="Remove Suffix:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.remove_suffix_entry = ttk.Entry(basic_frame)
        self.remove_suffix_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # Numbering Options
        self.numbering_var = tk.BooleanVar()
        ttk.Checkbutton(basic_frame, text="Auto Numbering", variable=self.numbering_var, 
                       command=self.toggle_numbering_options).grid(row=4, column=0, padx=5, pady=2, sticky="w")
        
        self.numbering_frame = ttk.Frame(basic_frame)
        self.numbering_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        
        ttk.Label(self.numbering_frame, text="Start:").grid(row=0, column=0, padx=5, pady=2)
        self.start_num = ttk.Spinbox(self.numbering_frame, from_=1, to=9999, width=5)
        self.start_num.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.numbering_frame, text="Step:").grid(row=0, column=2, padx=5, pady=2)
        self.step_num = ttk.Spinbox(self.numbering_frame, from_=1, to=10, width=5)
        self.step_num.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(self.numbering_frame, text="Digits:").grid(row=0, column=4, padx=5, pady=2)
        self.digits_num = ttk.Spinbox(self.numbering_frame, from_=1, to=5, width=5)
        self.digits_num.grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Label(self.numbering_frame, text="Position:").grid(row=0, column=6, padx=5, pady=2)
        self.number_pos = ttk.Combobox(self.numbering_frame, values=["Prefix", "Middle", "Suffix"], width=8)
        self.number_pos.grid(row=0, column=7, padx=5, pady=2)
        self.number_pos.current(2)
        
        # File Filter
        ttk.Label(basic_frame, text="File Filter (e.g. *.jpg;*.png):").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.file_filter = ttk.Entry(basic_frame)
        self.file_filter.grid(row=6, column=1, padx=5, pady=2, sticky="ew")
        
        # Action Buttons
        button_frame = ttk.Frame(self.main_tab)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Execute Rename", command=self.execute_rename).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Undo Last Rename", command=self.undo_rename).pack(side="left", padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.main_tab, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
    
    def build_advanced_tab(self):
        # Case Conversion
        case_frame = ttk.LabelFrame(self.advanced_tab, text="Case Conversion", padding=10)
        case_frame.pack(fill="x", padx=5, pady=5)
        
        self.case_style = tk.StringVar()
        ttk.Radiobutton(case_frame, text="Lower case", variable=self.case_style, value="lower").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(case_frame, text="UPPER CASE", variable=self.case_style, value="upper").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(case_frame, text="Title Case", variable=self.case_style, value="title").grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(case_frame, text="Sentence case", variable=self.case_style, value="sentence").grid(row=0, column=3, sticky="w")
        ttk.Radiobutton(case_frame, text="No Change", variable=self.case_style, value="none").grid(row=0, column=4, sticky="w")
        self.case_style.set("none")
        
        # Find and Replace
        replace_frame = ttk.LabelFrame(self.advanced_tab, text="Find and Replace", padding=10)
        replace_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(replace_frame, text="Find:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.find_text = ttk.Entry(replace_frame)
        self.find_text.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(replace_frame, text="Replace with:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.replace_text = ttk.Entry(replace_frame)
        self.replace_text.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        self.regex_var = tk.BooleanVar()
        ttk.Checkbutton(replace_frame, text="Use Regular Expression", variable=self.regex_var).grid(row=2, column=0, columnspan=2, sticky="w")
        
        # Date/Time Options
        date_frame = ttk.LabelFrame(self.advanced_tab, text="Date/Time Options", padding=10)
        date_frame.pack(fill="x", padx=5, pady=5)
        
        self.date_format_var = tk.StringVar()
        ttk.Label(date_frame, text="Format:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.date_format = ttk.Combobox(date_frame, textvariable=self.date_format_var, 
                                      values=["%Y-%m-%d", "%d-%m-%Y", "%Y%m%d", "%m%d%Y", "%H%M%S"])
        self.date_format.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.date_format_var.set("%Y-%m-%d")
        
        self.date_position_var = tk.StringVar()
        ttk.Label(date_frame, text="Position:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.date_position = ttk.Combobox(date_frame, textvariable=self.date_position_var, 
                                        values=["Prefix", "Suffix"])
        self.date_position.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.date_position_var.set("Prefix")
    
    def build_preview_tab(self):
        # Preview Treeview
        self.preview_tree = ttk.Treeview(self.preview_tab, columns=("Original", "New"), show="headings")
        self.preview_tree.heading("Original", text="Original Name")
        self.preview_tree.heading("New", text="New Name")
        self.preview_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.preview_tree, orient="vertical", command=self.preview_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        # Preview Button
        ttk.Button(self.preview_tab, text="Refresh Preview", command=self.preview_changes).pack(pady=5)
    
    def build_settings_tab(self):
        # Theme Selection
        theme_frame = ttk.LabelFrame(self.settings_tab, text="Theme", padding=10)
        theme_frame.pack(fill="x", padx=5, pady=5)
        
        self.theme_var = tk.StringVar()
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="light", 
                       command=lambda: self.apply_theme("light")).pack(anchor="w")
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="dark", 
                       command=lambda: self.apply_theme("dark")).pack(anchor="w")
        self.theme_var.set("light")
        
        # Backup Options
        backup_frame = ttk.LabelFrame(self.settings_tab, text="Backup Options", padding=10)
        backup_frame.pack(fill="x", padx=5, pady=5)
        
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="Create backup before renaming", variable=self.backup_var).pack(anchor="w")
        
        # Save/Load Settings
        settings_btn_frame = ttk.Frame(self.settings_tab)
        settings_btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(settings_btn_frame, text="Save Settings", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(settings_btn_frame, text="Load Settings", command=self.load_settings).pack(side="left", padx=5)
        ttk.Button(settings_btn_frame, text="Reset to Defaults", command=self.reset_settings).pack(side="left", padx=5)
    
    def toggle_numbering_options(self):
        if self.numbering_var.get():
            self.numbering_frame.grid()
        else:
            self.numbering_frame.grid_remove()
    
    def apply_theme(self, theme):
        if theme == "dark":
            self.root.tk_setPalette(background='#2d2d2d', foreground='white',
                                  activeBackground='#3d3d3d', activeForeground='white')
            style = ttk.Style()
            style.theme_use('alt')
            style.configure('.', background='#2d2d2d', foreground='white')
        else:
            self.root.tk_setPalette(background='#f0f0f0', foreground='black',
                                  activeBackground='#ececec', activeForeground='black')
            style = ttk.Style()
            style.theme_use('clam')
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.current_folder = folder_selected
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)
            self.status_var.set(f"Selected folder: {folder_selected}")
    
    def preview_changes(self):
        if not self.current_folder:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        
        # Clear previous preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Get all files
        try:
            files = self.get_filtered_files()
            if not files:
                messagebox.showinfo("Info", "No files match the current filter.")
                return
            
            # Generate preview
            changes = []
            for i, filename in enumerate(files):
                new_name = self.generate_new_name(filename, i)
                changes.append((filename, new_name))
                self.preview_tree.insert("", "end", values=(filename, new_name))
            
            self.notebook.select(self.preview_tab)
            self.status_var.set(f"Preview generated for {len(changes)} files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview: {str(e)}")
    
    def get_filtered_files(self):
        if not os.path.exists(self.current_folder):
            raise FileNotFoundError("Selected folder does not exist")
        
        all_files = [f for f in os.listdir(self.current_folder) if os.path.isfile(os.path.join(self.current_folder, f))]
        
        # Apply file filter if specified
        filter_text = self.file_filter.get().strip()
        if filter_text:
            filters = [f.strip().lower() for f in filter_text.split(";") if f.strip()]
            filtered_files = []
            
            for f in all_files:
                for flt in filters:
                    if flt.startswith("*."):
                        ext = flt[1:]
                        if f.lower().endswith(ext):
                            filtered_files.append(f)
                            break
                    else:
                        if flt.lower() in f.lower():
                            filtered_files.append(f)
                            break
            
            return filtered_files
        return all_files
    
    def generate_new_name(self, filename, index):
        name, ext = os.path.splitext(filename)
        new_name = name
        
        # Remove prefix/suffix
        remove_prefix = self.remove_prefix_entry.get().strip()
        if remove_prefix and new_name.startswith(remove_prefix):
            new_name = new_name[len(remove_prefix):]
        
        remove_suffix = self.remove_suffix_entry.get().strip()
        if remove_suffix and new_name.endswith(remove_suffix):
            new_name = new_name[:-len(remove_suffix)]
        
        # Find and replace
        find_text = self.find_text.get().strip()
        replace_text = self.replace_text.get().strip()
        if find_text:
            if self.regex_var.get():
                try:
                    new_name = re.sub(find_text, replace_text, new_name)
                except re.error:
                    pass  # Keep original if regex is invalid
            else:
                new_name = new_name.replace(find_text, replace_text)
        
        # Case conversion
        case_style = self.case_style.get()
        if case_style == "lower":
            new_name = new_name.lower()
        elif case_style == "upper":
            new_name = new_name.upper()
        elif case_style == "title":
            new_name = new_name.title()
        elif case_style == "sentence":
            if new_name:
                new_name = new_name[0].upper() + new_name[1:].lower()
        
        # Add numbering
        if self.numbering_var.get():
            try:
                start = int(self.start_num.get())
                step = int(self.step_num.get())
                digits = int(self.digits_num.get())
                number = start + (index * step)
                number_str = f"{number:0{digits}d}"
                
                position = self.number_pos.get().lower()
                if position == "prefix":
                    new_name = f"{number_str}_{new_name}"
                elif position == "suffix":
                    new_name = f"{new_name}_{number_str}"
                else:  # middle
                    parts = new_name.split("_")
                    if len(parts) > 1:
                        new_name = f"{parts[0]}_{number_str}_{'_'.join(parts[1:])}"
                    else:
                        new_name = f"{number_str}_{new_name}"
            except ValueError:
                pass
        
        # Add date/time
        if self.date_format_var.get():
            try:
                date_str = datetime.now().strftime(self.date_format_var.get())
                if self.date_position_var.get() == "Prefix":
                    new_name = f"{date_str}_{new_name}"
                else:
                    new_name = f"{new_name}_{date_str}"
            except ValueError:
                pass
        
        # Add prefix/suffix
        add_prefix = self.add_prefix_entry.get().strip()
        if add_prefix:
            new_name = add_prefix + new_name
        
        add_suffix = self.add_suffix_entry.get().strip()
        if add_suffix:
            new_name = new_name + add_suffix
        
        return f"{new_name}{ext}"
    
    def execute_rename(self):
        if not self.current_folder:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        
        try:
            files = self.get_filtered_files()
            if not files:
                messagebox.showinfo("Info", "No files match the current filter.")
                return
            
            # Create backup if enabled
            if self.backup_var.get():
                self.create_backup(files)
            
            # Execute rename
            self.progress["maximum"] = len(files)
            self.progress["value"] = 0
            
            rename_log = []
            success_count = 0
            
            for i, filename in enumerate(files):
                old_path = os.path.join(self.current_folder, filename)
                new_name = self.generate_new_name(filename, i)
                new_path = os.path.join(self.current_folder, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    rename_log.append((filename, new_name))
                    success_count += 1
                except Exception as e:
                    rename_log.append((filename, f"Error: {str(e)}"))
                
                self.progress["value"] = i + 1
                self.root.update_idletasks()
            
            self.last_rename_log = rename_log
            messagebox.showinfo("Complete", f"Renaming complete!\nSuccess: {success_count}/{len(files)}")
            self.status_var.set(f"Renamed {success_count} of {len(files)} files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during renaming: {str(e)}")
        finally:
            self.progress["value"] = 0
    
    def create_backup(self, files):
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_folder, f"backup_{timestamp}")
        os.makedirs(backup_path)
        
        for filename in files:
            src = os.path.join(self.current_folder, filename)
            dst = os.path.join(backup_path, filename)
            try:
                if os.path.exists(src):
                    import shutil
                    shutil.copy2(src, dst)
            except Exception as e:
                print(f"Failed to backup {filename}: {str(e)}")
    
    def undo_rename(self):
        if not self.last_rename_log:
            messagebox.showinfo("Info", "No rename operation to undo")
            return
        
        if not messagebox.askyesno("Confirm", "Undo the last rename operation?"):
            return
        
        try:
            undo_count = 0
            for original, new in self.last_rename_log:
                if not isinstance(new, str) or new.startswith("Error:"):
                    continue
                
                old_path = os.path.join(self.current_folder, new)
                original_path = os.path.join(self.current_folder, original)
                
                if os.path.exists(old_path):
                    os.rename(old_path, original_path)
                    undo_count += 1
            
            messagebox.showinfo("Complete", f"Undo complete! Restored {undo_count} files")
            self.last_rename_log = []
            self.preview_changes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during undo: {str(e)}")
    
    def save_settings(self):
        settings = {
            "folder": self.current_folder,
            "add_prefix": self.add_prefix_entry.get(),
            "add_suffix": self.add_suffix_entry.get(),
            "remove_prefix": self.remove_prefix_entry.get(),
            "remove_suffix": self.remove_suffix_entry.get(),
            "numbering": self.numbering_var.get(),
            "start_num": self.start_num.get(),
            "step_num": self.step_num.get(),
            "digits_num": self.digits_num.get(),
            "number_pos": self.number_pos.get(),
            "file_filter": self.file_filter.get(),
            "case_style": self.case_style.get(),
            "find_text": self.find_text.get(),
            "replace_text": self.replace_text.get(),
            "regex": self.regex_var.get(),
            "date_format": self.date_format_var.get(),
            "date_position": self.date_position_var.get(),
            "theme": self.theme_var.get(),
            "backup": self.backup_var.get()
        }
        
        try:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                
                self.current_folder = settings.get("folder", "")
                self.folder_entry.delete(0, tk.END)
                self.folder_entry.insert(0, self.current_folder)
                
                self.add_prefix_entry.delete(0, tk.END)
                self.add_prefix_entry.insert(0, settings.get("add_prefix", ""))
                
                self.add_suffix_entry.delete(0, tk.END)
                self.add_suffix_entry.insert(0, settings.get("add_suffix", ""))
                
                self.remove_prefix_entry.delete(0, tk.END)
                self.remove_prefix_entry.insert(0, settings.get("remove_prefix", ""))
                
                self.remove_suffix_entry.delete(0, tk.END)
                self.remove_suffix_entry.insert(0, settings.get("remove_suffix", ""))
                
                self.numbering_var.set(settings.get("numbering", False))
                self.toggle_numbering_options()
                
                self.start_num.delete(0, tk.END)
                self.start_num.insert(0, settings.get("start_num", "1"))
                
                self.step_num.delete(0, tk.END)
                self.step_num.insert(0, settings.get("step_num", "1"))
                
                self.digits_num.delete(0, tk.END)
                self.digits_num.insert(0, settings.get("digits_num", "3"))
                
                self.number_pos.set(settings.get("number_pos", "Suffix"))
                
                self.file_filter.delete(0, tk.END)
                self.file_filter.insert(0, settings.get("file_filter", ""))
                
                self.case_style.set(settings.get("case_style", "none"))
                
                self.find_text.delete(0, tk.END)
                self.find_text.insert(0, settings.get("find_text", ""))
                
                self.replace_text.delete(0, tk.END)
                self.replace_text.insert(0, settings.get("replace_text", ""))
                
                self.regex_var.set(settings.get("regex", False))
                
                self.date_format_var.set(settings.get("date_format", "%Y-%m-%d"))
                self.date_position_var.set(settings.get("date_position", "Prefix"))
                
                theme = settings.get("theme", "light")
                self.theme_var.set(theme)
                self.apply_theme(theme)
                
                self.backup_var.set(settings.get("backup", True))
                
                messagebox.showinfo("Success", "Settings loaded successfully!")
            else:
                messagebox.showinfo("Info", "No saved settings found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")
    
    def reset_settings(self):
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.current_folder = ""
            self.folder_entry.delete(0, tk.END)
            
            self.add_prefix_entry.delete(0, tk.END)
            self.add_suffix_entry.delete(0, tk.END)
            self.remove_prefix_entry.delete(0, tk.END)
            self.remove_suffix_entry.delete(0, tk.END)
            
            self.numbering_var.set(False)
            self.toggle_numbering_options()
            self.start_num.delete(0, tk.END)
            self.start_num.insert(0, "1")
            self.step_num.delete(0, tk.END)
            self.step_num.insert(0, "1")
            self.digits_num.delete(0, tk.END)
            self.digits_num.insert(0, "3")
            self.number_pos.set("Suffix")
            
            self.file_filter.delete(0, tk.END)
            
            self.case_style.set("none")
            self.find_text.delete(0, tk.END)
            self.replace_text.delete(0, tk.END)
            self.regex_var.set(False)
            
            self.date_format_var.set("%Y-%m-%d")
            self.date_position_var.set("Prefix")
            
            self.theme_var.set("light")
            self.apply_theme("light")
            
            self.backup_var.set(True)
            
            messagebox.showinfo("Info", "Settings reset to defaults")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenamer(root)
    root.mainloop()