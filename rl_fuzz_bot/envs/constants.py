

# Action identifiers (Discrete actions 0–3)
START_CMD = 0
CANCEL_CMD = 1
STATUS_POLL = 2
HEARTBEAT = 3

# Base latencies (in milliseconds) 
BASE_LATENCY = {
    START_CMD: 80,
    CANCEL_CMD: 60,
    STATUS_POLL: 40,
    HEARTBEAT: 20,
}

# Maximum number of steps/episode
MAX_STEPS = 20

# Standard deviation (ms) for per-hop latency jitter
LATENCY_JITTER_STD = 5.0

# Probability of injecting a transient fault on any message
FAULT_PROB = 0.05
