# adk-bot

A set of AI agents built with Google ADK as I learn/explore their SDK

## Setup

Get set up with:

```sh
uv init
uv venv
source .venv/bin/activate
uv add google-adk google-generativeai
```

## Create an agent (example)

Agents can be boostrapped quickly with the `adk` command:

```
adk create day_trip_agent
```

### Run the agent

From the terminal:

```
adk run day_trip_agent
```

With a web interface:

```
adk web --port 8000
```

The web interface makes it easy to interact with agents and debug them in real time: 

![Agent Debug](images/agent-debug.png)

