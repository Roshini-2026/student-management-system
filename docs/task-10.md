# Task 10: Roles and Permissions
- Created Admin, Staff and Viewer groups with the setup_roles command.
- Views check permissions on the server (403), and buttons are also hidden in templates.
- Viewers can't see mobile number, date of birth or address, and new users start as Viewers.
- Errors and fixes: existing tests needed a superuser because normal users now need permissions.