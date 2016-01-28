from os.path import join as pjoin, abspath, dirname, pardir


SECRET_KEY = 'SECRET'
PROJ_ROOT = abspath(pjoin(dirname(__file__), pardir))

ADMINS = (
    ('Example', 'tests@example.net'),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
MEDIA_ROOT = pjoin(PROJ_ROOT, 'media')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'tests.urls'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tests.testapp',
    'scrubpii',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
