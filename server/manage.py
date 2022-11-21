import django.conf
import sys
import pathlib

# Required for importing the server app (upper dir)
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

INSTALLED_APPS = [
    'server'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f'{root}/server/db.sqlite3'
    }
}

django.conf.settings.configure(
    INSTALLED_APPS=INSTALLED_APPS,
    DATABASES=DATABASES,
    DEFAULT_AUTO_FIELD='django.db.models.AutoField'
)

django.setup()


if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)