# 3 High-Level Architecture

- **3.1 Environment** (`RemoteStartEnv`)
- **3.2 Random-Fuzzer vs. PPO Agent**
- **3.3 Test-Export Harness**
- **3.4 Dashboard & CI Integration**

---

## 3.1 Environment (`RemoteStartEnv`)

The **environment** is a virtual simulation of Ford’s remote-start protocol. It implements the standard Gymnasium API so both our random fuzzer and RL agent can interact with it.

### Key components

1. **Action space**

   - Four discrete commands:
     - `0 = START_CMD`
     - `1 = CANCEL_CMD`
     - `2 = STATUS_POLL`
     - `3 = HEARTBEAT`

2. **Observation space**

   - A dictionary containing:
     - `engine_state` (OFF, STARTING, ON)
     - `last_resp` (OK, BUSY, ERROR, TIMEOUT)
     - `latency_ms` (a 1-element float32 array for jitter)
     - `error_flag` (a 1-element binary array)

3. **reset()**

   - Zeroes out internal state and step counter
   - Returns the initial observation

4. **step(action)**
   - Increments step counter
   - Simulates latency with Gaussian jitter
   - Randomly injects a fault per `FAULT_PROB`
   - Updates `engine_state` based on the action
   - Computes a reward (+1 on fault, –0.01 per step, –0.5 on cutting off)
   - Returns `(obs, reward, done, truncated, info)`

This environment lets us catch the same kinds of faults we see on physical hardware.

---

## 3.2 Random-Fuzzer vs. PPO Agent

We attack `RemoteStartEnv` with two strategies:

### A) Random-Fuzzer

- **Script**: `tools/random_fuzzer.py`
- **Behavior**:
  1. Reset the env with a fixed seed
  2. Sample actions uniformly at random
  3. Step until termination or max steps
  4. Log any sequence that ends in a fault

### B) PPO Agent (Proximal policy optimization)

- **Training** (`tools/train_ppo.py`):

  1. Wrap `RemoteStartEnv` in Gym’s `TimeLimit`
  2. Instantiate a PPO agent with a `MultiInputPolicy`
  3. Call `model.learn(total_timesteps=…)`
  4. Save the trained model

- **Evaluation** (`tools/eval_ppo.py`):
  1. Load the saved model
  2. Run many episodes, each with a unique seed (base + episode index)
  3. Record only those sequences ending in a fault
  4. Write them to `ppo_failures.json`

**Why this combination?**

- Random gives broad coverage (“breadth”).
- PPO learns which sequences actually break the system.
- Together they find bugs faster than either alone.

---

## 3.3 Test-Export Harness

After collecting failure sequences (JSON), we need reproducible unit tests.

- **Script**: `tools/export_tests.py`
- **Input**: `my_failures.json` or `ppo_failures.json` (with `seed`, `episode`, `sequence`)
- **Output**: A `tests/generated/` directory containing one pytest file per failure:

  ```python
  def test_sequence_005():
      env = RemoteStartEnv(seed=42)
      obs, _ = env.reset(seed=42 + 5)
      for action in [1, 0, 0, 3, 0]:
          obs, reward, done, truncated, _ = env.step(action)
      assert done and reward > 0.0
  ```

## 3.4 Dashboard & CI Integration

### Streamlit Dashboard (`app.py`)

- **Metrics**  
  Side‐by‐side cards showing:

  - **Random failures** count
  - **PPO failures** count

- **Sample table**  
  Displays the top few failure records (`seed`, `episode`, `sequence`) for quick inspection.

- **Raw JSON**  
  A JSON widget that shows the exact `seed`, `episode`, and `sequence` for the selected record.

- **Replay**  
  Step through any recorded sequence action-by-action, with rows highlighted where `error_flag == 1`.

- **Charts**  
  Bar chart comparing the distribution of sequence lengths between the random fuzzer and the PPO agent.

- **Test runner**  
  One‐click “Run pytest” button that executes the full generated test suite and displays pass/fail output.
