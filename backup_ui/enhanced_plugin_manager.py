#!/usr/bin/env python3
"""
Enhanced Plugin Manager UI for Atlas

Provides intuitive interface for managing plugins with descriptions, versions, and controls.
"""

import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict

import customtkinter as ctk


class PluginInfo:
    """Class to hold plugin information."""

    def __init__(self, plugin_id: str, data: Dict[str, Any]):
        self.id = plugin_id
        self.name = data.get("name", plugin_id)
        self.version = data.get("version", "1.0.0")
        self.description = data.get("description", "No description available")
        self.author = data.get("author", "Unknown")
        self.enabled = data.get("enabled", False)
        self.dependencies = data.get("dependencies", [])
        self.path = data.get("path", "")
        self.last_updated = data.get("last_updated", "")
        self.category = data.get("category", "Other")


class EnhancedPluginManagerWindow:
    """Enhanced Plugin Manager with detailed controls and information."""

    def __init__(self, parent, plugin_manager=None):
        self.parent = parent
        self.plugin_manager = plugin_manager

        #Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Plugin Manager")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        self.window.grab_set()

        #Plugin data
        self.plugins_data = {}
        self.selected_plugin = None

        self.setup_ui()
        self.load_plugins_info()
        self.refresh_plugins_list()

    def setup_ui(self):
        """Setup the plugin manager UI."""
        #Configure main grid
        self.window.grid_columnconfigure(0, weight=2)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        #Left panel - Plugins list
        self.setup_plugins_list_panel()

        #Right panel - Plugin details and controls
        self.setup_plugin_details_panel()

    def setup_plugins_list_panel(self):
        """Setup the left panel with plugins list."""
        list_frame = ctk.CTkFrame(self.window)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(2, weight=1)

        #Title
        ctk.CTkLabel(list_frame, text="Available Plugins", font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 5),
        )

        #Search and filter frame
        search_frame = ctk.CTkFrame(list_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=(10, 5), pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.category_var = tk.StringVar(value="All")
        category_combo = ctk.CTkComboBox(
            search_frame,
            variable=self.category_var,
            values=["All", "Tools", "Automation", "System", "Web", "Other"],
            command=self.on_filter,
        )
        category_combo.grid(row=0, column=2, padx=(5, 10), pady=5)

        #Plugins tree frame
        tree_frame = ctk.CTkFrame(list_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        #Create Treeview with tkinter (CustomTkinter doesn't have Treeview)
        columns = ("Name", "Version", "Status", "Category")
        self.plugins_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        #Configure columns
        self.plugins_tree.heading("Name", text="Name")
        self.plugins_tree.heading("Version", text="Version")
        self.plugins_tree.heading("Status", text="Status")
        self.plugins_tree.heading("Category", text="Category")

        self.plugins_tree.column("Name", width=200)
        self.plugins_tree.column("Version", width=80)
        self.plugins_tree.column("Status", width=80)
        self.plugins_tree.column("Category", width=100)

        #Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.plugins_tree.yview)
        self.plugins_tree.configure(yscrollcommand=tree_scroll.set)

        self.plugins_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        #Bind selection event
        self.plugins_tree.bind("<<TreeviewSelect>>", self.on_plugin_select)

        #Bottom buttons
        buttons_frame = ctk.CTkFrame(list_frame)
        buttons_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            command=self.refresh_plugins_list,
            width=100,
        ).pack(side="left", padx=5, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Install from File",
            command=self.install_plugin_from_file,
            width=120,
        ).pack(side="left", padx=5, pady=5)

    def setup_plugin_details_panel(self):
        """Setup the right panel with plugin details."""
        details_frame = ctk.CTkFrame(self.window)
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        details_frame.grid_columnconfigure(0, weight=1)

        #Title
        ctk.CTkLabel(details_frame, text="Plugin Details", font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 5),
        )

        #Plugin info frame
        info_frame = ctk.CTkFrame(details_frame)
        info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        info_frame.grid_columnconfigure(1, weight=1)

        #Plugin information labels
        ctk.CTkLabel(info_frame, text="Name:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=2,
        )
        self.plugin_name_label = ctk.CTkLabel(info_frame, text="-")
        self.plugin_name_label.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        ctk.CTkLabel(info_frame, text="Version:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=2,
        )
        self.plugin_version_label = ctk.CTkLabel(info_frame, text="-")
        self.plugin_version_label.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        ctk.CTkLabel(info_frame, text="Author:", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky="w", padx=10, pady=2,
        )
        self.plugin_author_label = ctk.CTkLabel(info_frame, text="-")
        self.plugin_author_label.grid(row=2, column=1, sticky="w", padx=10, pady=2)

        ctk.CTkLabel(info_frame, text="Category:", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky="w", padx=10, pady=2,
        )
        self.plugin_category_label = ctk.CTkLabel(info_frame, text="-")
        self.plugin_category_label.grid(row=3, column=1, sticky="w", padx=10, pady=2)

        #Description
        desc_frame = ctk.CTkFrame(details_frame)
        desc_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        details_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(desc_frame, text="Description:", font=("Arial", 12, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        self.plugin_description_text = ctk.CTkTextbox(desc_frame, height=150)
        self.plugin_description_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        #Dependencies
        deps_frame = ctk.CTkFrame(details_frame)
        deps_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(deps_frame, text="Dependencies:", font=("Arial", 12, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        self.dependencies_label = ctk.CTkLabel(deps_frame, text="None")
        self.dependencies_label.pack(anchor="w", padx=10, pady=(0, 10))

        #Control buttons
        buttons_frame = ctk.CTkFrame(details_frame)
        buttons_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        self.enable_button = ctk.CTkButton(
            buttons_frame,
            text="Enable",
            command=self.toggle_plugin,
            height=35,
        )
        self.enable_button.pack(fill="x", pady=2)

        self.configure_button = ctk.CTkButton(
            buttons_frame,
            text="Configure",
            command=self.configure_plugin,
            height=35,
        )
        self.configure_button.pack(fill="x", pady=2)

        self.reload_button = ctk.CTkButton(
            buttons_frame,
            text="Reload",
            command=self.reload_plugin,
            height=35,
        )
        self.reload_button.pack(fill="x", pady=2)

        self.remove_button = ctk.CTkButton(
            buttons_frame,
            text="Remove",
            command=self.remove_plugin,
            height=35,
            fg_color="darkred",
            hover_color="red",
        )
        self.remove_button.pack(fill="x", pady=2)

    def load_plugins_info(self):
        """Load plugin information from the plugins directory."""
        plugins_dir = "plugins"
        self.plugins_data = {}

        if os.path.exists(plugins_dir):
            for item in os.listdir(plugins_dir):
                plugin_path = os.path.join(plugins_dir, item)
                if os.path.isdir(plugin_path) and not item.startswith("__"):
                    info_file = os.path.join(plugin_path, "plugin_info.json")

                    if os.path.exists(info_file):
                        try:
                            with open(info_file) as f:
                                info_data = json.load(f)
                                info_data["path"] = plugin_path
                                self.plugins_data[item] = PluginInfo(item, info_data)
                        except Exception as e:
                            #Create basic info for plugins without proper info file
                            self.plugins_data[item] = PluginInfo(item, {
                                "name": item,
                                "version": "Unknown",
                                "description": f"Error loading plugin info: {e}",
                                "author": "Unknown",
                                "enabled": False,
                                "path": plugin_path,
                                "category": "Other",
                            })
                    else:
                        #Create basic info for plugins without info file
                        self.plugins_data[item] = PluginInfo(item, {
                            "name": item,
                            "version": "Unknown",
                            "description": "No plugin information available",
                            "author": "Unknown",
                            "enabled": False,
                            "path": plugin_path,
                            "category": "Other",
                        })

    def refresh_plugins_list(self):
        """Refresh the plugins list display."""
        #Clear existing items
        for item in self.plugins_tree.get_children():
            self.plugins_tree.delete(item)

        #Apply filters
        search_term = self.search_var.get().lower()
        category_filter = self.category_var.get()

        #Add filtered plugins
        for plugin_id, plugin_info in self.plugins_data.items():
            #Apply search filter
            if search_term and search_term not in plugin_info.name.lower() and search_term not in plugin_info.description.lower():
                continue

            #Apply category filter
            if category_filter != "All" and plugin_info.category != category_filter:
                continue

            status = "Enabled" if plugin_info.enabled else "Disabled"

            self.plugins_tree.insert("", "end", values=(
                plugin_info.name,
                plugin_info.version,
                status,
                plugin_info.category,
            ))

    def on_search(self, event):
        """Handle search input changes."""
        self.refresh_plugins_list()

    def on_filter(self, value):
        """Handle category filter changes."""
        self.refresh_plugins_list()

    def on_plugin_select(self, event):
        """Handle plugin selection in the tree."""
        selection = self.plugins_tree.selection()
        if not selection:
            return

        item = self.plugins_tree.item(selection[0])
        plugin_name = item["values"][0]

        #Find plugin info by name
        self.selected_plugin = None
        for plugin_id, plugin_info in self.plugins_data.items():
            if plugin_info.name == plugin_name:
                self.selected_plugin = plugin_info
                break

        if self.selected_plugin:
            self.update_plugin_details()

    def update_plugin_details(self):
        """Update the plugin details panel."""
        if not self.selected_plugin:
            return

        plugin = self.selected_plugin

        #Update labels
        self.plugin_name_label.configure(text=plugin.name)
        self.plugin_version_label.configure(text=plugin.version)
        self.plugin_author_label.configure(text=plugin.author)
        self.plugin_category_label.configure(text=plugin.category)

        #Update description
        self.plugin_description_text.delete(1.0, tk.END)
        self.plugin_description_text.insert(1.0, plugin.description)

        #Update dependencies
        if plugin.dependencies:
            deps_text = ", ".join(plugin.dependencies)
        else:
            deps_text = "None"
        self.dependencies_label.configure(text=deps_text)

        #Update button states
        if plugin.enabled:
            self.enable_button.configure(text="Disable", fg_color="orange", hover_color="darkorange")
        else:
            self.enable_button.configure(text="Enable", fg_color="green", hover_color="darkgreen")

    def toggle_plugin(self):
        """Toggle plugin enabled/disabled state."""
        if not self.selected_plugin:
            return

        try:
            if self.plugin_manager:
                if self.selected_plugin.enabled:
                    success = self.plugin_manager.disable_plugin(self.selected_plugin.id)
                    action = "disabled"
                else:
                    success = self.plugin_manager.enable_plugin(self.selected_plugin.id)
                    action = "enabled"

                if success:
                    self.selected_plugin.enabled = not self.selected_plugin.enabled
                    self.update_plugin_details()
                    self.refresh_plugins_list()
                    messagebox.showinfo("Plugin Manager", f"Plugin {action} successfully!")
                else:
                    messagebox.showerror("Plugin Manager", f"Failed to {action[:-1]} plugin.")
            else:
                messagebox.showinfo("Plugin Manager", "Plugin manager not available for actual toggle.")
        except Exception as e:
            messagebox.showerror("Plugin Manager", f"Error toggling plugin: {e}")

    def configure_plugin(self):
        """Open plugin configuration dialog."""
        if not self.selected_plugin:
            return

        #Check if plugin has configuration
        config_file = os.path.join(self.selected_plugin.path, "config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    config = json.load(f)

                #Create configuration dialog
                self.open_config_dialog(config, config_file)
            except Exception as e:
                messagebox.showerror("Plugin Manager", f"Error loading plugin configuration: {e}")
        else:
            messagebox.showinfo("Plugin Manager", "This plugin does not have configurable options.")

    def open_config_dialog(self, config: Dict, config_file: str):
        """Open a dialog for editing plugin configuration."""
        config_window = ctk.CTkToplevel(self.window)
        config_window.title(f"Configure {self.selected_plugin.name}")
        config_window.geometry("400x500")
        config_window.transient(self.window)
        config_window.grab_set()

        #Create form fields based on config
        fields = {}
        row = 0

        for key, value in config.items():
            ctk.CTkLabel(config_window, text=f"{key}:").grid(row=row, column=0, sticky="w", padx=10, pady=5)

            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                field = ctk.CTkCheckBox(config_window, text="", variable=var)
                fields[key] = var
            elif isinstance(value, (int, float)):
                var = tk.StringVar(value=str(value))
                field = ctk.CTkEntry(config_window, textvariable=var)
                fields[key] = var
            else:
                var = tk.StringVar(value=str(value))
                field = ctk.CTkEntry(config_window, textvariable=var)
                fields[key] = var

            field.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
            row += 1

        config_window.grid_columnconfigure(1, weight=1)

        #Buttons
        button_frame = ctk.CTkFrame(config_window)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        def save_config():
            try:
                new_config = {}
                for key, field in fields.items():
                    value = field.get()
                    #Try to convert to original type
                    if isinstance(config[key], bool):
                        new_config[key] = value
                    elif isinstance(config[key], int):
                        new_config[key] = int(value)
                    elif isinstance(config[key], float):
                        new_config[key] = float(value)
                    else:
                        new_config[key] = value

                with open(config_file, "w") as f:
                    json.dump(new_config, f, indent=2)

                messagebox.showinfo("Configuration", "Configuration saved successfully!")
                config_window.destroy()
            except Exception as e:
                messagebox.showerror("Configuration", f"Error saving configuration: {e}")

        ctk.CTkButton(button_frame, text="Save", command=save_config).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=config_window.destroy).pack(side="left", padx=5)

    def reload_plugin(self):
        """Reload the selected plugin."""
        if not self.selected_plugin:
            return

        try:
            if self.plugin_manager:
                success = self.plugin_manager.reload_plugin(self.selected_plugin.id)
                if success:
                    messagebox.showinfo("Plugin Manager", "Plugin reloaded successfully!")
                else:
                    messagebox.showerror("Plugin Manager", "Failed to reload plugin.")
            else:
                messagebox.showinfo("Plugin Manager", "Plugin manager not available for actual reload.")
        except Exception as e:
            messagebox.showerror("Plugin Manager", f"Error reloading plugin: {e}")

    def remove_plugin(self):
        """Remove the selected plugin."""
        if not self.selected_plugin:
            return

        result = messagebox.askyesno(
            "Remove Plugin",
            f"Are you sure you want to remove '{self.selected_plugin.name}'?\nThis action cannot be undone.",
        )

        if result:
            try:
                import shutil
                shutil.rmtree(self.selected_plugin.path)
                del self.plugins_data[self.selected_plugin.id]
                self.refresh_plugins_list()

                #Clear details panel
                self.selected_plugin = None
                self.plugin_name_label.configure(text="-")
                self.plugin_version_label.configure(text="-")
                self.plugin_author_label.configure(text="-")
                self.plugin_category_label.configure(text="-")
                self.plugin_description_text.delete(1.0, tk.END)
                self.dependencies_label.configure(text="None")

                messagebox.showinfo("Plugin Manager", "Plugin removed successfully!")
            except Exception as e:
                messagebox.showerror("Plugin Manager", f"Error removing plugin: {e}")

    def install_plugin_from_file(self):
        """Install a plugin from a file or directory."""
        path = filedialog.askdirectory(title="Select Plugin Directory")
        if path:
            try:
                plugin_name = os.path.basename(path)
                target_path = os.path.join("plugins", plugin_name)

                if os.path.exists(target_path):
                    messagebox.showerror("Plugin Manager", "A plugin with this name already exists!")
                    return

                import shutil
                shutil.copytree(path, target_path)

                #Reload plugins list
                self.load_plugins_info()
                self.refresh_plugins_list()

                messagebox.showinfo("Plugin Manager", f"Plugin '{plugin_name}' installed successfully!")
            except Exception as e:
                messagebox.showerror("Plugin Manager", f"Error installing plugin: {e}")
