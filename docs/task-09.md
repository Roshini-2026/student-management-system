# Task 9: Registration and Login
- Added an accounts app with register, login, logout, profile, change password and password reset.
- Passwords use Django's built-in hashing, and usernames and emails must be unique.
- Student pages need login, and logout works only by POST.
- Errors and fixes: fixed the form styling mixin so it doesn't validate too early, and removed the old EMAIL_BACKEND setting.