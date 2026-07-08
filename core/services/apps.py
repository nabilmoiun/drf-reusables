from django.apps import apps

EXCLUDED_APPS = {
    "admin",
    "auth",
    "contenttypes",
    "sessions",
    "authtoken",
    "token_blacklist",
}


def get_all_model_names():
    return sorted([
        model._meta.model_name
        for model in apps.get_models()
        if not model._meta.app_label in EXCLUDED_APPS
    ])
