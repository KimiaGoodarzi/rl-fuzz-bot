# ────────────────────────────────────────────────────────────────
# Project-wide automation for RL Fuzz Bot
# ────────────────────────────────────────────────────────────────

.PHONY: clean random train eval export test dashboard all

# 0) remove all generated artifacts
clean:
	rm -f my_failures.json ppo_failures.json
	rm -rf models tests/generated
	mkdir -p tests/generated && touch tests/generated/__init__.py

# 1) run the random fuzzer
random: clean
	python -m rl_fuzz_bot.tools.random_fuzzer \
	    --episodes 200 --seed 42 --output my_failures.json

# 2) train the PPO agent
train:
	python -m rl_fuzz_bot.tools.train_ppo \
	    --timesteps 10000 --seed 42

# 3) evaluate the trained PPO
eval:
	python -m rl_fuzz_bot.tools.eval_ppo \
	    --model models/ppo_remote_start.zip \
	    --episodes 1000 --seed 42 --output ppo_failures.json

# 4) export pytest cases from failures
export:
	python -m rl_fuzz_bot.tools.export_tests \
	    --input ppo_failures.json --output tests/generated

# 5) run the full test suite
test:
	python -m pytest -q

# 6) launch the dashboard
dashboard:
	streamlit run app.py

# A “meta” target to do everything except dashboard
all: random train eval export test


