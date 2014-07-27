def setup(app):
    # Simple signal handler to annotate files
    app.files.tab_icon.set_from_file("icons/folder.svg")
    app.terminals.tab_icon.set_from_file("icons/activity-terminal.svg")
    app.bookmarks.tab_icon.set_from_file("icons/star.svg")
