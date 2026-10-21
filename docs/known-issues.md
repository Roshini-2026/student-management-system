# Known Issues and Limitations

| # | Issue | Steps to reproduce | Status |
|---|---|---|---|
| 1 | Deleting students in bulk left their files on disk | Upload a photo, then in /admin/ choose "Delete selected students". The file stayed in media/. | Fixed: files are now deleted by a post_delete signal. Test added. |
| 2 | No email when a student's course is changed | Edit an existing student and change the course. No email is printed. | Open. Email is sent only for new students. |
| 3 | A failed email is logged but not retried | Set EMAIL_MODE=smtp with a wrong password and register a student. The student is saved, the log shows a failure. | Open. A background job queue would be needed. |
| 4 | No separate enrollment history | The dashboard's "recent enrollment activity" shows the most recently changed students. | Open. Needs an Enrollment table. |
| 5 | Mobile numbers are stored without a country code | Register a student. "+91" is only displayed in the form. | Open. |
| 6 | No limit on repeated failed logins | Try many wrong passwords. | Open. A package such as django-axes would add it. |
| 7 | Uploaded files are stored on the local disk | Files are in media/ and private_media/. | Open. Production should use cloud storage with private access. |
| 8 | Static files are not served when DEBUG=False on the dev server | Set DEBUG=False and open any page. It has no styling. | Open. Production needs WhiteNoise or a web server. |
| 9 | The browsable API cannot send PATCH | Open /api/students/<id>/ in the browser. | PATCH is covered by automated tests. |
| 10 | Contact form messages are checked but not stored or emailed | Submit /contact/. Only a success message is shown. | Open. |