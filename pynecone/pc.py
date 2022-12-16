"""Pynecone CLI to create, run, and deploy apps."""

import os

import httpx
import typer

from pynecone import constants, utils

# Create the app.
cli = typer.Typer()


@cli.command()
def version():
    """Get the Pynecone version."""
    utils.console.print(constants.VERSION)


@cli.command()
def init():
    """Initialize a new Pynecone app.

    Raises:
        Exit: If the app directory is invalid.
    """
    app_name = utils.get_default_app_name()

    # Make sure they don't name the app "pynecone".
    if app_name == constants.MODULE_NAME:
        utils.console.print(
            f"[red]The app directory cannot be named [bold]{constants.MODULE_NAME}."
        )
        raise typer.Exit()

    with utils.console.status(f"[bold]Initializing {app_name}"):
        # Set up the web directory.
        utils.install_bun()
        utils.initialize_web_directory()

        # Set up the app directory, only if the config doesn't exist.
        if not os.path.exists(constants.CONFIG_FILE):
            utils.create_config(app_name)
            utils.initialize_app_directory(app_name)

        # Finish initializing the app.
        utils.console.log(f"[bold green]Finished Initializing: {app_name}")


@cli.command()
def run(
    env: constants.Env = constants.Env.DEV,
    frontend: bool = True,
    backend: bool = True,
):
    """Run the app.

    Args:
        env: The environment to run the app in.
        frontend: Whether to run the frontend.
        backend: Whether to run the backend.

    Raises:
        Exit: If the app is not initialized.
    """
    # Check that the app is initialized.
    if frontend and not utils.is_initialized():
        utils.console.print(
            "[red]The app is not initialized. Run [bold]pc init[/bold] first."
        )
        raise typer.Exit()

    # Get the app module.
    utils.console.rule("[bold]Starting Pynecone App")
    app = utils.get_app()

    # Get the frontend and backend commands, based on the environment.
    frontend_cmd = backend_cmd = None
    if env == constants.Env.DEV:
        frontend_cmd, backend_cmd = utils.run_frontend, utils.run_backend
    if env == constants.Env.PROD:
        frontend_cmd, backend_cmd = utils.run_frontend_prod, utils.run_backend_prod
    assert frontend_cmd and backend_cmd, "Invalid env"

    # Run the frontend and backend.
    if frontend:
        frontend_cmd(app.app)
    if backend:
        backend_cmd(app.__name__)


@cli.command()
def deploy(dry_run: bool = False):
    """Deploy the app to the hosting service.

    Args:
        dry_run: Whether to run a dry run.
    """
    # Get the app config.
    config = utils.get_config()
    config.api_url = utils.get_production_backend_url()

    # Check if the deploy url is set.
    if config.deploy_url is None:
        typer.echo("This feature is coming soon!")
        return

    # Compile the app in production mode.
    typer.echo("Compiling production app")
    app = utils.get_app().app
    utils.export_app(app, zip=True)

    # Exit early if this is a dry run.
    if dry_run:
        return

    # Deploy the app.
    data = {"userId": config.username, "projectId": config.app_name}
    original_response = httpx.get(config.deploy_url, params=data)
    response = original_response.json()
    print("response", response)
    frontend = response["frontend_resources_url"]
    backend = response["backend_resources_url"]

    # Upload the frontend and backend.
    with open(constants.FRONTEND_ZIP, "rb") as f:
        response = httpx.put(frontend, data=f)  # type: ignore

    with open(constants.BACKEND_ZIP, "rb") as f:
        response = httpx.put(backend, data=f)  # type: ignore


main = cli


if __name__ == "__main__":
    main()
