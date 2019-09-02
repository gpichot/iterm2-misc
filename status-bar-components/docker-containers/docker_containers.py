import subprocess

import iterm2


class DockerNotRunning(Exception):
    pass


def get_docker_info(value):
    out = subprocess.run(
        ['/usr/local/bin/docker', 'info', '--format="{{.' + value + '}}"'],
        capture_output=True)
    try:
        return int(out.stdout.decode('utf-8').strip()[1:-1])
    except ValueError:
        raise DockerNotRunning


async def main(connection):
    # Define the configuration knobs:
    ds = "docker_status"
    knobs = []
    component = iterm2.StatusBarComponent(
        short_description="Docker Status",
        detailed_description=
        "Show docker status and number or running containers",
        knobs=knobs,
        exemplar=" Docker status",
        update_cadence=60,
        identifier="fr.gabrielpichot.iterm2.statusbarcomponent.docker_status")

    @iterm2.StatusBarRPC
    async def coro(knobs):
        try:
            running = get_docker_info('ContainersRunning')
            paused = get_docker_info('ContainersPaused')
            stopped = get_docker_info('ContainersStopped')
        except DockerNotRunning as e:
            print(e)
            return " Stopped"
        except Exception as e:
            print(e)
            return " Errored"

        return " {}   {}   {} ".format(running, stopped, paused)

    # Register the component.
    await component.async_register(connection, coro)

iterm2.run_forever(main)
