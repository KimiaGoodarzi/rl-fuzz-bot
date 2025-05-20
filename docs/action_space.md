Actions: 0 START_CMD | 1 CANCEL_CMD | 2 STATUS_POLL | 3 HEARTBEAT
Observations: [last_resp_code, engine_state, last_latency_ms, error_flag]
Reward: +1 on first error, -0.01 otherwise
Episode ends: on error or after 20 steps
