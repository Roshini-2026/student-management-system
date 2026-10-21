# Architecture and Code Decisions

## Structure
- core: students, courses, instructors, dashboard, emails, file handling
- accounts: registration, login, password change and reset, the setup_roles command
- api: Django REST Framework serializers, viewsets and URLs

A request goes: URL (urls.py) -> view (views.py) -> form or serializer (validation) -> model (database) -> template or JSON.

## Important decisions
- Forms: StudentForm, CourseForm and InstructorForm are ModelForms, so the model's rules (required, unique email, minimum fee) are written once. A shared BootstrapFormMixin styles every form.
- Roles: Admin, Staff and Viewer are Django groups with permissions, created by "python manage.py setup_roles" (safe to run again). Views check permissions on the server (403) and templates only hide buttons. The API reuses the same permissions through DjangoModelPermissions.
- Deleting: a course with students can't be deleted (on_delete=PROTECT), but deleting an instructor only removes the link.
- Performance: select_related for student->course, prefetch_related for course->instructors, database counts with annotate(Count), and tests prove the query count does not grow with the data.
- Email: a post_save signal calls core/emails.py through transaction.on_commit, so an email is sent only after the enrollment is saved, and failures are caught and logged without undoing the save.
- Files: random server-side names, extension, content and size checks. Photos are public under /media/. Documents are in a private folder and served only by a permission-checked view.
- Configuration: secrets and environment-specific values are in .env (python-decouple). Production-only security settings turn on when DEBUG=False.
- API: token authentication, pagination, search, filters and consistent JSON errors.
- Current limitation: there is no separate Enrollment table. Each student has one course and an enrollment status.