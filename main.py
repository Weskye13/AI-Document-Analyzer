"""
AI Document Analyzer - Main Application
========================================

Main orchestration script for the AI Document Analyzer.
Provides both GUI and CLI interfaces for processing documents.

Workflow:
1. Load document (PDF/image)
2. AI extracts data using Claude Vision
3. Compare with existing InfoTems record
4. Show approval GUI for user review
5. Apply approved changes to InfoTems

Author: Law Office of Joshua E. Bardavid
Version: 1.0.0
Date: January 2026
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from datetime import datetime
import sys
import json
import threading
import argparse

from config import UI_CONFIG, DOCUMENT_TYPES, SCRIPT_DIR
from document_extractor import DocumentExtractor
from enhanced_extractor import EnhancedDocumentExtractor
from infotems_comparator import InfotemsComparator, ChangeSet
from approval_gui import ChangeReviewGUI, BatchReviewGUI


class DocumentAnalyzerApp:
    """
    Main application GUI for AI Document Analyzer.
    
    Provides:
    - Document selection (single or batch)
    - Document type selection or auto-detection
    - Progress tracking
    - Results display
    - Integration with approval workflow
    """
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title(UI_CONFIG['window_title'])
        self.root.geometry(UI_CONFIG['window_size'])
        self.root.minsize(1000, 700)
        
        # State
        self.selected_files: list = []
        self.processing = False
        self.extractor = None
        self.comparator = None
        self.change_sets: list = []
        
        # Initialize components
        self._init_components()
        
        # Create GUI
        self._create_widgets()
        
        self.log("✅ Application initialized")
        self.log("📋 Ready to analyze documents")
    
    def _init_components(self):
        """Initialize extractor and comparator components."""
        try:
            # Use enhanced extractor by default for better accuracy
            self.extractor = EnhancedDocumentExtractor(verbose=False, use_enhanced=True)
            self.log("✓ Enhanced AI Extractor ready (multi-pass mode)")
        except Exception as e:
            # Fall back to basic extractor
            try:
                self.extractor = DocumentExtractor(verbose=False)
                self.log("✓ Basic AI Extractor ready")
            except Exception as e2:
                self.log(f"⚠ AI Extractor error: {e2}", 'error')
        
        try:
            self.comparator = InfotemsComparator(verbose=False)
            self.log("✓ InfoTems connection ready")
        except Exception as e:
            self.log(f"⚠ InfoTems connection error: {e}", 'error')
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header(main)
        
        # File selection
        self._create_file_section(main)
        
        # Options
        self._create_options_section(main)
        
        # Progress
        self._create_progress_section(main)
        
        # Log
        self._create_log_section(main)
        
        # Buttons
        self._create_buttons(main)
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header,
            text="🔍 AI DOCUMENT ANALYZER",
            font=UI_CONFIG['header_font']
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header,
            text="Extract data from documents and update InfoTems automatically",
            foreground='gray'
        ).pack(anchor=tk.W)
    
    def _create_file_section(self, parent):
        """Create file selection section."""
        frame = ttk.LabelFrame(parent, text="Select Documents", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # File list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.X)
        
        self.file_listbox = tk.Listbox(
            list_frame,
            height=4,
            selectmode=tk.EXTENDED,
            font=('Arial', 9)
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="📂 Add Files...", command=self._add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📁 Add Folder...", command=self._add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Clear All", command=self._clear_files).pack(side=tk.LEFT, padx=5)
        
        # File count label
        self.file_count_label = ttk.Label(btn_frame, text="0 files selected", foreground='gray')
        self.file_count_label.pack(side=tk.RIGHT, padx=5)
    
    def _create_options_section(self, parent):
        """Create options section."""
        frame = ttk.LabelFrame(parent, text="Options", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Document type selection
        type_frame = ttk.Frame(frame)
        type_frame.pack(fill=tk.X)
        
        ttk.Label(type_frame, text="Document Type:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.doc_type_var = tk.StringVar(value="auto")
        
        type_options = [("Auto-detect", "auto")] + [
            (config['display_name'], key) 
            for key, config in DOCUMENT_TYPES.items()
        ]
        
        self.doc_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.doc_type_var,
            values=[opt[0] for opt in type_options],
            state='readonly',
            width=30
        )
        self.doc_type_combo.current(0)
        self.doc_type_combo.pack(side=tk.LEFT)
        
        # Store mapping
        self._type_map = {opt[0]: opt[1] for opt in type_options}
        
        # Options checkboxes
        check_frame = ttk.Frame(frame)
        check_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.auto_approve_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            check_frame,
            text="Auto-approve high-confidence changes (>95%)",
            variable=self.auto_approve_var
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        self.create_contacts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            check_frame,
            text="Create new contacts if not found",
            variable=self.create_contacts_var
        ).pack(side=tk.LEFT)
    
    def _create_progress_section(self, parent):
        """Create progress section."""
        frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(frame, text="Ready", foreground='gray')
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_log_section(self, parent):
        """Create activity log section."""
        frame = ttk.LabelFrame(parent, text="Activity Log", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = ScrolledText(
            frame,
            height=12,
            font=UI_CONFIG['log_font'],
            state=tk.DISABLED,
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.log_text.tag_config('timestamp', foreground='#6a9955')
        self.log_text.tag_config('info', foreground='#d4d4d4')
        self.log_text.tag_config('success', foreground='#4ec9b0')
        self.log_text.tag_config('error', foreground='#f14c4c')
        self.log_text.tag_config('warning', foreground='#cca700')
    
    def _create_buttons(self, parent):
        """Create action buttons."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="⚙ Settings", command=self._show_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❓ Help", command=self._show_help).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="❌ Exit", command=self._exit).pack(side=tk.RIGHT, padx=5)
        
        self.analyze_btn = ttk.Button(
            btn_frame,
            text="🔍 Analyze Documents",
            command=self._start_analysis,
            style='Accent.TButton'
        )
        self.analyze_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_status_bar(self):
        """Create status bar."""
        status = ttk.Frame(self.root)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Separator(status, orient='horizontal').pack(fill=tk.X)
        
        inner = ttk.Frame(status, padding=(10, 5))
        inner.pack(fill=tk.X)
        
        self.status_label = ttk.Label(inner, text="Status: Ready", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Label(inner, text="v1.0.0", font=('Arial', 9), foreground='gray').pack(side=tk.RIGHT)
    
    # ========================================================================
    # FILE MANAGEMENT
    # ========================================================================
    
    def _add_files(self):
        """Add files via file dialog."""
        files = filedialog.askopenfilenames(
            title="Select Documents",
            filetypes=[
                ("All supported", "*.pdf *.png *.jpg *.jpeg *.gif *.webp"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("All files", "*.*")
            ]
        )
        
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
        
        self._update_file_count()
    
    def _add_folder(self):
        """Add all documents from a folder."""
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return
        
        folder_path = Path(folder)
        extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp']
        
        count = 0
        for ext in extensions:
            for f in folder_path.glob(f'*{ext}'):
                if str(f) not in self.selected_files:
                    self.selected_files.append(str(f))
                    self.file_listbox.insert(tk.END, f.name)
                    count += 1
        
        self.log(f"Added {count} files from {folder_path.name}")
        self._update_file_count()
    
    def _remove_selected(self):
        """Remove selected files."""
        selection = list(self.file_listbox.curselection())
        selection.reverse()  # Remove from end to preserve indices
        
        for idx in selection:
            self.file_listbox.delete(idx)
            del self.selected_files[idx]
        
        self._update_file_count()
    
    def _clear_files(self):
        """Clear all files."""
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self._update_file_count()
    
    def _update_file_count(self):
        """Update file count label."""
        count = len(self.selected_files)
        self.file_count_label.config(text=f"{count} file(s) selected")
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    def log(self, message: str, level: str = 'info'):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"{timestamp}  ", 'timestamp')
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_progress(self, value: float, text: str):
        """Update progress bar and label."""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    
    def _start_analysis(self):
        """Start document analysis."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select at least one document.")
            return
        
        if self.processing:
            messagebox.showinfo("Processing", "Analysis already in progress.")
            return
        
        if not self.extractor:
            messagebox.showerror("Error", "AI Extractor not available. Check API key.")
            return
        
        if not self.comparator:
            messagebox.showerror("Error", "InfoTems connection not available. Check credentials.")
            return
        
        # Get selected document type
        type_display = self.doc_type_combo.get()
        doc_type = self._type_map.get(type_display, "auto")
        if doc_type == "auto":
            doc_type = None
        
        self.processing = True
        self.analyze_btn.config(state=tk.DISABLED)
        self.change_sets.clear()
        
        # Run in thread
        threading.Thread(
            target=self._run_analysis,
            args=(doc_type,),
            daemon=True
        ).start()
    
    def _run_analysis(self, doc_type: str):
        """Run analysis in background thread."""
        total = len(self.selected_files)
        
        try:
            for i, file_path in enumerate(self.selected_files):
                file_name = Path(file_path).name
                
                # Update progress
                progress = (i / total) * 100
                self.root.after(0, lambda p=progress, t=f"Processing {i+1}/{total}: {file_name}": 
                               self.update_progress(p, t))
                self.root.after(0, lambda f=file_name: self.log(f"\n📄 Processing: {f}"))
                
                try:
                    # Extract data
                    self.root.after(0, lambda: self.log("  🔍 Extracting data..."))
                    extracted = self.extractor.extract_data(file_path, doc_type)
                    
                    if extracted.get('errors'):
                        for err in extracted['errors']:
                            self.root.after(0, lambda e=err: self.log(f"  ⚠ {e}", 'warning'))
                        continue
                    
                    self.root.after(0, lambda d=extracted['document_type']: 
                                   self.log(f"  ✓ Detected: {d}"))
                    
                    # Compare with InfoTems
                    self.root.after(0, lambda: self.log("  📊 Comparing with InfoTems..."))
                    change_set = self.comparator.compare(extracted, file_path)
                    
                    if change_set.errors:
                        for err in change_set.errors:
                            self.root.after(0, lambda e=err: self.log(f"  ⚠ {e}", 'warning'))
                    else:
                        self.root.after(0, lambda c=change_set.total_changes: 
                                       self.log(f"  ✓ Found {c} changes", 'success'))
                        self.change_sets.append(change_set)
                    
                except Exception as e:
                    self.root.after(0, lambda e=str(e): self.log(f"  ❌ Error: {e}", 'error'))
            
            # Complete
            self.root.after(0, lambda: self.update_progress(100, "Complete"))
            self.root.after(0, lambda: self.log(f"\n✅ Processed {total} document(s)", 'success'))
            
            # Show review GUI if changes found
            if self.change_sets:
                self.root.after(100, self._show_review_gui)
            else:
                self.root.after(0, lambda: self.log("ℹ No changes to review"))
            
        finally:
            self.processing = False
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
    
    def _show_review_gui(self):
        """Show the review GUI for approving changes."""
        if len(self.change_sets) == 1:
            # Single document - show individual review
            gui = ChangeReviewGUI(
                self.change_sets[0],
                on_approve=self._apply_single_changeset
            )
            result = gui.run()
        else:
            # Multiple documents - show batch review
            gui = BatchReviewGUI(self.change_sets)
            result = gui.run()
            
            if result == 'apply':
                self._apply_all_changesets()
    
    def _apply_single_changeset(self, change_set: ChangeSet):
        """Apply a single change set."""
        self.log(f"\n📤 Applying changes for {change_set.contact_name}...")
        
        try:
            result = self.comparator.apply_changes(change_set)
            
            if result['success']:
                self.log(f"✅ Changes applied successfully!", 'success')
                if result.get('contact_created'):
                    self.log(f"   New contact ID: {result['contact_id']}")
                if result.get('fields_updated'):
                    self.log(f"   Updated fields: {', '.join(result['fields_updated'])}")
            else:
                for err in result.get('errors', []):
                    self.log(f"❌ {err}", 'error')
                    
        except Exception as e:
            self.log(f"❌ Error applying changes: {e}", 'error')
    
    def _apply_all_changesets(self):
        """Apply all change sets."""
        self.log(f"\n📤 Applying changes for {len(self.change_sets)} documents...")
        
        success_count = 0
        error_count = 0
        
        for cs in self.change_sets:
            if not cs.approved_changes:
                continue
            
            try:
                result = self.comparator.apply_changes(cs)
                
                if result['success']:
                    success_count += 1
                    self.log(f"✓ {cs.contact_name}: {len(cs.approved_changes)} changes applied", 'success')
                else:
                    error_count += 1
                    self.log(f"✗ {cs.contact_name}: Failed", 'error')
                    
            except Exception as e:
                error_count += 1
                self.log(f"✗ {cs.contact_name}: {e}", 'error')
        
        self.log(f"\n✅ Complete: {success_count} success, {error_count} errors", 'success')
    
    # ========================================================================
    # DIALOGS
    # ========================================================================
    
    def _show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo("Settings", "Settings dialog - Coming soon")
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """AI Document Analyzer - Help

WORKFLOW:
1. Add documents (PDF or images)
2. Select document type (or use auto-detect)
3. Click "Analyze Documents"
4. Review proposed changes
5. Approve and apply to InfoTems

SUPPORTED DOCUMENTS:
• Questionnaires
• Passports
• EAD Cards
• Green Cards
• Birth Certificates
• ID Cards
• I-94 Records

For support, contact the IT department."""
        
        messagebox.showinfo("Help", help_text)
    
    def _exit(self):
        """Exit the application."""
        if self.processing:
            if not messagebox.askyesno("Confirm", "Processing in progress. Exit anyway?"):
                return
        
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


# ============================================================================
# CLI INTERFACE
# ============================================================================

def process_document_cli(file_path: str, doc_type: str = None, apply: bool = False, use_enhanced: bool = True):
    """
    Process a document via CLI.
    
    Args:
        file_path: Path to document
        doc_type: Document type (or None for auto-detect)
        apply: Whether to apply changes without review
        use_enhanced: Use multi-pass enhanced extraction (default True)
    """
    print("\n" + "="*60)
    print("AI DOCUMENT ANALYZER - CLI MODE")
    print("="*60)
    
    # Initialize
    print("\n[1/4] Initializing...")
    if use_enhanced:
        extractor = EnhancedDocumentExtractor(verbose=True, use_enhanced=True)
        print("Using: Enhanced multi-pass extraction")
    else:
        extractor = DocumentExtractor(verbose=True)
        print("Using: Basic single-pass extraction")
    comparator = InfotemsComparator(verbose=True)
    
    # Extract
    print("\n[2/4] Extracting data...")
    if use_enhanced:
        extracted = extractor.extract_from_file(file_path)
    else:
        extracted = extractor.extract_data(file_path, doc_type)
    
    if extracted.get('errors'):
        print("\n❌ Extraction errors:")
        for err in extracted['errors']:
            print(f"  - {err}")
        return
    
    # Compare
    print("\n[3/4] Comparing with InfoTems...")
    change_set = comparator.compare(extracted, file_path)
    
    # Display changes
    print("\n" + "="*60)
    print("PROPOSED CHANGES")
    print("="*60)
    
    print(f"\nClient: {change_set.contact_name}")
    print(f"A-Number: {change_set.a_number}")
    print(f"Document Type: {change_set.document_type}")
    print(f"Contact ID: {change_set.contact_id or 'NEW'}")
    print(f"Total Changes: {change_set.total_changes}")
    
    if change_set.total_changes > 0:
        print("\nChanges:")
        for change in change_set.changes:
            if change.has_change:
                print(f"  {change.field_label}: '{change.current_value}' → '{change.new_value}'")
    
    # Apply if requested
    if apply and change_set.total_changes > 0:
        print("\n[4/4] Applying changes...")
        result = comparator.apply_changes(change_set)
        
        if result['success']:
            print("\n✅ Changes applied successfully!")
        else:
            print("\n❌ Errors:")
            for err in result.get('errors', []):
                print(f"  - {err}")
    else:
        print("\n[4/4] Skipping apply (use --apply to apply changes)")
    
    print("\n" + "="*60)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Document Analyzer - Extract document data and update InfoTems"
    )
    parser.add_argument(
        'file', 
        nargs='?', 
        help='Document file path (for CLI mode)'
    )
    parser.add_argument(
        '--type', '-t',
        choices=list(DOCUMENT_TYPES.keys()),
        help='Document type (default: auto-detect)'
    )
    parser.add_argument(
        '--apply', '-a',
        action='store_true',
        help='Apply changes without review (CLI only)'
    )
    parser.add_argument(
        '--basic', '-b',
        action='store_true',
        help='Use basic single-pass extraction instead of enhanced multi-pass'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Force GUI mode even with file argument'
    )
    
    args = parser.parse_args()
    
    if args.file and not args.gui:
        # CLI mode
        process_document_cli(args.file, args.type, args.apply, use_enhanced=not args.basic)
    else:
        # GUI mode
        app = DocumentAnalyzerApp()
        app.run()


if __name__ == "__main__":
    main()
