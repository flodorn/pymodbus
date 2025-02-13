# Pymodbus REPL Server

Pymodbus REPL server helps to quicky spin an [asynchronous server](../../../examples/common/asyncio_server.py) from command line.

Support both `Modbus TCP` and `Modbus RTU` server.


Some features offered are

---
1. Runs a [reactive server](../../server/reactive/main.py) in `REPL` and `NON REPL` mode.
2. Exposes REST API's to manipulate the behaviour of the server in non repl mode.
3. Ability to manipulate the out-going response dynamically (either via REPL console or via REST API request).
4. Ability to delay the out-going response dynamically (either via REPL console or via REST API request).
5. Auto revert to normal response after pre-defined number of manipulated responses.

## Installation
Install `pymodbus` with the required dependencies

`pip install pymodbus[repl]`

## Docker
Pull Docker image with everything installed

`docker pull riptideio/pymodbus`

## Usage

Invoke REPL server with `pymodbus.server run` command.

```shell
 ✗ pymodbus.server --help

 Usage: pymodbus.server [OPTIONS] COMMAND [ARGS]...

 Reactive modebus server

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --host                                    TEXT     Host address [default: localhost]                                       │
│ --web-port                                INTEGER  Web app port [default: 8080]                                            │
│                       -b                           Support broadcast messages                                              │
│ --repl                    --no-repl                Enable/Disable repl for server [default: repl]                          │
│ --verbose                 --no-verbose             Run with debug logs enabled for pymodbus [default: no-verbose]          │
│ --install-completion                               Install completion for the current shell.                               │
│ --show-completion                                  Show completion for the current shell, to copy it or customize the      │
│                                                    installation.                                                           │
│ --help                                             Show this message and exit.                                             │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ run              Run Reactive Modbus server.                                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

If using the docker image, you can run all the same commands, prepending the `docker run` command. For example:

```shell
docker run -it riptideio/pymodbus pymodbus.server --help
```

```shell
✗ pymodbus.server run --help

 Usage: pymodbus.server run [OPTIONS]

 Run Reactive Modbus server.
 Exposing REST endpoint for response manipulation.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --modbus-server  -s      TEXT     Modbus Server [default: ModbusServerTypes.tcp]                                           │
│ --framer         -f      TEXT     Modbus framer to use [default: ModbusFramerTypes.socket]                                 │
│ --modbus-port    -p      TEXT     Modbus port [default: 5020]                                                              │
│ --unit-id        -u      INTEGER  Supported Modbus unit id's [default: None]                                               │
│ --modbus-config          PATH     Path to additional modbus server config [default: None]                                  │
│ --random         -r      INTEGER  Randomize every `r` reads. 0=never, 1=always,2=every-second-read, and so on. Applicable  │
│                                   IR and DI.                                                                               │
│                                   [default: 0]                                                                             │
│ --help                            Show this message and exit.                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Pymodbus Server REPL mode

The REPL server comes with auto-completion and can be installed for the supported shell with `pymodbus.server --install-completion <shell>`.
Don't forget to restart the terminal for the auto-completion to kick-in. Use `TAB` key to show auto-completion.

Example usage.

```shell
✗ pymodbus.server run --modbus-server tcp --framer socket --unit-id 1 --unit-id 4 --random 2

__________                          .______.                    _________
\______   \___.__. _____   ____   __| _/\_ |__  __ __  ______  /   _____/ ______________  __ ___________
 |     ___<   |  |/     \ /  _ \ / __ |  | __ \|  |  \/  ___/  \_____  \_/ __ \_  __ \  \/ // __ \_  __ \\
 |    |    \___  |  Y Y  (  <_> ) /_/ |  | \_\ \  |  /\___ \   /        \  ___/|  | \/\   /\  ___/|  | \/
 |____|    / ____|__|_|  /\____/\____ |  |___  /____//____  > /_______  /\___  >__|    \_/  \___  >__|
           \/          \/            \/      \/           \/          \/     \/                 \/

SERVER > help
Available commands:
clear                                        Clears screen
manipulator                                  Manipulate response from server.
Usage: manipulator response_type=|normal|error|delayed|empty|stray
        Additional parameters
                error_code=<int>
                delay_by=<in seconds>
                clear_after=<clear after n messages int>
                data_len=<length of stray data (int)>

        Example usage:
        1. Send error response 3 for 4 requests
           manipulator response_type=error error_code=3 clear_after=4
        2. Delay outgoing response by 5 seconds indefinitely
           manipulator response_type=delayed delay_by=5
        3. Send empty response
           manipulator response_type=empty
        4. Send stray response of length 12 and revert to normal after 2 responses
           manipulator response_type=stray data_len=11 clear_after=2
        5. To disable response manipulation
           manipulator response_type=normal
```

[![Pymodbus Server REPL](https://img.youtube.com/vi/OutaVz0JkWg/maxresdefault.jpg)](https://youtu.be/OutaVz0JkWg)
