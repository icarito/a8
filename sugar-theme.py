def setup(activity):
    # Simple signal handler to annotate files
    activity.files.tab_icon.set_from_file("icons/folder.svg")
    activity.terminals.tab_icon.set_from_file("icons/activity-terminal.svg")
    activity.bookmarks.tab_icon.set_from_file("icons/star.svg")
