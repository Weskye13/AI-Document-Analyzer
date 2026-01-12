"""
AI Document Analyzer - Approval GUI
====================================

Tkinter GUI for reviewing and approving document data changes
before they are applied to InfoTems.

Features:
- Side-by-side comparison view
- Color-coded change indicators
- Checkbox approval for each field
- Bulk approve/reject options
- Change summary and confidence display

Author: Law Office of Joshua E. Bardavid
Version: 1.0.0
Date: January 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json

from config import UI_CONFIG, CHANGE_COLORS
from infotems_comparator import ChangeSet, FieldChange


class ChangeReviewGUI:
    """
    GUI for reviewing proposed InfoTems changes.
    
    Displays current vs. new values and allows user to approve/reject
    individual changes before they are applied.
    """
    
    def __init__(self, change_set: ChangeSet, on_approve: Callable[[ChangeSet], None] = None):
        """
        Initialize the review GUI.
        
        Args:
            change_set: ChangeSet with proposed changes
            on_approve: Callback when user approves changes
        """
        self.change_set = change_set
        self.on_approve = on_approve
        self.result = None
        
        # Create root window
        self.root = tk.Tk()
        self.root.title(f"{UI_CONFIG['window_title']} - Review Changes")
        self.root.geometry(UI_CONFIG['window_size'])
        self.root.minsize(1000, 700)
        
        # Track checkboxes
        self.checkboxes: Dict[str, tk.BooleanVar] = {}
        
        self._create_widgets()
        self._populate_data()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self._create_header(main)
        
        # Document info section
        self._create_info_section(main)
        
        # Changes table
        self._create_changes_table(main)
        
        # Action buttons
        self._create_buttons(main)
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self, parent):
        """Create header with title and summary."""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        ttk.Label(
            header,
            text="📋 REVIEW PROPOSED CHANGES",
            font=UI_CONFIG['header_font']
        ).pack(anchor=tk.W)
        
        # Subtitle with change count
        total = self.change_set.total_changes
        subtitle = f"Review {total} proposed change(s) before applying to InfoTems"
        ttk.Label(header, text=subtitle, foreground='gray').pack(anchor=tk.W)
    
    def _create_info_section(self, parent):
        """Create document and client info section."""
        info_frame = ttk.LabelFrame(parent, text="Document Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid layout for info
        info_data = [
            ("Client:", self.change_set.contact_name or "Unknown"),
            ("A-Number:", self.change_set.a_number or "N/A"),
            ("Document Type:", self.change_set.document_type),
            ("Source File:", Path(self.change_set.source_file).name if self.change_set.source_file else "N/A"),
            ("Extraction Confidence:", f"{self.change_set.extraction_confidence:.0%}"),
            ("Contact ID:", str(self.change_set.contact_id) if self.change_set.contact_id else "NEW CONTACT"),
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(info_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )
            
            # Color code contact ID
            fg = None
            if label == "Contact ID:" and value == "NEW CONTACT":
                fg = CHANGE_COLORS['new']
            
            ttk.Label(info_frame, text=value, foreground=fg).grid(
                row=row, column=col + 1, sticky=tk.W, padx=(0, 20), pady=2
            )
    
    def _create_changes_table(self, parent):
        """Create table showing proposed changes."""
        table_frame = ttk.LabelFrame(parent, text="Proposed Changes", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview with columns
        columns = ('approved', 'field', 'current', 'arrow', 'new', 'confidence', 'type')
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=15
        )
        
        # Configure columns
        self.tree.heading('approved', text='✓')
        self.tree.heading('field', text='Field')
        self.tree.heading('current', text='Current Value')
        self.tree.heading('arrow', text='')
        self.tree.heading('new', text='New Value')
        self.tree.heading('confidence', text='Conf')
        self.tree.heading('type', text='Change')
        
        self.tree.column('approved', width=40, anchor=tk.CENTER)
        self.tree.column('field', width=180)
        self.tree.column('current', width=250)
        self.tree.column('arrow', width=40, anchor=tk.CENTER)
        self.tree.column('new', width=250)
        self.tree.column('confidence', width=60, anchor=tk.CENTER)
        self.tree.column('type', width=80, anchor=tk.CENTER)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to toggle approval
        self.tree.bind('<Double-1>', self._toggle_approval)
        
        # Configure tags for coloring
        self.tree.tag_configure('new', foreground=CHANGE_COLORS['new'])
        self.tree.tag_configure('modified', foreground=CHANGE_COLORS['modified'])
        self.tree.tag_configure('unchanged', foreground=CHANGE_COLORS['unchanged'])
        
        # Legend
        legend_frame = ttk.Frame(table_frame)
        legend_frame.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(legend_frame, text="Legend:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(legend_frame, text="● New", foreground=CHANGE_COLORS['new']).pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="● Modified", foreground=CHANGE_COLORS['modified']).pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="● Unchanged", foreground=CHANGE_COLORS['unchanged']).pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="(Double-click to toggle approval)", foreground='gray').pack(side=tk.LEFT, padx=20)
    
    def _create_buttons(self, parent):
        """Create action buttons."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X)
        
        # Left side - bulk actions
        left = ttk.Frame(btn_frame)
        left.pack(side=tk.LEFT)
        
        ttk.Button(left, text="✓ Select All", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(left, text="✗ Deselect All", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(left, text="↻ Reset", command=self._reset_selections).pack(side=tk.LEFT, padx=5)
        
        # Right side - main actions
        right = ttk.Frame(btn_frame)
        right.pack(side=tk.RIGHT)
        
        ttk.Button(right, text="❌ Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        self.apply_btn = ttk.Button(
            right, 
            text="✅ Apply Approved Changes",
            command=self._apply_changes,
            style='Accent.TButton'
        )
        self.apply_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_status_bar(self):
        """Create status bar at bottom."""
        status = ttk.Frame(self.root)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Separator(status, orient='horizontal').pack(fill=tk.X)
        
        inner = ttk.Frame(status, padding=(10, 5))
        inner.pack(fill=tk.X)
        
        self.status_label = ttk.Label(inner, text="Ready", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Label(inner, text="v1.0.0", font=('Arial', 9), foreground='gray').pack(side=tk.RIGHT)
    
    def _populate_data(self):
        """Populate the changes table."""
        for change in self.change_set.changes:
            # Only show fields with actual changes by default
            if not change.has_change:
                continue
            
            # Determine display values
            approved = "☑" if change.approved else "☐"
            current = change.current_value or "(empty)"
            new = change.new_value or "(empty)"
            conf = f"{change.confidence:.0%}" if change.confidence else "N/A"
            change_type = change.change_type.capitalize()
            
            # Create checkbox var
            self.checkboxes[change.field_key] = tk.BooleanVar(value=change.approved)
            
            # Insert row
            self.tree.insert(
                '', 'end',
                values=(approved, change.field_label, current, "→", new, conf, change_type),
                tags=(change.change_type,),
                iid=change.field_key
            )
        
        self._update_status()
    
    def _toggle_approval(self, event):
        """Toggle approval status on double-click."""
        item = self.tree.selection()
        if not item:
            return
        
        field_key = item[0]
        
        # Find the change
        for change in self.change_set.changes:
            if change.field_key == field_key:
                change.approved = not change.approved
                
                # Update checkbox var
                if field_key in self.checkboxes:
                    self.checkboxes[field_key].set(change.approved)
                
                # Update display
                approved = "☑" if change.approved else "☐"
                values = list(self.tree.item(field_key, 'values'))
                values[0] = approved
                self.tree.item(field_key, values=values)
                
                break
        
        self._update_status()
    
    def _select_all(self):
        """Select all changes."""
        for change in self.change_set.changes:
            if change.has_change:
                change.approved = True
                if change.field_key in self.checkboxes:
                    self.checkboxes[change.field_key].set(True)
        
        self._refresh_tree()
        self._update_status()
    
    def _deselect_all(self):
        """Deselect all changes."""
        for change in self.change_set.changes:
            change.approved = False
            if change.field_key in self.checkboxes:
                self.checkboxes[change.field_key].set(False)
        
        self._refresh_tree()
        self._update_status()
    
    def _reset_selections(self):
        """Reset to default selections (all changes selected)."""
        for change in self.change_set.changes:
            change.approved = change.has_change
            if change.field_key in self.checkboxes:
                self.checkboxes[change.field_key].set(change.approved)
        
        self._refresh_tree()
        self._update_status()
    
    def _refresh_tree(self):
        """Refresh tree display."""
        for change in self.change_set.changes:
            if not change.has_change:
                continue
            
            approved = "☑" if change.approved else "☐"
            if change.field_key in self.tree.get_children():
                values = list(self.tree.item(change.field_key, 'values'))
                values[0] = approved
                self.tree.item(change.field_key, values=values)
    
    def _update_status(self):
        """Update status bar."""
        approved_count = len([c for c in self.change_set.changes if c.approved and c.has_change])
        total_count = self.change_set.total_changes
        
        self.status_label.config(text=f"Selected: {approved_count}/{total_count} changes")
        
        # Enable/disable apply button
        if approved_count > 0:
            self.apply_btn.config(state=tk.NORMAL)
        else:
            self.apply_btn.config(state=tk.DISABLED)
    
    def _apply_changes(self):
        """Apply approved changes."""
        approved_count = len(self.change_set.approved_changes)
        
        if approved_count == 0:
            messagebox.showinfo("No Changes", "No changes selected to apply.")
            return
        
        # Confirm
        msg = f"Apply {approved_count} change(s) to InfoTems?\n\n"
        msg += "This will update the client record in InfoTems."
        
        if not self.change_set.contact_id:
            msg += "\n\n⚠️ This will CREATE a new contact."
        
        if not messagebox.askyesno("Confirm Changes", msg):
            return
        
        # Set result and close
        self.result = 'apply'
        
        if self.on_approve:
            self.on_approve(self.change_set)
        
        self.root.destroy()
    
    def _cancel(self):
        """Cancel without applying changes."""
        if self.change_set.total_changes > 0:
            if not messagebox.askyesno("Cancel", "Discard all changes?"):
                return
        
        self.result = 'cancel'
        self.root.destroy()
    
    def run(self) -> Optional[str]:
        """
        Run the GUI.
        
        Returns:
            'apply' if changes were approved, 'cancel' otherwise
        """
        self.root.mainloop()
        return self.result


class BatchReviewGUI:
    """
    GUI for reviewing multiple documents at once.
    
    Shows summary of all documents and allows batch approval.
    """
    
    def __init__(self, change_sets: List[ChangeSet]):
        """
        Initialize batch review GUI.
        
        Args:
            change_sets: List of ChangeSets to review
        """
        self.change_sets = change_sets
        self.result = None
        
        self.root = tk.Tk()
        self.root.title(f"{UI_CONFIG['window_title']} - Batch Review")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        self._create_widgets()
        self._populate_data()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            main,
            text="📋 BATCH DOCUMENT REVIEW",
            font=UI_CONFIG['header_font']
        ).pack(anchor=tk.W)
        
        ttk.Label(
            main,
            text=f"Review {len(self.change_sets)} document(s) before applying changes",
            foreground='gray'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Summary table
        self._create_summary_table(main)
        
        # Buttons
        self._create_buttons(main)
    
    def _create_summary_table(self, parent):
        """Create summary table."""
        frame = ttk.LabelFrame(parent, text="Documents to Process", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ('idx', 'client', 'a_number', 'doc_type', 'changes', 'confidence', 'status')
        
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('idx', text='#')
        self.tree.heading('client', text='Client')
        self.tree.heading('a_number', text='A-Number')
        self.tree.heading('doc_type', text='Document Type')
        self.tree.heading('changes', text='Changes')
        self.tree.heading('confidence', text='Confidence')
        self.tree.heading('status', text='Status')
        
        self.tree.column('idx', width=40)
        self.tree.column('client', width=200)
        self.tree.column('a_number', width=120)
        self.tree.column('doc_type', width=180)
        self.tree.column('changes', width=80, anchor=tk.CENTER)
        self.tree.column('confidence', width=100, anchor=tk.CENTER)
        self.tree.column('status', width=120, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-click to open individual review
        self.tree.bind('<Double-1>', self._open_individual_review)
    
    def _create_buttons(self, parent):
        """Create action buttons."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="❌ Cancel All", command=self._cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Apply All", command=self._apply_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="📝 Review Selected", command=self._review_selected).pack(side=tk.RIGHT, padx=5)
    
    def _populate_data(self):
        """Populate the summary table."""
        for i, cs in enumerate(self.change_sets, 1):
            status = "Ready" if cs.total_changes > 0 else "No Changes"
            if cs.errors:
                status = "Error"
            
            self.tree.insert('', 'end', values=(
                i,
                cs.contact_name or "Unknown",
                cs.a_number or "N/A",
                cs.document_type,
                cs.total_changes,
                f"{cs.extraction_confidence:.0%}",
                status
            ), iid=str(i-1))
    
    def _open_individual_review(self, event):
        """Open individual review for selected document."""
        selection = self.tree.selection()
        if not selection:
            return
        
        idx = int(selection[0])
        self._review_document(idx)
    
    def _review_selected(self):
        """Review selected document."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a document to review.")
            return
        
        idx = int(selection[0])
        self._review_document(idx)
    
    def _review_document(self, idx: int):
        """Open individual review for a document."""
        if idx < 0 or idx >= len(self.change_sets):
            return
        
        cs = self.change_sets[idx]
        
        # Create individual review window
        review = ChangeReviewGUI(cs)
        review.run()
        
        # Update table after review
        self._refresh_row(idx)
    
    def _refresh_row(self, idx: int):
        """Refresh a single row in the table."""
        cs = self.change_sets[idx]
        approved_count = len(cs.approved_changes)
        
        status = f"{approved_count}/{cs.total_changes} approved"
        if cs.errors:
            status = "Error"
        
        self.tree.item(str(idx), values=(
            idx + 1,
            cs.contact_name or "Unknown",
            cs.a_number or "N/A",
            cs.document_type,
            cs.total_changes,
            f"{cs.extraction_confidence:.0%}",
            status
        ))
    
    def _apply_all(self):
        """Apply all approved changes."""
        total_changes = sum(len(cs.approved_changes) for cs in self.change_sets)
        
        if total_changes == 0:
            messagebox.showinfo("No Changes", "No changes to apply.")
            return
        
        if not messagebox.askyesno("Confirm", f"Apply {total_changes} total change(s)?"):
            return
        
        self.result = 'apply'
        self.root.destroy()
    
    def _cancel(self):
        """Cancel batch processing."""
        self.result = 'cancel'
        self.root.destroy()
    
    def run(self) -> Optional[str]:
        """Run the GUI."""
        self.root.mainloop()
        return self.result


# ============================================================================
# STANDALONE TEST
# ============================================================================

if __name__ == "__main__":
    # Create sample change set for testing
    sample_changes = [
        FieldChange(
            field_key='first_name',
            field_label='First Name',
            current_value='John',
            new_value='Jonathan',
            confidence=0.95,
            change_type='modified',
            infotems_field='FirstName',
            is_biographic=False
        ),
        FieldChange(
            field_key='cell_phone',
            field_label='Cell Phone',
            current_value=None,
            new_value='(212) 555-1234',
            confidence=0.90,
            change_type='new',
            infotems_field='CellPhone',
            is_biographic=False
        ),
        FieldChange(
            field_key='date_of_birth',
            field_label='Date of Birth',
            current_value='1990-01-15',
            new_value='1990-01-15',
            confidence=0.98,
            change_type='unchanged',
            infotems_field='BirthDate',
            is_biographic=True
        ),
    ]
    
    sample_set = ChangeSet(
        contact_id=12345,
        contact_name="DOE, John",
        a_number="A123456789",
        document_type="questionnaire",
        source_file="sample_questionnaire.pdf",
        extraction_confidence=0.92,
        changes=sample_changes
    )
    
    def on_approve(cs):
        print(f"\nApproved {len(cs.approved_changes)} changes!")
        for change in cs.approved_changes:
            print(f"  {change.field_label}: {change.current_value} → {change.new_value}")
    
    gui = ChangeReviewGUI(sample_set, on_approve=on_approve)
    result = gui.run()
    print(f"\nResult: {result}")
