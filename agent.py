from uagents import Agent

from protocols import trip_planner_protocol

agent = Agent()

agent.include(trip_planner_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()

