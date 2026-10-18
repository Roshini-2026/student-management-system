* manage.py: A command-line tool that lets you interact with your Django project.

settings.py: The control center for your project. It stores database connections, installed apps, security keys, and static files.

urls.py: It maps web addresses (URLs) to specific Python functions or views.

views.py: The brain of your app logic. It receives web requests, processes data, and sends back a response (like an HTML page or JSON data).

models.py: The blueprint for your database. We will write Python classes here, and Django turns them into database tables

asgi.py: A configuration file that helps your project run on modern, asynchronous web servers (handling real-time features like WebSockets).

wsgi.py: A configuration file that connects your Django project to traditional, synchronous web servers when launching live in production