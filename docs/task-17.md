# Task 17: Automated Tests and Bug Fixes
- The test suite covers models, forms, views, CRUD, courses, authentication, roles, search, the API, email, file uploads, invalid input, unauthorized access and missing records.
- Results are in docs/test-results.txt and docs/coverage.txt. Known bugs and limitations are in docs/known-issues.md.
- Bug fixed: bulk deletes left uploaded files behind, so I moved the cleanup to a post_delete signal and added a test.
- Errors and fixes: several test failures came from my own helpers or old test data (a text course instead of a Course object), and I fixed the code or the data, never by weakening tests.