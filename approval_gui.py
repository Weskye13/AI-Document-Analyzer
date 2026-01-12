"""
AI Document Analyzer - Approval GUI
====================================

Comprehensive Tkinter GUI for reviewing and approving all changes:
- Primary contact field updates
- Family member search/link/create/update
- Address, employment, education history
- Other extracted information

DESIGN PRINCIPLES:
- Everything requires approval - no automatic updates
- All data is editable before applying
- Family members can be searched, linked, or created
- History is saved as formatted case notes

Author: Law Office of Joshua E. Bardavid
Version: 2.0.0
Date: January 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json

from config import (
    UI_CONFIG, CHANGE_COLORS, FAMILY_RELATIONSHIPS, HISTORY_TYPES,
    CONTACT_FIELDS, BIOGRAPHIC_FIELDS
)
from infotems_comparator import (
    ChangeSet, FieldChange, ChangeType,
    FamilyMember, FamilyMemberAction,
    HistoryRecord, HistorySet, HistoryAction
)


class ApprovalGUI:
    """
    Comprehensive GUI for reviewing all extracted data before applying.
    
    Features:
    - Tabbed interface for different data types
    - Editable fields throughout
    - Family member search and linking
    - History record management
    - Full approval workflow
    """
    
    def __init__(
        self, 
        change_set: ChangeSet, 
        comparator = None,
        on_apply: Callable[[ChangeSet], None] = None
    ):
        """
        Initialize the approval GUI.
        
        Args:
            change_set: ChangeSet with all extracted data
            comparator: InfotemsComparator for searching contacts
            on_apply: Callback when user applies changes
        """
        self.change_set = change_set
        self.comparator = comparator
        self.on_apply = on_apply
        self.result = None
        
        # Create root window
        self.root = tk.Tk()
        self.root.title(f"{UI_CONFIG['window_title']} - Review & Approve")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Style configuration
        self._configure_styles()
        
        # Data tracking
        self.field_entries: Dict[str, tk.Entry] = {}
        self.field_vars: Dict[str, tk.StringVar] = {}
        self.approval_vars: Dict[str, tk.BooleanVar] = {}
        
        # Build UI
        self._create_widgets()
        self._populate_all_tabs()
    
    def _configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        
        # Tab styling
        style.configure('TNotebook.Tab', padding=[12, 8], font=('Arial', 10))
        
        # Button styles
        style.configure('Apply.TButton', font=('Arial', 11, 'bold'))
        style.configure('Search.TButton', font=('Arial', 9))
        
        # Treeview styling
        style.configure('Treeview', rowheight=28, font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header(main)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Create tabs
        self.tab_primary = ttk.Frame(self.notebook, padding=10)
        self.tab_family = ttk.Frame(self.notebook, padding=10)
        self.tab_address = ttk.Frame(self.notebook, padding=10)
        self.tab_employment = ttk.Frame(self.notebook, padding=10)
        self.tab_education = ttk.Frame(self.notebook, padding=10)
        self.tab_other = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_primary, text="📋 Primary Contact")
        self.notebook.add(self.tab_family, text=f"👥 Family ({len(self.change_set.family_members)})")
        self.notebook.add(self.tab_address, text="🏠 Address History")
        self.notebook.add(self.tab_employment, text="💼 Employment")
        self.notebook.add(self.tab_education, text="🎓 Education")
        self.notebook.add(self.tab_other, text="📝 Other Info")
        
        # Bottom action bar
        self._create_action_bar(main)
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - document info
        left = ttk.Frame(header)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            left,
            text="📄 DOCUMENT DATA REVIEW",
            font=('Arial', 14, 'bold')
        ).pack(anchor=tk.W)
        
        info_text = (
            f"Client: {self.change_set.contact_name or 'Unknown'} | "
            f"A#: {self.change_set.a_number or 'N/A'} | "
            f"Document: {self.change_set.document_type} | "
            f"Confidence: {self.change_set.extraction_confidence:.0%}"
        )
        ttk.Label(left, text=info_text, foreground='gray').pack(anchor=tk.W)
        
        # Right side - contact status
        right = ttk.Frame(header)
        right.pack(side=tk.RIGHT)
        
        if self.change_set.contact_id:
            status_text = f"✓ Existing Contact (ID: {self.change_set.contact_id})"
            status_color = CHANGE_COLORS['modified']
        else:
            status_text = "➕ Will Create New Contact"
            status_color = CHANGE_COLORS['new']
        
        ttk.Label(right, text=status_text, foreground=status_color, 
                  font=('Arial', 11, 'bold')).pack()
    
    def _create_action_bar(self, parent):
        """Create bottom action bar."""
        bar = ttk.Frame(parent)
        bar.pack(fill=tk.X, pady=(10, 0))
        
        # Left - summary
        left = ttk.Frame(bar)
        left.pack(side=tk.LEFT)
        
        self.summary_label = ttk.Label(
            left, 
            text=self._get_summary_text(),
            font=('Arial', 10)
        )
        self.summary_label.pack(anchor=tk.W)
        
        # Right - buttons
        right = ttk.Frame(bar)
        right.pack(side=tk.RIGHT)
        
        ttk.Button(
            right, 
            text="❌ Cancel",
            command=self._cancel
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            right,
            text="💾 Save Draft",
            command=self._save_draft
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            right,
            text="✅ Apply All Approved Changes",
            command=self._apply_changes,
            style='Apply.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_status_bar(self):
        """Create status bar."""
        status = ttk.Frame(self.root)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Separator(status, orient='horizontal').pack(fill=tk.X)
        
        inner = ttk.Frame(status, padding=(10, 5))
        inner.pack(fill=tk.X)
        
        self.status_label = ttk.Label(inner, text="Ready", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Label(
            inner, 
            text=f"Source: {Path(self.change_set.source_file).name}",
            font=('Arial', 9),
            foreground='gray'
        ).pack(side=tk.RIGHT)
    
    def _get_summary_text(self) -> str:
        """Get summary of pending changes."""
        parts = []
        
        primary = sum(1 for c in self.change_set.changes if c.has_change and c.approved)
        if primary:
            parts.append(f"{primary} field changes")
        
        family = sum(1 for fm in self.change_set.family_members 
                     if fm.action != FamilyMemberAction.SKIP)
        if family:
            parts.append(f"{family} family members")
        
        history = 0
        for hs in self.change_set.history.values():
            if hs.action == HistoryAction.SAVE_TO_NOTES:
                history += len(hs.records)
        if history:
            parts.append(f"{history} history records")
        
        if parts:
            return f"📊 Pending: {', '.join(parts)}"
        return "📊 No changes selected"
    
    # ========================================================================
    # TAB 1: PRIMARY CONTACT
    # ========================================================================
    
    def _populate_all_tabs(self):
        """Populate all tabs with data."""
        self._populate_primary_tab()
        self._populate_family_tab()
        self._populate_history_tab(self.tab_address, 'address')
        self._populate_history_tab(self.tab_employment, 'employment')
        self._populate_history_tab(self.tab_education, 'education')
        self._populate_other_tab()
    
    def _populate_primary_tab(self):
        """Populate primary contact tab."""
        tab = self.tab_primary
        
        # Instructions
        ttk.Label(
            tab,
            text="Review and edit field changes. Check boxes to approve changes.",
            foreground='gray'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Scrollable frame
        canvas = tk.Canvas(tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create field rows
        # Header row
        header = ttk.Frame(scroll_frame)
        header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header, text="Approve", width=8, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Field", width=25, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Current Value", width=30, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="", width=5).pack(side=tk.LEFT)
        ttk.Label(header, text="New Value (editable)", width=30, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Conf", width=6, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(scroll_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Group by Contact vs Biographic
        contact_changes = [c for c in self.change_set.changes if not c.is_biographic]
        bio_changes = [c for c in self.change_set.changes if c.is_biographic]
        
        if contact_changes:
            ttk.Label(
                scroll_frame, 
                text="Contact Fields",
                font=('Arial', 10, 'bold'),
                foreground='#1976D2'
            ).pack(anchor=tk.W, pady=(10, 5))
            
            for change in contact_changes:
                self._create_field_row(scroll_frame, change)
        
        if bio_changes:
            ttk.Label(
                scroll_frame,
                text="Biographic Fields", 
                font=('Arial', 10, 'bold'),
                foreground='#1976D2'
            ).pack(anchor=tk.W, pady=(15, 5))
            
            for change in bio_changes:
                self._create_field_row(scroll_frame, change)
        
        # Bulk actions
        bulk_frame = ttk.Frame(scroll_frame)
        bulk_frame.pack(fill=tk.X, pady=(20, 10))
        
        ttk.Button(bulk_frame, text="✓ Approve All", 
                   command=self._approve_all_primary).pack(side=tk.LEFT, padx=5)
        ttk.Button(bulk_frame, text="✗ Reject All",
                   command=self._reject_all_primary).pack(side=tk.LEFT, padx=5)
    
    def _create_field_row(self, parent, change: FieldChange):
        """Create a single field row."""
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=3)
        
        # Checkbox
        var = tk.BooleanVar(value=change.approved and change.has_change)
        self.approval_vars[change.field_key] = var
        
        cb = ttk.Checkbutton(row, variable=var, command=lambda: self._on_approval_change(change))
        cb.pack(side=tk.LEFT, padx=5)
        
        # Field name
        label_fg = None
        if change.change_type == ChangeType.NEW:
            label_fg = CHANGE_COLORS['new']
        elif change.change_type == ChangeType.MODIFIED:
            label_fg = CHANGE_COLORS['modified']
        
        ttk.Label(
            row, 
            text=change.field_label,
            width=25,
            foreground=label_fg
        ).pack(side=tk.LEFT, padx=5)
        
        # Current value
        current_text = change.current_value or "(empty)"
        ttk.Label(row, text=current_text, width=30, foreground='gray').pack(side=tk.LEFT, padx=5)
        
        # Arrow
        arrow = "→" if change.has_change else "="
        ttk.Label(row, text=arrow, width=5).pack(side=tk.LEFT)
        
        # New value (editable)
        new_var = tk.StringVar(value=change.new_value or "")
        self.field_vars[change.field_key] = new_var
        
        entry = ttk.Entry(row, textvariable=new_var, width=35)
        entry.pack(side=tk.LEFT, padx=5)
        self.field_entries[change.field_key] = entry
        
        # Bind change
        new_var.trace_add('write', lambda *args, c=change: self._on_value_edit(c))
        
        # Confidence
        conf_text = f"{change.confidence:.0%}" if change.confidence else "-"
        ttk.Label(row, text=conf_text, width=6).pack(side=tk.LEFT, padx=5)
        
        # Disable checkbox if no change
        if not change.has_change:
            cb.configure(state='disabled')
    
    def _on_approval_change(self, change: FieldChange):
        """Handle approval checkbox change."""
        var = self.approval_vars.get(change.field_key)
        if var:
            change.approved = var.get()
        self._update_summary()
    
    def _on_value_edit(self, change: FieldChange):
        """Handle value edit."""
        var = self.field_vars.get(change.field_key)
        if var:
            change.edited_value = var.get()
            
            # If value was edited, auto-approve
            if change.edited_value != change.new_value:
                change.approved = True
                if change.field_key in self.approval_vars:
                    self.approval_vars[change.field_key].set(True)
        
        self._update_summary()
    
    def _approve_all_primary(self):
        """Approve all primary contact changes."""
        for change in self.change_set.changes:
            if change.has_change:
                change.approved = True
                if change.field_key in self.approval_vars:
                    self.approval_vars[change.field_key].set(True)
        self._update_summary()
    
    def _reject_all_primary(self):
        """Reject all primary contact changes."""
        for change in self.change_set.changes:
            change.approved = False
            if change.field_key in self.approval_vars:
                self.approval_vars[change.field_key].set(False)
        self._update_summary()
    
    # ========================================================================
    # TAB 2: FAMILY MEMBERS
    # ========================================================================
    
    def _populate_family_tab(self):
        """Populate family members tab."""
        tab = self.tab_family
        
        if not self.change_set.family_members:
            ttk.Label(
                tab,
                text="No family members extracted from this document.",
                foreground='gray',
                font=('Arial', 11)
            ).pack(pady=50)
            return
        
        # Instructions
        ttk.Label(
            tab,
            text="For each family member: Search InfoTems, link to existing contact, or create new.",
            foreground='gray'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Create scrollable list of family members
        canvas = tk.Canvas(tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create panel for each family member
        for i, fm in enumerate(self.change_set.family_members):
            self._create_family_member_panel(scroll_frame, fm, i)
    
    def _create_family_member_panel(self, parent, fm: FamilyMember, index: int):
        """Create panel for a single family member."""
        # Frame with border
        panel = ttk.LabelFrame(
            parent,
            text=f"{FAMILY_RELATIONSHIPS.get(fm.relationship, {}).get('display_name', fm.relationship)}: {fm.display_name}",
            padding=10
        )
        panel.pack(fill=tk.X, pady=10, padx=5)
        
        # Top row: extracted data and match info
        top = ttk.Frame(panel)
        top.pack(fill=tk.X)
        
        # Left: extracted data
        left = ttk.LabelFrame(top, text="Extracted Data", padding=5)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        data = fm.extracted_data
        fields = [
            ('Name', f"{data.get('first_name', '')} {data.get('middle_name', '')} {data.get('last_name', '')}".strip()),
            ('DOB', data.get('date_of_birth', '')),
            ('A-Number', data.get('a_number', '')),
            ('Birth Place', f"{data.get('city_of_birth', '')}, {data.get('country_of_birth', '')}".strip(', ')),
            ('Immigration Status', data.get('immigration_status', '')),
        ]
        
        for label, value in fields:
            if value:
                row = ttk.Frame(left)
                row.pack(fill=tk.X, pady=1)
                ttk.Label(row, text=f"{label}:", width=15, font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
                ttk.Label(row, text=value, font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Right: match info
        right = ttk.LabelFrame(top, text="InfoTems Match", padding=5)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if fm.matched_contact_id:
            match_color = CHANGE_COLORS['linked']
            ttk.Label(
                right,
                text=f"✓ Found: {fm.matched_contact_name}",
                foreground=match_color,
                font=('Arial', 10, 'bold')
            ).pack(anchor=tk.W)
            ttk.Label(
                right,
                text=f"ID: {fm.matched_contact_id} | Match: {fm.match_method} ({fm.match_confidence:.0%})",
                foreground='gray'
            ).pack(anchor=tk.W)
        else:
            ttk.Label(
                right,
                text="⚠ No match found",
                foreground=CHANGE_COLORS['modified'],
                font=('Arial', 10)
            ).pack(anchor=tk.W)
        
        # Search button
        search_frame = ttk.Frame(right)
        search_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            search_frame,
            text="🔍 Search InfoTems",
            command=lambda f=fm: self._search_family_member(f),
            style='Search.TButton'
        ).pack(side=tk.LEFT)
        
        # Bottom: action selection
        action_frame = ttk.LabelFrame(panel, text="Action", padding=5)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        action_var = tk.StringVar(value=fm.action.value)
        
        actions = [
            (FamilyMemberAction.SKIP, "⏭ Skip - Do nothing"),
            (FamilyMemberAction.LINK_EXISTING, "🔗 Link to existing contact"),
            (FamilyMemberAction.CREATE_NEW, "➕ Create new contact"),
            (FamilyMemberAction.UPDATE_LINKED, "📝 Update linked contact"),
        ]
        
        for action, label in actions:
            rb = ttk.Radiobutton(
                action_frame,
                text=label,
                variable=action_var,
                value=action.value,
                command=lambda f=fm, v=action_var: self._on_family_action_change(f, v)
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Store reference
        fm._action_var = action_var
    
    def _search_family_member(self, fm: FamilyMember):
        """Search InfoTems for family member."""
        if not self.comparator:
            messagebox.showwarning("Warning", "InfoTems comparator not available")
            return
        
        # Get search params
        data = fm.extracted_data
        
        # Show search dialog
        results = self.comparator.search_contacts(
            a_number=data.get('a_number'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            dob=data.get('date_of_birth'),
            limit=10
        )
        
        if not results:
            messagebox.showinfo("Search Results", "No matching contacts found in InfoTems.")
            return
        
        # Show selection dialog
        dialog = FamilySearchDialog(self.root, fm, results)
        self.root.wait_window(dialog.top)
        
        if dialog.selected_contact:
            fm.matched_contact_id = dialog.selected_contact.get('Id')
            fm.matched_contact_name = dialog.selected_contact.get('DisplayAs')
            fm.match_method = 'manual_search'
            fm.match_confidence = 1.0
            fm.action = FamilyMemberAction.LINK_EXISTING
            
            # Refresh the tab
            for widget in self.tab_family.winfo_children():
                widget.destroy()
            self._populate_family_tab()
        
        self._update_summary()
    
    def _on_family_action_change(self, fm: FamilyMember, var: tk.StringVar):
        """Handle family member action change."""
        fm.action = FamilyMemberAction(var.get())
        self._update_summary()
    
    # ========================================================================
    # TABS 3-5: HISTORY
    # ========================================================================
    
    def _populate_history_tab(self, tab, history_type: str):
        """Populate a history tab (address, employment, education)."""
        history_set = self.change_set.history.get(history_type)
        
        if not history_set or not history_set.records:
            config = HISTORY_TYPES.get(history_type, {})
            ttk.Label(
                tab,
                text=f"No {config.get('display_name', history_type).lower()} extracted from this document.",
                foreground='gray',
                font=('Arial', 11)
            ).pack(pady=50)
            return
        
        config = HISTORY_TYPES[history_type]
        
        # Instructions
        ttk.Label(
            tab,
            text=f"Review {config['display_name']}. Edit as needed. Will be saved as a case note.",
            foreground='gray'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Action
        action_frame = ttk.Frame(tab)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        action_var = tk.StringVar(value=history_set.action.value)
        history_set._action_var = action_var
        
        ttk.Radiobutton(
            action_frame,
            text="💾 Save to Case Notes",
            variable=action_var,
            value=HistoryAction.SAVE_TO_NOTES.value,
            command=lambda: self._on_history_action_change(history_set, action_var)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            action_frame,
            text="⏭ Skip",
            variable=action_var,
            value=HistoryAction.SKIP.value,
            command=lambda: self._on_history_action_change(history_set, action_var)
        ).pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = [f['key'] for f in config['fields']]
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        for field_def in config['fields']:
            tree.heading(field_def['key'], text=field_def['label'])
            tree.column(field_def['key'], width=120, minwidth=80)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Populate data
        for i, record in enumerate(history_set.records):
            values = []
            for field_def in config['fields']:
                val = record.data.get(field_def['key'], '')
                values.append(val)
            
            tag = 'current' if record.is_current else ''
            tree.insert('', 'end', values=values, tags=(tag,), iid=str(i))
        
        tree.tag_configure('current', background='#E8F5E9')
        
        # Store reference
        history_set._tree = tree
        
        # Edit buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="✏️ Edit Selected",
            command=lambda: self._edit_history_record(history_set, tree)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="➕ Add Record",
            command=lambda: self._add_history_record(history_set, tree, config)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Delete Selected",
            command=lambda: self._delete_history_record(history_set, tree)
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_history_action_change(self, history_set: HistorySet, var: tk.StringVar):
        """Handle history action change."""
        history_set.action = HistoryAction(var.get())
        self._update_summary()
    
    def _edit_history_record(self, history_set: HistorySet, tree: ttk.Treeview):
        """Edit selected history record."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return
        
        idx = int(selection[0])
        record = history_set.records[idx]
        config = HISTORY_TYPES[history_set.history_type]
        
        # Show edit dialog
        dialog = HistoryEditDialog(self.root, record, config)
        self.root.wait_window(dialog.top)
        
        if dialog.result:
            record.edited_data.update(dialog.result)
            
            # Update tree
            values = []
            for field_def in config['fields']:
                val = record.final_data.get(field_def['key'], '')
                values.append(val)
            tree.item(selection[0], values=values)
        
        self._update_summary()
    
    def _add_history_record(self, history_set: HistorySet, tree: ttk.Treeview, config: Dict):
        """Add new history record."""
        record = HistoryRecord(record_type=history_set.history_type)
        
        dialog = HistoryEditDialog(self.root, record, config, title="Add Record")
        self.root.wait_window(dialog.top)
        
        if dialog.result:
            record.data = dialog.result
            history_set.records.append(record)
            
            # Add to tree
            values = [record.data.get(f['key'], '') for f in config['fields']]
            tree.insert('', 'end', values=values, iid=str(len(history_set.records) - 1))
        
        self._update_summary()
    
    def _delete_history_record(self, history_set: HistorySet, tree: ttk.Treeview):
        """Delete selected history record."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Delete this record?"):
            return
        
        idx = int(selection[0])
        del history_set.records[idx]
        tree.delete(selection[0])
        
        self._update_summary()
    
    # ========================================================================
    # TAB 6: OTHER INFO
    # ========================================================================
    
    def _populate_other_tab(self):
        """Populate other information tab."""
        tab = self.tab_other
        
        if not self.change_set.other_info:
            ttk.Label(
                tab,
                text="No additional information extracted.",
                foreground='gray',
                font=('Arial', 11)
            ).pack(pady=50)
            return
        
        # Instructions
        ttk.Label(
            tab,
            text="Additional extracted information (not mapped to InfoTems fields).",
            foreground='gray'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Display as formatted text
        text = tk.Text(tab, wrap=tk.WORD, font=('Consolas', 10), height=30)
        text.pack(fill=tk.BOTH, expand=True)
        
        # Format the data
        content = json.dumps(self.change_set.other_info, indent=2, default=str)
        text.insert('1.0', content)
        
        # Make read-only
        text.configure(state='disabled')
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    def _update_summary(self):
        """Update summary label."""
        self.summary_label.configure(text=self._get_summary_text())
    
    def _cancel(self):
        """Cancel and close."""
        if messagebox.askyesno("Confirm", "Discard all changes and close?"):
            self.result = None
            self.root.destroy()
    
    def _save_draft(self):
        """Save current state as draft."""
        # Update all values from UI
        for change in self.change_set.changes:
            if change.field_key in self.field_vars:
                change.edited_value = self.field_vars[change.field_key].get()
            if change.field_key in self.approval_vars:
                change.approved = self.approval_vars[change.field_key].get()
        
        # Save to file
        draft_path = Path(self.change_set.source_file).with_suffix('.draft.json')
        
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(self.change_set.to_dict(), f, indent=2, default=str)
            messagebox.showinfo("Saved", f"Draft saved to:\n{draft_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save draft: {e}")
    
    def _apply_changes(self):
        """Apply all approved changes."""
        # Sync UI values to change_set
        for change in self.change_set.changes:
            if change.field_key in self.field_vars:
                change.edited_value = self.field_vars[change.field_key].get()
            if change.field_key in self.approval_vars:
                change.approved = self.approval_vars[change.field_key].get()
        
        # Confirm
        summary = self._get_summary_text()
        if not messagebox.askyesno("Confirm", f"Apply changes?\n\n{summary}"):
            return
        
        # Call callback
        if self.on_apply:
            self.result = self.change_set
            self.on_apply(self.change_set)
        
        self.root.destroy()
    
    def run(self) -> Optional[ChangeSet]:
        """Run the GUI and return result."""
        self.root.mainloop()
        return self.result


# ============================================================================
# DIALOGS
# ============================================================================

class FamilySearchDialog:
    """Dialog for selecting a contact from search results."""
    
    def __init__(self, parent, fm: FamilyMember, results: List[Dict]):
        self.selected_contact = None
        
        self.top = tk.Toplevel(parent)
        self.top.title("Select Contact")
        self.top.geometry("600x400")
        self.top.transient(parent)
        self.top.grab_set()
        
        # Results list
        frame = ttk.Frame(self.top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text=f"Search results for: {fm.display_name}",
            font=('Arial', 11, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Listbox
        self.listbox = tk.Listbox(frame, font=('Arial', 10), height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        for r in results:
            display = f"{r.get('DisplayAs', 'Unknown')} (ID: {r.get('Id')}) - {r.get('_match_method', 'name')}"
            self.listbox.insert(tk.END, display)
        
        self.results = results
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Select", command=self._select).pack(side=tk.RIGHT)
    
    def _select(self):
        selection = self.listbox.curselection()
        if selection:
            self.selected_contact = self.results[selection[0]]
        self.top.destroy()


class HistoryEditDialog:
    """Dialog for editing a history record."""
    
    def __init__(self, parent, record: HistoryRecord, config: Dict, title: str = "Edit Record"):
        self.result = None
        self.entries = {}
        
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x400")
        self.top.transient(parent)
        self.top.grab_set()
        
        frame = ttk.Frame(self.top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create fields
        data = record.final_data
        
        for i, field_def in enumerate(config['fields']):
            key = field_def['key']
            label = field_def['label']
            
            ttk.Label(frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=3)
            
            entry = ttk.Entry(frame, width=40)
            entry.insert(0, data.get(key, ''))
            entry.grid(row=i, column=1, sticky=tk.EW, pady=3, padx=(10, 0))
            
            self.entries[key] = entry
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(config['fields']), column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
    
    def _save(self):
        self.result = {key: entry.get() for key, entry in self.entries.items()}
        self.top.destroy()


# ============================================================================
# LEGACY WRAPPER
# ============================================================================

# Keep old class name for compatibility
ChangeReviewGUI = ApprovalGUI


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    # Test with mock data
    from infotems_comparator import ChangeSet, FieldChange, ChangeType, FamilyMember, HistorySet, HistoryRecord
    
    cs = ChangeSet(
        contact_name="Test, Client",
        a_number="A123456789",
        document_type="asylum_questionnaire",
    )
    
    cs.changes = [
        FieldChange("first_name", "First Name", "John", "Juan", 0.95, ChangeType.MODIFIED, "FirstName"),
        FieldChange("last_name", "Last Name", "Doe", "Doe", 0.98, ChangeType.UNCHANGED, "LastName"),
        FieldChange("date_of_birth", "Date of Birth", None, "1990-01-15", 0.92, ChangeType.NEW, "BirthDate", True),
    ]
    
    cs.family_members = [
        FamilyMember(
            relationship="spouse",
            extracted_data={'first_name': 'Maria', 'last_name': 'Garcia', 'date_of_birth': '1992-05-20'},
            confidence=0.9
        )
    ]
    
    cs.history['address'] = HistorySet(
        history_type='address',
        records=[
            HistoryRecord('address', {'address_line1': '123 Main St', 'city': 'New York', 'state': 'NY'}, is_current=True),
            HistoryRecord('address', {'address_line1': '456 Oak Ave', 'city': 'Brooklyn', 'state': 'NY'}),
        ]
    )
    
    gui = ApprovalGUI(cs)
    result = gui.run()
    
    if result:
        print("Changes approved!")
        print(json.dumps(result.to_dict(), indent=2, default=str))
