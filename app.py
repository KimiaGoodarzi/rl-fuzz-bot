
import streamlit as st
import pandas as pd
import subprocess
from rl_fuzz_bot.envs.remote_start_env import RemoteStartEnv

def highlight_error_row(row: pd.Series) -> list:

    return [
        "background-color: #ffcccc" if row["error_flag"] == 1 else ""
        for _ in row
    ]

st.title("RL Fuzz Bot Dashboard")
st.markdown(
    """
    - **action**  
      - `0` = START command  
      - `1` = CANCEL command  
      - `2` = STATUS_POLL  
      - `3` = HEARTBEAT  
    - **engine_state**  
      - `0` = OFF  
      - `1` = STARTING  
      - `2` = ON  
    - **error_flag**  
      - `0` = no fault  
      - `1` = fault occurred  
    """
)
st.markdown("### Failure discovery metrics")


rand_df = pd.read_json("my_failures.json")
ppo_df  = pd.read_json("ppo_failures.json")


col1, col2 = st.columns(2)
col1.metric("Random failures", len(rand_df), delta="(baseline)")
col2.metric("PPO failures",    len(ppo_df),  delta="(+ ML boost)")


st.subheader("Sample PPO failure sequences")
st.dataframe(ppo_df.head()[["seed", "episode", "sequence"]])


seq_idx = st.number_input(
    "Choose sequence index to replay",
    min_value=0, max_value=len(ppo_df)-1, value=0
)


st.markdown("**Raw failure record:**")
st.json(ppo_df.loc[seq_idx].to_dict())


if st.button("Run sequence"):
    base_seed = int(ppo_df.loc[seq_idx, "seed"])
    episode   = int(ppo_df.loc[seq_idx, "episode"])
    seq       = ppo_df.loc[seq_idx, "sequence"]

    env = RemoteStartEnv(seed=base_seed)
    obs, _ = env.reset(seed=base_seed + episode)

    rows = []
    for a in seq:
        obs, reward, done, trunc, _ = env.step(a)
        rows.append({
            "action":      a,
            "reward":      reward,
            "engine_state": int(obs["engine_state"][0]),
            "error_flag":   int(obs["error_flag"][0]),
        })
    replay_df = pd.DataFrame(rows)

    st.subheader(f"Replay of sequence #{seq_idx}")
    st.markdown("**Each row is one step of the replay: action → result**")
    styled = replay_df.style.apply(highlight_error_row, axis=1)
    st.dataframe(styled, use_container_width=True)


    if replay_df["error_flag"].iloc[-1] == 1 and replay_df["reward"].iloc[-1] > 0:
        st.success("✅ Replay ended in a fault")
    else:
        st.error(" Replay did *not* end in a fault!")

st.markdown("---")



st.subheader("Failure‐Sequence Lengths")


ppo_lengths = ppo_df["sequence"].apply(len)
pd_len = ppo_lengths.value_counts().sort_index().rename("ppo")


rand_lengths = rand_df["sequence"].apply(len)
pd_len = pd.concat((pd_len, rand_lengths.value_counts().sort_index().rename("random")), axis=1).fillna(0)

st.bar_chart(pd_len)



st.subheader("Run full test suite")
if st.button("Run pytest"):
    with st.spinner("Executing pytest…"):
        result = subprocess.run(
            ["pytest", "--disable-warnings", "-q"],
            capture_output=True,
            text=True,
        )
    if result.returncode == 0:
        st.success("✅ All tests passed!")
    else:
        st.error(f"❌ Some tests failed (exit code {result.returncode})")
    st.code(result.stdout, language="bash")
