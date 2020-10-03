from webapi import create_app, db

webapi = create_app()


@webapi.shell_context_processor
def make_shell_context():
    # Selected packages that will be pre-imported if using 'flask shell'
    return {'db': db}
